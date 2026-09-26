"""Extra-month ratei of a period: the rateo of an extra run and settlements.

An extra-month run pays its accrued share of a monthly pay.  When the
employment ends before an extra month's payment month, the ratei accrued up
to the termination are paid on the last regular run as extra-month earnings
(``it/earning/extra_month`` policy: ordinary IRPEF, INPS and TFR base).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._calendar import standard_calendar
from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _apply_extra_month_policy,
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual, absence_days
from ccnl_engine.payroll.domain.calendar import ExtraMonthKind, ExtraMonthSchedule
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import ExtraMonthEarning, PayItem
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.payroll.application.allocate_events import _EventTotals
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment import EmploymentPeriod
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.service.types import MonthlyPayChain

__all__ = [
    "ExtraMonthSettlement",
    "non_accruing_days",
    "run_accrual",
    "run_fraction",
    "run_schedule",
    "settle_extra_months",
    "termination_settlements",
]

_EXTRA_KIND = "extra_month_earning"


def run_accrual(
    request: PeriodCalculationRequest, ccnl: CCNL, competence: date
) -> ExtraMonthAccrual | None:
    """Return the rateo an extra-month run pays.

    Args:
        request: The period request.  Its ``extra_month_accrual`` is used
            when given; otherwise an extra-month run counts its rateo from
            ``employment_period`` over the 12 months ending in the run month,
            with the CCNL fraction of that extra month.
        ccnl: The contract, whose standard calendar gives the fraction.
        competence: Date the CCNL entitlement is read at.

    Returns:
        The accrual of an extra-month run, ``None`` for any other run.
    """
    run = request.run
    if run is None or run.run_kind not in {k.value for k in ExtraMonthKind}:
        return None
    if request.extra_month_accrual is not None:
        return request.extra_month_accrual
    kind = ExtraMonthKind(run.run_kind.value)
    standard = standard_calendar(ccnl, run.year, competence)
    max_fraction = next(
        (s.max_fraction for s in standard.extra_months if s.kind is kind),
        Decimal(1),
    )
    schedule = run_schedule(kind, run.month, max_fraction)
    return ExtraMonthAccrual.of(schedule, run.year, request.employment_period)


def run_schedule(
    kind: ExtraMonthKind, payment_month: int, max_fraction: Decimal
) -> ExtraMonthSchedule:
    """Return the schedule of an extra month paid in ``payment_month``.

    Returns:
        The schedule whose accrual window is the 12 months ending in the
        payment month.
    """
    return ExtraMonthSchedule(
        kind=kind,
        name=kind.value,
        payment_month=payment_month,
        accrual_window_start_month=payment_month % 12 + 1,
        max_fraction=max_fraction,
    )


def run_fraction(accrual: ExtraMonthAccrual | None) -> Decimal:
    """Return the share of a monthly pay the run pays.

    Args:
        accrual: The rateo of an extra-month run from :func:`run_accrual`,
            ``None`` for any other run.

    Returns:
        ``1`` for a regular run, the accrued fraction for an extra run.
    """
    return Decimal(1) if accrual is None else accrual.fraction


@dataclass(frozen=True)
class ExtraMonthSettlement:
    """Earnings of the ratei liquidated on a run and the bases they enter.

    Attributes:
        items: One extra-month earning per settled extra month.
        entries: Cash-earning ledger entries of the items.
        inps_base: Amount entering the INPS contribution base.
        tfr_base: Amount entering the TFR base.
        irpef_base: Amount entering the ordinary IRPEF base.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    inps_base: Decimal = _ZERO
    tfr_base: Decimal = _ZERO
    irpef_base: Decimal = _ZERO

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return ``totals`` with the settled amounts added to its bases.

        Returns:
            A copy of ``totals`` with larger INPS, TFR and IRPEF bases.
        """
        return replace(
            totals,
            inps_base=totals.inps_base + self.inps_base,
            tfr_base=totals.tfr_base + self.tfr_base,
            irpef_base=totals.irpef_base + self.irpef_base,
        )


def settle_extra_months(
    settlements: tuple[ExtraMonthAccrual, ...],
    chain: MonthlyPayChain,
    competence_period: CompetencePeriod,
    payment_date: date,
    run_id: str,
    resolver: PolicyResolver,
    context: PolicyContext,
) -> ExtraMonthSettlement:
    """Pay the ratei of ``settlements`` on this run.

    Each extra month pays ``chain`` restricted to the allowances of that
    extra month, every component scaled by the accrued fraction and rounded
    to cents.  A settlement with no qualifying month pays nothing.

    Returns:
        The earnings, their ledger entries and the bases they enter.
    """
    due = [
        (accrual, _gross(chain, accrual))
        for accrual in settlements
        if accrual.months > 0
    ]
    if not due:
        return ExtraMonthSettlement()
    resolution = _require_resolution(resolver, _EXTRA_KIND, context)
    treatment = _treatment_from_resolution(resolution)
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    for accrual, gross in due:
        item_id = f"extra_month_{accrual.kind.value}_{run_id}"
        items.append(
            ExtraMonthEarning(
                item_id=item_id,
                competence_period=competence_period,
                payment_date=payment_date,
                quantity=accrual.fraction,
                amount=gross,
                month_number=14 if accrual.kind is ExtraMonthKind.FOURTEENTH else 13,
                source=f"ratei at termination: {accrual.months}/12",
            )
        )
        entries.append(
            _make_entry(
                item_id,
                item_id,
                _EXTRA_KIND,
                competence_period,
                payment_date,
                AccountKind.CASH_EARNINGS,
                gross,
                policy_id=resolution.policy_id,
            )
        )
    total = sum((gross for _, gross in due), _ZERO)
    return ExtraMonthSettlement(
        items=tuple(items),
        entries=tuple(entries),
        inps_base=total if treatment.inps else _ZERO,
        tfr_base=total if treatment.tfr else _ZERO,
        irpef_base=total if treatment.irpef else _ZERO,
    )


def _gross(chain: MonthlyPayChain, accrual: ExtraMonthAccrual) -> Decimal:
    """Return the gross of ``accrual`` on ``chain``.

    Returns:
        Sum of the scaled extra-month components.
    """
    scaled = _apply_extra_month_policy(chain, accrual.kind.value, accrual.fraction)
    return money(scaled.base + scaled.seniority + scaled.allowances_total)


def non_accruing_days(
    *event_maps: Mapping[int, tuple[WorkEvent, ...]]
    | Mapping[str, tuple[WorkEvent, ...]],
) -> frozenset[date]:
    """Return the days of the year's absences that suspend accrual.

    Returns:
        Every calendar day of an :class:`AbsenceEvent` with
        ``suspends_accrual`` set, across all the event maps.
    """
    days: set[date] = set()
    for events in (e for m in event_maps for e in m.values()):
        for event in events:
            if isinstance(event, AbsenceEvent) and event.suspends_accrual:
                last = event.end_date or event.event_date
                days |= absence_days(event.event_date, last)
    return frozenset(days)


def termination_settlements(
    calendar: WorkCalendar,
    employment_period: EmploymentPeriod | None,
    non_accruing_days: frozenset[date],
) -> dict[str, tuple[ExtraMonthAccrual, ...]]:
    """Return the ratei the last run of an employment ending this year pays.

    An extra month whose next payment after the termination month falls
    outside the employment is liquidated on the regular run of the
    termination month.  Its window is the one of that next payment (the
    following year when the payment month precedes the termination month),
    clipped to the hire date and counted up to the termination date.

    Returns:
        The accruals keyed by the ``run_id`` of the termination month's
        regular run, empty when the employment does not end in the year.
    """
    if employment_period is None or employment_period.ended_on is None:
        return {}
    ended_on = employment_period.ended_on
    if ended_on.year != calendar.year:
        return {}
    accruals = tuple(
        ExtraMonthAccrual.of(
            extra,
            calendar.year + (1 if extra.payment_month < ended_on.month else 0),
            employment_period,
            non_accruing_days=non_accruing_days,
        )
        for extra in calendar.extra_months
        if extra.payment_month != ended_on.month
    )
    return {PayrollRun.regular(calendar.year, ended_on.month).run_id: accruals}
