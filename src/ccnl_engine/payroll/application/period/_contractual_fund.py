"""Contractual contribution a CCNL owes a fund for every worker.

The amount is fixed per level and month (:class:`~ccnl_engine.contract.domain\
.fund_contribution.ContractualFundContribution`): a run that posts the monthly
pay of its month owes it, an extra-month run does not.  The sources quoted in
the bundle state no rule for a partly employed month or a part-time worker:
such a run pays the full amount and traverses :data:`PARTIAL_VARIANT`, which
the CCNL declares as an open limitation.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_lookup import Rule

__all__ = ["PARTIAL_VARIANT", "contractual_amount", "contractual_paths"]

_ZERO = Decimal(0)
#: Variant of the CCNL limitation a partial month or part time traverses.
PARTIAL_VARIANT = "contractual_fund_partial"
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_FEATURE = "pension_fund_contribution"


def _pays_month(ctx: RunContext) -> bool:
    return ctx.run_kind in _PAYING_KINDS and ctx.proration.posted_by is None


def contractual_amount(ctx: RunContext) -> Decimal:
    """Return the contractual contribution the run owes.

    Returns:
        The monthly amount of the level, zero without one or on a run that
        does not post the monthly pay.
    """
    contract = ctx.contract
    spec = contract.ccnl.parameters.contractual_fund_contribution
    if spec is None or not _pays_month(ctx):
        return _ZERO
    series = spec.monthly_by_level[contract.level.code]
    with rule_scope(ruleset=contract.ccnl.meta.ccnl_id, feature=_FEATURE):
        return series.value_at(contract.tctx.competence)


def contractual_rules(ctx: RunContext, prefix: str) -> tuple[Rule, ...]:
    """Return the clause of the contractual contribution the run read.

    Returns:
        The amount of the level in force, empty when the run owes none.
    """
    contract = ctx.contract
    spec = contract.ccnl.parameters.contractual_fund_contribution
    if spec is None or not _pays_month(ctx):
        return ()
    series = spec.monthly_by_level[contract.level.code]
    rule = f"{prefix}:contractual_fund_contribution[{contract.level.code}]"
    periods = (series.period_at(contract.tctx.competence),)
    return tuple(
        (f"{rule}[{p.valid_from}]", p.provenance or spec.provenance)
        for p in periods
        if p is not None
    )


def contractual_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation path of a contribution owed on part of a month.

    Returns:
        The :data:`PARTIAL_VARIANT` path of the CCNL when the run owes the
        contribution on a partly employed month or a part-time worker.
    """
    request = ctx.request
    hours, full = request.weekly_hours, request.full_time_weekly_hours
    part_time = hours is not None and (full is None or hours.value < full.value)
    if contractual_amount(ctx) == _ZERO or not (ctx.proration.partial or part_time):
        return frozenset()
    return frozenset({f"{ctx.contract.ccnl.meta.ccnl_id}/{PARTIAL_VARIANT}"})
