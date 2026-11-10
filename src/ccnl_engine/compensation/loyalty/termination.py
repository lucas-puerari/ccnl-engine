"""Whole-month loyalty twelfths at the close of an employment."""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.loyalty.rules import LoyaltySettlement, _award_amount
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import LoyaltyPremiumEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)

if TYPE_CHECKING:
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
                    "Art. 65 loyalty dismissal twelfths need "
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
    if (ctx.request.period_id.year, ctx.request.period_id.month) != (
        ended.year,
        ended.month,
    ):
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
    rule, version = _ccnl_rule(ctx.contract.ccnl, ended.year)
    location = clause.provenance.location
    resolution = _require_resolution(
        ctx.resolver, "loyalty_premium_earning", ctx.policy_context
    )
    treatment = _treatment_from_resolution(resolution)
    item_id = f"loyalty_premium_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = LoyaltyPremiumEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(months) / Decimal(12),
        amount=amount,
        source=f"Premio di fedeltà: {getattr(location, 'section', '')}",
    )
    entry = _make_entry(
        item_id,
        item_id,
        "loyalty_premium_earning",
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
                capability="base_salary",
                status=CalculationStatus.FINAL,
                reason_code="loyalty_dismissal_twelfths",
                rule=f"{rule}:parameters.loyalty_premium",
                rule_version=version,
                source=location,
                inputs={"whole_months": str(months), "annual_award": full},
                amount=amount,
            ),
        ),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
    )
