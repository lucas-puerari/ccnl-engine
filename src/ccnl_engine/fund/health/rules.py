"""Which workers a health fund covers, by contract, length, hours and choice."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.fund.contractual.policies import ends_within

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.fund.health.models import ContractualFund
    from ccnl_engine.fund.health.services import FundOutcome
    from ccnl_engine.period.context.services import RunContext

__all__ = ["excluded", "with_opt_ins"]

_FACT = "fund_opt_ins"
_Funds = tuple["ContractualFund", ...]


def excluded(fund: ContractualFund, ctx: RunContext) -> bool:
    """Return whether the fund leaves the worker of the run out.

    A permanent-only fund leaves out the other contracts; a fixed term
    whose stated end comes before ``minimum_fixed_term_months``, a
    part-timer below ``minimum_weekly_hours`` and, for a fund that
    ``excludes_probation``, a month starting within the probation are left
    out too, the months counted within the calendar year of the run for a
    fund with ``fixed_term_months_in_year``.  A fixed term without a stated
    end is covered.

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
    if (
        months is None
        or not isinstance(request.contract_type, FixedTerm)
        or period is None
        or period.ended_on is None
    ):
        return False
    start, end = period.started_on, period.ended_on
    if fund.fixed_term_months_in_year:
        year = ctx.contract.tctx.competence.year
        start, end = max(start, date(year, 1, 1)), min(end, date(year, 12, 31))
    return ends_within(start, end, months)


def _opted_in(fund: ContractualFund, ctx: RunContext) -> bool | None:
    """Whether the worker stays in ``fund``, by the choice it asks from a day.

    Returns:
        ``True`` when the fund asks no choice on the run or the worker pays
        its worker share, ``False`` when not, ``None`` when not stated.
    """
    start = fund.opt_in_from
    if start is None or ctx.contract.tctx.competence < start:
        return True
    chosen = ctx.request.fund_opt_ins
    return None if chosen is None else fund.code in chosen


def with_opt_ins(
    ctx: RunContext,
    funds: _Funds,
    paid: frozenset[str],
    post: Callable[
        [RunContext, tuple[ContractualFund, ...], frozenset[str]], FundOutcome
    ],
) -> FundOutcome:
    """Post the funds the employer pays, less those the worker left.

    Alimentari art. 74 quater: "Laddove il lavoratore non manifesti la
    volontà di partecipare con la propria quota al Fondo, lo stesso decade
    dall'iscrizione e cessa automaticamente la contribuzione da parte
    dell'impresa."  A worker who left a fund the employer pays has neither
    its shares nor its element; an unstated choice posts nothing for the
    fund, with a missing-fact issue.

    Returns:
        The outcome of ``post`` on the funds the worker stays in.
    """
    choice = {f.code: _opted_in(f, ctx) for f in funds if f.code in paid}
    kept = tuple(f for f in funds if choice.get(f.code, True))
    outcome = post(ctx, kept, paid)
    unknown = sorted(code for code, chosen in choice.items() if chosen is None)
    if not unknown:
        return outcome
    issue = CalculationIssue(
        code="fund_opt_ins_unknown",
        message=(
            f"the worker of the funds {', '.join(unknown)} chooses whether to "
            "pay their worker share, and without it leaves them: nothing is "
            "posted for them; state Employment.fund_opt_ins"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=_FACT,
        capability="contractual_funds",
    )
    return replace(outcome, issues=(*outcome.issues, issue))
