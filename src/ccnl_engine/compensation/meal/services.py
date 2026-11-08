"""Electronic contractual meal vouchers on verified eligible days."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.run.types import RunKind
from ccnl_engine.variable_pay.inputs import WelfareEvent

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def meal_benefit(ctx: RunContext) -> tuple[WelfareEvent, ...]:
    """Value the caller's eligible days using the contract's dated daily rate.

    The caller verifies electronic delivery, canteen availability, lunch
    break or split shift, and excludes sick leave, injury, holiday, permits,
    rest, absence, maternity and disciplinary suspension. The electronic
    vouchers must satisfy the applicable tax exemption limit; paper vouchers
    are outside this input. A day count is not inferred from hours.
    Only regular and termination runs may carry eligible days.

    Returns:
        A non-remunerative benefit event, or no event when none is due.

    Raises:
        InvalidInputError: If positive days are declared for an ineligible
            employer, an extra-month run or a contract without a daily rate.
    """
    days = ctx.request.meal_benefit_days
    if not days:
        return ()
    if ctx.request.employer.headcount.value <= 10:
        msg = "meal benefit requires an employer with more than 10 employees"
        raise InvalidInputError(msg, feature="meal_benefit")
    run = ctx.request.run
    if run is not None and run.run_kind not in {RunKind.REGULAR, RunKind.TERMINATION}:
        msg = "meal benefit days belong to a regular or termination run"
        raise InvalidInputError(msg, feature="meal_benefit")
    series = ctx.contract.ccnl.parameters.meal_benefit_daily
    competence = ctx.contract.tctx.competence
    rate = None if series is None else series.value_at(competence)
    if rate is None:
        msg = "no contractual daily meal benefit rate for this period"
        raise InvalidInputError(msg, feature="meal_benefit")
    return (WelfareEvent(date(competence.year, competence.month, 1), rate * days),)


def meal_benefit_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Trace the contract rate and verified day count of a meal posting.

    Returns:
        One contract-derived welfare decision for a posted meal benefit.
    """
    benefits = meal_benefit(ctx)
    if not benefits:
        return ()
    competence = ctx.contract.tctx.competence
    series = ctx.contract.ccnl.parameters.meal_benefit_daily
    assert series is not None
    period = series.period_at(competence)
    assert period is not None
    assert period.provenance is not None
    rule, version = _ccnl_rule(ctx.contract.ccnl, competence.year)
    return (
        CalculationDecision(
            capability="welfare",
            status=CalculationStatus.FINAL,
            reason_code="contractual_meal_benefit",
            rule=f"{rule}:parameters.meal_benefit_daily",
            rule_version=version,
            source=period.provenance.location,
            inputs={
                "eligible_days": str(ctx.request.meal_benefit_days),
                "daily_rate": str(period.value),
            },
            amount=benefits[0].amount,
        ),
    )
