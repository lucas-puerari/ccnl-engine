"""Whole-month loyalty twelfths at the close of an employment."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.loyalty.rules import (
    LoyaltySettlement,
    _award_amount,
    _hourly_pay,
)
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import BonusEarning, LoyaltyPremiumEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import PayrollRun, RunKind

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.compensation.loyalty.models import LoyaltyPremium
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.period.context.services import RunContext


def _anniversary(hire: date, year: int) -> date:
    """Clamp a leap-day hire to the last day of February in other years.

    Returns:
        The anniversary in ``year``.
    """
    return hire.replace(
        year=year, day=min(hire.day, calendar.monthrange(year, hire.month)[1])
    )


def _months_since(anniversary: date, ended: date) -> int:
    """Count completed months since the preceding award, not partial months.

    Returns:
        The number of whole months from the anniversary through the last day.
    """
    months = (ended.year - anniversary.year) * 12 + ended.month - anniversary.month
    boundary = anniversary.day
    boundary = min(boundary, calendar.monthrange(ended.year, ended.month)[1])
    return months - (ended.day < boundary)


def _closes(ctx: RunContext, day: date) -> bool:
    """Whether the run closes an employment that ends on ``day``.

    As for the ratei of the extra months (``run_settlements``): the regular
    run of the month, or the termination run of the month when its regular
    run is not closed.

    Returns:
        ``True`` for that run.
    """
    month = ctx.request.period_id
    if (month.year, month.month) != (day.year, day.month):
        return False
    if ctx.run_kind is RunKind.REGULAR:
        return True
    regular = PayrollRun.regular(day.year, day.month).identifier
    return regular not in ctx.request.opening_state.accrual.competence_runs


def _missing(fact: str) -> LoyaltySettlement:
    """Flag a missing closing-run fact without guessing an award.

    Returns:
        An incomplete settlement naming the missing fact.
    """
    return LoyaltySettlement(
        issues=(
            CalculationIssue(
                code=f"loyalty_{fact}_unknown",
                message=(
                    "the loyalty award at the end of the employment needs "
                    f"EmploymentPeriod.{fact}, which is not stated"
                ),
                capability="base_salary",
                status=CalculationStatus.INCOMPLETE,
                fact=fact,
                cause=IssueCause.FACT,
            ),
        )
    )


def dismissal_award(  # noqa: PLR0911
    ctx: RunContext, clause: LoyaltyPremium, period: EmploymentPeriod
) -> LoyaltySettlement:
    """Pay full-month twelfths after a vested anniversary on dismissal only.

    Returns:
        The proportional award, an incomplete missing-fact issue, or nothing.
    """
    if not clause.dismissal_pro_rata or period.ended_on is None:
        return LoyaltySettlement()
    ended = period.ended_on
    if not _closes(ctx, ended):
        return LoyaltySettlement()
    previous = _anniversary(period.started_on, ended.year)
    if previous > ended:
        previous = _anniversary(period.started_on, ended.year - 1)
    service_start = period.uninterrupted_service_started_on or period.started_on
    qualified = _anniversary(service_start, service_start.year + clause.service_years)
    months = _months_since(previous, ended)
    if previous < qualified or months <= 0:
        return LoyaltySettlement()
    if period.ended_by is None:
        return _missing("ended_by")
    if period.ended_by is not TerminationCause.DISMISSAL:
        return LoyaltySettlement()
    if period.disciplinary_dismissal is None:
        return _missing("disciplinary_dismissal")
    if period.disciplinary_dismissal:
        return LoyaltySettlement()
    full = _award_amount(ctx, clause, ended)
    if full is None:
        return LoyaltySettlement()
    amount = money(full * Decimal(months) / Decimal(12))
    return _posted(
        ctx,
        clause,
        (amount, Decimal(months) / Decimal(12)),
        ended,
        (
            "loyalty_dismissal_twelfths",
            {"whole_months": str(months), "annual_award": full},
        ),
    )


def _whole_years(start: date, ended: date) -> int:
    """Count the whole years of service from ``start`` through ``ended``.

    Returns:
        The years completed by the end of the last day of service.
    """
    after = ended + timedelta(days=1)
    return (
        after.year - start.year - ((after.month, after.day) < (start.month, start.day))
    )


def _early_cause(period: EmploymentPeriod) -> bool | LoyaltySettlement:
    """Whether the employment ends by death or permanent incapacity.

    Returns:
        ``True`` or ``False``, or an incomplete settlement naming the fact
        that is not stated.
    """
    if period.ended_by is None:
        return _missing("ended_by")
    if period.ended_by is TerminationCause.DEATH:
        return True
    if period.permanent_incapacity is None:
        return _missing("permanent_incapacity")
    return period.permanent_incapacity


def early_award(
    ctx: RunContext, clause: LoyaltyPremium, period: EmploymentPeriod
) -> LoyaltySettlement:
    """Settle the ratei of a once-only award the employment ends before.

    Alimentari saccarifero, punto 25: "In caso di risoluzione anticipata del
    rapporto di lavoro per causa di morte o di invalidità permanente, saranno
    liquidati ... i ratei corrispondenti agli anni interi maturati in
    funzione di 8 ore annue per gli operai e 7 ore per gli impiegati."

    Returns:
        The ratei on the run of the month the employment ends, an incomplete
        settlement naming a missing fact, or nothing.
    """
    category = ctx.worker_category
    hours = None if category is None else clause.early_hours.get(category)
    ended = period.ended_on
    if hours is None or ended is None or not _closes(ctx, ended):
        return LoyaltySettlement()
    start = period.uninterrupted_service_started_on or period.started_on
    years = _whole_years(start, ended)
    if not 0 < years < clause.service_years:
        return LoyaltySettlement()
    cause = _early_cause(period)
    if cause is not True:
        return cause or LoyaltySettlement()
    hourly = _hourly_pay(ctx, clause, ended)
    if hourly is None:
        return LoyaltySettlement()
    amount = money(years * hours * hourly)
    return _posted(
        ctx,
        clause,
        (amount, Decimal(years)),
        ended,
        ("loyalty_early_ratei", {"whole_years": str(years), "hours": str(hours)}),
    )


def closing_award(
    ctx: RunContext, clause: LoyaltyPremium, period: EmploymentPeriod
) -> LoyaltySettlement:
    """Pay what the loyalty clause owes at the end of the employment.

    Returns:
        The early ratei of a clause that settles them, else the dismissal
        twelfths.
    """
    if clause.early_hours:
        return early_award(ctx, clause, period)
    return dismissal_award(ctx, clause, period)


def _posted(
    ctx: RunContext,
    clause: LoyaltyPremium,
    paid: tuple[Decimal, Decimal],
    ended: date,
    reason: tuple[str, Mapping[str, Decimal | str]],
) -> LoyaltySettlement:
    """Post ``paid`` (amount and quantity) as the award of the clause.

    Returns:
        The earning, its ledger entry and its decision.
    """
    amount, quantity = paid
    reason_code, inputs = reason
    once = clause.recurrence == "once"
    kind = "bonus_earning" if once else "loyalty_premium_earning"
    rule, version = _ccnl_rule(ctx.contract.ccnl, ended.year)
    location = clause.provenance.location
    resolution = _require_resolution(ctx.resolver, kind, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"loyalty_premium_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = (BonusEarning if once else LoyaltyPremiumEarning)(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=quantity,
        amount=amount,
        source=f"Premio di fedeltà: {getattr(location, 'section', '')}",
    )
    entry = _make_entry(
        item_id,
        item_id,
        kind,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    return LoyaltySettlement(
        items=(item,),
        entries=(entry,),
        decisions=(
            CalculationDecision(
                capability="bonus" if once else "base_salary",
                status=CalculationStatus.FINAL,
                reason_code=reason_code,
                rule=f"{rule}:parameters.loyalty_premium",
                rule_version=version,
                source=location,
                inputs=inputs,
                amount=amount,
            ),
        ),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
    )
