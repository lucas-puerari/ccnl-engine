"""Amounts of a sickness episode in a run: deduction, indemnity, top-up.

The payable units of each class of sick days are counted with the CCNL
daily quota.  The sick days of a month, earlier episodes of the run
included, never count more than one monthly pay, and their pay is rounded
once on the units counted so far, so the deductions of the month add up to
at most its pay.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.period.services_shared import _ZERO
from ccnl_engine.payroll.sickness.results_cumulation import (
    CumulationReport,
    cumulation_report,
)
from ccnl_engine.payroll.sickness.rules_day import (
    SickDayKind,
    SickDaySegment,
    classify_days,
    segment_units,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.amount.types_chain import MonthlyPayChain
    from ccnl_engine.payroll.sickness.models import SicknessEpisode
    from ccnl_engine.payroll.sickness.models_pay_rule import SickPayRules
    from ccnl_engine.payroll.sickness.rules_terms import (
        SicknessTerms,
    )

__all__ = ["EpisodePay", "episode_pay"]


@dataclass(frozen=True)
class EpisodePay:
    """Amounts of one episode in the run.

    Attributes:
        segments: The classified sick days of the run.
        units: Payable units of each segment.
        absence: Daily pay of the sick days, deducted.
        inps: INPS indemnity.
        integration: Employer integration on indemnified days.
        carenza: Employer pay of the waiting period.
        report: What a CCNL treatment counted over several episodes rests
            on; ``None`` for a per-episode CCNL.
    """

    segments: tuple[SickDaySegment, ...]
    units: tuple[Decimal, ...]
    absence: Decimal = _ZERO
    inps: Decimal = _ZERO
    integration: Decimal = _ZERO
    carenza: Decimal = _ZERO
    report: CumulationReport | None = None

    @property
    def paid(self) -> Decimal:
        """Everything paid back to the worker for the sick days."""
        return self.inps + self.integration + self.carenza

    @property
    def sick_days(self) -> frozenset[date]:
        """Days of the segments within the comporto."""
        return frozenset(
            s.first + timedelta(days=step)
            for s in self.segments
            if s.kind is not SickDayKind.BEYOND_COMPORTO
            for step in range((s.last - s.first).days + 1)
        )

    def units_of(self, kind: SickDayKind) -> Decimal:
        """Return the payable units of the segments of ``kind``.

        Returns:
            Their sum, zero without such a segment.
        """
        pairs = zip(self.segments, self.units, strict=True)
        return sum((u for s, u in pairs if s.kind is kind), _ZERO)


def _quota(chain: MonthlyPayChain, units: Decimal, divisor: Decimal) -> Decimal:
    """Return the pay of ``units`` of the ``divisor`` units of ``chain``.

    Returns:
        The prorated base, seniority and allowances, each rounded once.
    """
    part = chain.prorated(units, divisor)
    return part.base + part.seniority + part.allowances_total


def _within_month(
    segments: tuple[SickDaySegment, ...],
    units: tuple[Decimal, ...],
    counted: Decimal,
    divisor: Decimal,
) -> tuple[Decimal, ...]:
    """Clip the deducted units so the month never counts more than ``divisor``.

    Episodes of the same month are counted from their own first day, so
    their units can add up to more than a monthly pay (27 working days of a
    ``by_26`` month).  The units past what is left of the month after the
    ``counted`` units of earlier episodes are dropped; the days past the
    comporto, not deducted, keep theirs.

    Returns:
        One unit count per segment, in segment order.
    """
    left = divisor - counted
    clipped: list[Decimal] = []
    for segment, unit in zip(segments, units, strict=True):
        if segment.kind is SickDayKind.BEYOND_COMPORTO:
            clipped.append(unit)
            continue
        kept = min(unit, left)
        left -= kept
        clipped.append(kept)
    return tuple(clipped)


def _grossed(share: Decimal, rules: SickPayRules, terms: SicknessTerms) -> Decimal:
    """Return the INPS share as gross pay, for a CCNL of the net daily pay.

    The INPS indemnity bears no contributions, the company integration
    does: on the net basis the share is divided by one less the worker's
    INPS rate before the integration is taken from the target.

    Returns:
        ``share`` on the gross basis, grossed up on the net one.
    """
    if not rules.ccnl.net_basis:
        return share
    return money(share / (1 - terms.employee_rate))


def episode_pay(
    episode: SicknessEpisode, span: tuple[date, date], terms: SicknessTerms
) -> EpisodePay | None:
    """Return the amounts of ``episode`` over ``span``.

    The deduction of each segment is the pay of the units of the month
    counted up to its end, earlier episodes of the run included, less the
    pay of those counted before it: the month is rounded once, so the sick
    days of a month never deduct more than its pay.

    Returns:
        The amounts, ``None`` when the CCNL lacks the sickness rule or the
        daily quota.
    """
    rules, quota, chain = terms.rules, terms.quota, terms.chain
    if rules is None or quota is None or chain is None:
        return None
    segments = classify_days(episode, span, terms.history, rules)
    units = _within_month(
        segments,
        segment_units(segments, quota.method, quota.divisor, quota.daily_hours),
        terms.counted,
        quota.divisor,
    )
    absence = inps = integration = carenza = _ZERO
    excluded = rules.ccnl.apprentices_excluded and terms.apprentice
    counted = terms.counted
    before = _quota(chain, counted, quota.divisor)
    for segment, unit in zip(segments, units, strict=True):
        if segment.kind is SickDayKind.BEYOND_COMPORTO or unit == _ZERO:
            continue
        counted += unit
        reached = _quota(chain, counted, quota.divisor)
        base, before = reached - before, reached
        absence += base
        share = money(base * segment.inps_rate)
        if segment.kind is not SickDayKind.CARENZA:
            inps += share
        if excluded:
            continue
        worker = money(base * segment.worker_rate)
        if segment.kind is SickDayKind.CARENZA:
            carenza += worker
            continue
        integration += max(_ZERO, worker - _grossed(share, rules, terms))
    cumulative = rules.cumulative(episode, terms.history)
    report = None if cumulative is None else cumulation_report(cumulative, span)
    return EpisodePay(segments, units, absence, inps, integration, carenza, report)
