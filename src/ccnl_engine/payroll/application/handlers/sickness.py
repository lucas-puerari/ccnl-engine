"""Handler of a sickness episode: deduction, INPS indemnity and CCNL top-up.

The run that posts the monthly pay of a month pays the sick days of the
episode in that month and in the employment.  Each day is classified by
:func:`~ccnl_engine.payroll.domain.sick_days.classify_days`; the payable
days of each class are counted with the CCNL daily quota of an unpaid
absence, so a hire, a termination, an absence and a sick day count the same
days.  For each class the run deducts the daily pay and pays back:

- the INPS indemnity (``sickness_inps_item``), outside the contribution
  base;
- the employer integration up to the CCNL target, and the waiting-period
  pay, as ``sickness_item``.

Every episode records one ``sickness`` decision.  A missing CCNL rule posts
nothing and raises an incomplete issue; a worker the bundle cannot place
inside or outside INPS cover is paid as uncovered with a provisional issue.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
    _treatment_deltas,
)
from ccnl_engine.payroll.application.handlers._sickness_issues import (
    CUMULATION_LIMITATION,
    INPS_DAILY_BASE_LIMITATION,
    episode_decision,
    episode_issues,
    episode_limitations,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    PayItem,
    SicknessInpsItem,
    SicknessItem,
)
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.sick_days import (
    SickDayKind,
    SickDaySegment,
    classify_days,
    segment_units,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.application.handlers._sickness_terms import (
        SicknessTerms,
    )
    from ccnl_engine.payroll.domain.sickness import SicknessEpisode

__all__ = [
    "CUMULATION_LIMITATION",
    "INPS_DAILY_BASE_LIMITATION",
    "EpisodePay",
    "_handle_sickness_episode",
    "episode_pay",
]


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
    """

    segments: tuple[SickDaySegment, ...]
    units: tuple[Decimal, ...]
    absence: Decimal = _ZERO
    inps: Decimal = _ZERO
    integration: Decimal = _ZERO
    carenza: Decimal = _ZERO

    @property
    def paid(self) -> Decimal:
        """Everything paid back to the worker for the sick days."""
        return self.inps + self.integration + self.carenza

    def units_of(self, kind: SickDayKind) -> Decimal:
        """Return the payable units of the segments of ``kind``.

        Returns:
            Their sum, zero without such a segment.
        """
        pairs = zip(self.segments, self.units, strict=True)
        return sum((u for s, u in pairs if s.kind is kind), _ZERO)


def episode_pay(
    episode: SicknessEpisode, span: tuple[date, date], terms: SicknessTerms
) -> EpisodePay | None:
    """Return the amounts of ``episode`` over ``span``.

    Returns:
        The amounts, ``None`` when the CCNL lacks the sickness rule or the
        daily quota.
    """
    rules, quota, chain = terms.rules, terms.quota, terms.chain
    if rules is None or quota is None or chain is None:
        return None
    segments = classify_days(episode, span, terms.history, rules)
    units = segment_units(segments, quota.method, quota.divisor, quota.daily_hours)
    absence = inps = integration = carenza = _ZERO
    for segment, unit in zip(segments, units, strict=True):
        if segment.kind is SickDayKind.BEYOND_COMPORTO or unit == _ZERO:
            continue
        part = chain.prorated(unit, quota.divisor)
        base = part.base + part.seniority + part.allowances_total
        absence += base
        worker = money(base * segment.worker_rate)
        if segment.kind is SickDayKind.CARENZA:
            carenza += worker
            continue
        share = money(base * segment.inps_rate)
        inps += share
        integration += worker - share
    return EpisodePay(segments, units, absence, inps, integration, carenza)


def _item(
    item_id: str, amount: Decimal, units: Decimal, inps: bool, ctx: _EventHandlerCtx
) -> tuple[PayItem, AccountKind, str]:
    """Return the pay item of one episode amount, its account and kind.

    Returns:
        An absence deduction for a negative amount, an INPS indemnity item
        when ``inps``, a sickness item otherwise.
    """
    cp, day = ctx.cp, ctx.payment_date
    if amount < _ZERO:
        deduction = AbsenceDeduction(
            item_id=item_id,
            competence_period=cp,
            payment_date=day,
            quantity=units,
            amount=-amount,
            absence_days=units,
        )
        return deduction, AccountKind.EMPLOYEE_DEDUCTIONS, "absence_deduction"
    if inps:
        indemnity = SicknessInpsItem(
            item_id=item_id,
            competence_period=cp,
            payment_date=day,
            quantity=Decimal(1),
            amount=amount,
            sick_days=units,
        )
        return indemnity, AccountKind.CASH_EARNINGS, "sickness_inps_item"
    paid = SicknessItem(
        item_id=item_id,
        competence_period=cp,
        payment_date=day,
        quantity=Decimal(1),
        amount=amount,
        sick_days=units,
    )
    return paid, AccountKind.CASH_EARNINGS, "sickness_item"


def _postings(
    pay: EpisodePay, ctx: _EventHandlerCtx
) -> tuple[list[PayItem], list[PostingIntent], tuple[Decimal, Decimal, Decimal]]:
    """Return the items, intents and base deltas of the episode amounts.

    Returns:
        ``(items, intents, (inps, tfr, irpef))``.
    """
    evt = ctx.evt_id
    sickness = _require_resolution(ctx.resolver, "sickness_item", ctx.context)
    indemnity = _require_resolution(ctx.resolver, "sickness_inps_item", ctx.context)
    indemnified = pay.units_of(SickDayKind.INDEMNIFIED)
    carenza = pay.units_of(SickDayKind.CARENZA)
    lines = (
        (f"{evt}_abs", -pay.absence, sickness, indemnified + carenza),
        (f"{evt}_inps", pay.inps, indemnity, indemnified),
        (f"{evt}_intg", pay.integration, sickness, indemnified),
        (f"{evt}_crnz", pay.carenza, sickness, carenza),
    )
    items: list[PayItem] = []
    intents: list[PostingIntent] = []
    deltas = [_ZERO, _ZERO, _ZERO]
    for item_id, amount, resolution, units in lines:
        if amount == _ZERO:
            continue
        item, account, kind = _item(
            item_id, amount, units, resolution is indemnity, ctx
        )
        items.append(item)
        prefix = "deduction" if amount < _ZERO else "cash"
        intents.append(
            PostingIntent(
                entry_id=f"{prefix}_{item_id}",
                source_item_id=item_id,
                pay_item_kind=kind,
                account=account,
                amount=abs(amount),
                policy_decision_id=resolution.policy_id,
            )
        )
        treatment = _treatment_from_resolution(resolution)
        for axis, delta in enumerate(_treatment_deltas(treatment, amount)):
            deltas[axis] += delta
    return items, intents, (deltas[0], deltas[1], deltas[2])


def _span(episode: SicknessEpisode, terms: SicknessTerms) -> tuple[date, date]:
    """Return the sick days of ``episode`` the run pays.

    Returns:
        The days of the episode within the employed days of the month.

    Raises:
        InvalidInputError: When the run posts no monthly pay, or the
            episode does not touch the employed days of its month.
    """
    employed = terms.employed
    span = None if employed is None else episode.within(*employed)
    if span is None:
        msg = (
            f"sickness episode '{episode.episode_id}' must be passed to the run "
            "that posts the monthly pay of a month it touches, within the "
            "employment"
        )
        raise InvalidInputError(msg, field="SicknessEpisode", feature="sickness")
    return span


def _handle_sickness_episode(
    event: SicknessEpisode, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the sick days of ``event`` in the month of the run.

    Returns:
        The items, entries, base deltas, decision and issues of the episode,
        and the episode cut at its last day in the month, to record.
    """
    terms = ctx.sickness
    span = _span(event, terms)
    pay = episode_pay(event, span, terms)
    issues = episode_issues(event, pay, terms)
    effect = EventEffect(
        decisions=[episode_decision(event, span, pay, terms, issues)],
        issues=list(issues),
        sickness_episode=event.through(span[1]),
        limitations=episode_limitations(event, pay, terms),
    )
    if pay is None:
        return effect
    effect.items, effect.intents, deltas = _postings(pay, ctx)
    effect.inps_delta, effect.tfr_delta, effect.irpef_delta = deltas
    return effect
