"""Which workers a health fund covers, by contract, length and hours."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.fund.contractual.policies import ends_within

if TYPE_CHECKING:
    from ccnl_engine.fund.health.models import ContractualFund
    from ccnl_engine.period.context.services import RunContext

__all__ = ["excluded"]


def excluded(fund: ContractualFund, ctx: RunContext) -> bool:
    """Return whether the fund leaves the worker of the run out.

    A permanent-only fund leaves out the other contracts; a fixed term
    whose stated end comes before ``minimum_fixed_term_months``, a
    part-timer below ``minimum_weekly_hours`` and, for a fund that
    ``excludes_probation``, a month starting within the probation are left
    out too.  A fixed
    term without a stated end is covered.

    Returns:
        True when the worker is not covered.
    """
    request = ctx.request
    if fund.excludes_contract(request.contract_type):
        return True
    hours, minimum = request.weekly_hours, fund.minimum_weekly_hours
    if minimum is not None and hours is not None and Decimal(hours.value) < minimum:
        return True
    period, months = request.employment_period, fund.minimum_fixed_term_months
    if (
        fund.excludes_probation
        and period is not None
        and period.probation_until is not None
        and ctx.contract.tctx.competence <= period.probation_until
    ):
        return True
    return (
        months is not None
        and isinstance(request.contract_type, FixedTerm)
        and period is not None
        and period.ended_on is not None
        and ends_within(period.started_on, period.ended_on, months)
    )
