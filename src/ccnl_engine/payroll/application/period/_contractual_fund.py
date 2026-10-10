"""Contractual contribution a CCNL owes a fund for every worker.

The amount is fixed per level and month (:class:`~ccnl_engine.contract.fund.models\
.ContractualFundContribution`): a run that posts the monthly
pay of its month owes it, an extra-month run only when the clause says so, in
proportion to its ratei.  The clause may set the categories it covers, a
minimum of days worked in the month, a proportion for part time and a minimum
length of a fixed term (CNCE vademecum on the Prevedi contribution).  A level
or a category the clause gives no amount for owes an amount the engine does
not compute: the run has an incomplete issue.  A partial month or part time
the clause gives no rule for pays the full amount and traverses
:data:`PARTIAL_VARIANT`, an open limitation the CCNL declares.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.rules_validity import rule_scope
from ccnl_engine.payroll.application.period._contractual_eligibility import (
    contributing,
    not_permanent,
    short_fixed_term,
    worked_days,
)
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.contract.fund.models import (
        ContractualFundContribution,
    )
    from ccnl_engine.contract.identity.rules_validity import TimeSeries
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_lookup import Rule

__all__ = [
    "PARTIAL_VARIANT",
    "ContractualRun",
    "contractual_paths",
    "contractual_rules",
    "contractual_run",
]

_ZERO = Decimal(0)
_TWELVE = Decimal(12)
_EURO = Decimal(1)
_DAY = timedelta(days=1)
#: Variant of the CCNL limitation a partial month or part time traverses.
PARTIAL_VARIANT = "contractual_fund_partial"
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_EXTRA_KINDS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})
_FEATURE = "pension_fund_contribution"
_CATEGORY_UNKNOWN = CalculationIssue(
    code="contractual_fund_category_unknown",
    message=(
        "the contractual fund contribution of the CCNL depends on the worker "
        "category, which the level leaves open: the amounts shown leave it "
        "out; state Employment.category"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="category",
)
_HOURS_UNKNOWN = CalculationIssue(
    code="contractual_fund_hours_unknown",
    message=(
        "the contractual fund contribution of an operaio is an amount per "
        "ordinary hour worked, which the run does not state: the amounts "
        "shown leave it out; state PeriodFacts.ordinary_hours_worked"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="ordinary_hours_worked",
)
_UNCOVERED = CalculationIssue(
    code="contractual_fund_not_computed",
    message=(
        "the CCNL owes its fund a contractual contribution for this worker "
        "that the engine does not compute (e.g. the Prevedi amount per hour "
        "worked of an operaio): the amounts shown leave it out"
    ),
    status=CalculationStatus.INCOMPLETE,
)


@dataclass(frozen=True)
class ContractualRun:
    """Contractual contribution of one run.

    Attributes:
        amount: Amount the run owes.
        series: Amount series of the clause the run read, if any.
        key: Key of ``series`` in the clause (``5``, ``apprentice``,
            ``hourly[2]``...).
        paths: Limitation paths the run traversed.
        issue: Missing fact that leaves the amount out, if any.
        not_enrolled: Series of the amount added for a worker not enrolled
            voluntarily, when the run read it.
    """

    amount: Decimal = _ZERO
    series: TimeSeries | None = None
    paths: frozenset[str] = frozenset()
    key: str = ""
    issue: CalculationIssue | None = None
    not_enrolled: TimeSeries | None = None


_NONE = ContractualRun()


def contractual_run(ctx: RunContext) -> ContractualRun:
    """Return the contractual contribution the run owes, and why.

    Returns:
        The amount, the clause read, the limitation paths and the issue.
    """
    spec = ctx.contract.ccnl.parameters.contractual_fund_contribution
    extra = ctx.run_kind in _EXTRA_KINDS
    if spec is None or not (_pays_month(ctx) or (extra and spec.extra_months)):
        return _NONE
    category = ctx.worker_category
    if spec.categories is not None and category is None:
        return ContractualRun(issue=_CATEGORY_UNKNOWN)
    if short_fixed_term(spec, ctx) or not_permanent(spec, ctx):
        return _NONE
    if category in (spec.hourly_categories or ()):
        return _NONE if extra else _hourly(spec, ctx)
    if spec.categories and category not in spec.categories:
        return ContractualRun(issue=_UNCOVERED)
    return _by_month(spec, ctx, extra=extra)


def _by_month(
    spec: ContractualFundContribution, ctx: RunContext, *, extra: bool
) -> ContractualRun:
    """Return the monthly amount of the level, or the ratei of an extra month.

    Returns:
        The amount, an issue when the level has none.
    """
    key, series = _series(spec, ctx)
    if series is None:
        return ContractualRun(issue=_UNCOVERED)
    added = spec.not_enrolled_monthly
    if contributing(ctx.request.pension_fund):
        added = None
    with rule_scope(ruleset=ctx.contract.ccnl.meta.ccnl_id, feature=_FEATURE):
        day = ctx.contract.tctx.competence
        monthly = series.value_at(day)
        monthly += _ZERO if added is None else added.value_at(day)
    if extra:
        months = _ZERO if ctx.accrual is None else Decimal(ctx.accrual.months)
        amount = money(monthly * months / _TWELVE)
        return ContractualRun(amount, series, key=key, not_enrolled=added)
    read = ContractualRun(series=series, key=key, not_enrolled=added)
    return _monthly(spec, ctx, monthly, read)


def _hourly(spec: ContractualFundContribution, ctx: RunContext) -> ContractualRun:
    """Return the amount per ordinary hour worked of an hourly category.

    CNCE vademecum: "dovrà essere calcolato [...] con esclusivo riferimento
    [...] alle ore ordinarie effettivamente lavorate", the monthly amount
    "arrotondato all'euro".

    Returns:
        The amount rounded to the euro, an issue without the hours or the
        level amount.
    """
    apprentice = isinstance(ctx.request.contract_type, Apprentice)
    level = ctx.contract.level.code
    key, series = f"hourly[{level}]", (spec.hourly_by_level or {}).get(level)
    if apprentice and spec.apprentice_hourly is not None:
        key, series = "hourly[apprentice]", spec.apprentice_hourly
    hours = ctx.request.ordinary_hours_worked
    if series is None:
        return ContractualRun(issue=_UNCOVERED)
    if hours is None:
        return ContractualRun(series=series, issue=_HOURS_UNKNOWN, key=key)
    with rule_scope(ruleset=ctx.contract.ccnl.meta.ccnl_id, feature=_FEATURE):
        rate = series.value_at(ctx.contract.tctx.competence)
    amount = (rate * hours.value).quantize(_EURO, rounding=ROUND_HALF_UP)
    return ContractualRun(amount, series, key=key)


def _pays_month(ctx: RunContext) -> bool:
    return ctx.run_kind in _PAYING_KINDS and ctx.proration.posted_by is None


def _series(
    spec: ContractualFundContribution, ctx: RunContext
) -> tuple[str, TimeSeries | None]:
    apprentice = isinstance(ctx.request.contract_type, Apprentice)
    if apprentice and spec.apprentice_monthly is not None:
        return "apprentice", spec.apprentice_monthly
    level = ctx.contract.level.code
    return level, spec.monthly_by_level.get(level)


def _monthly(
    spec: ContractualFundContribution,
    ctx: RunContext,
    monthly: Decimal,
    read: ContractualRun,
) -> ContractualRun:
    request = ctx.request
    hours, full = request.weekly_hours, request.full_time_weekly_hours
    part_time = hours is not None and full is not None and hours.value < full.value
    if spec.minimum_days_in_month is not None and (
        worked_days(ctx) < spec.minimum_days_in_month
    ):
        return read
    partial = ctx.proration.partial and spec.minimum_days_in_month is None
    unruled = partial or (part_time and spec.part_time_proportional is None)
    paths = frozenset(
        {f"{ctx.contract.ccnl.meta.ccnl_id}/{PARTIAL_VARIANT}"} if unruled else ()
    )
    if part_time and spec.part_time_proportional and hours and full:
        monthly = money(monthly * hours.value / full.value)
    return replace(read, amount=monthly, paths=paths)


def contractual_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation paths the contractual contribution traversed.

    Returns:
        The paths of :func:`contractual_run`.
    """
    return contractual_run(ctx).paths


def contractual_rules(ctx: RunContext, prefix: str) -> tuple[Rule, ...]:
    """Return the clause of the contractual contribution the run read.

    Returns:
        The amount in force of the series the run read, empty without one.
    """
    spec = ctx.contract.ccnl.parameters.contractual_fund_contribution
    run = contractual_run(ctx)
    series = run.series
    if spec is None or series is None:
        return ()
    rule = f"{prefix}:contractual_fund_contribution"
    day = ctx.contract.tctx.competence
    read = ((run.key, series), ("not_enrolled", run.not_enrolled))
    return tuple(
        (f"{rule}[{key}][{p.valid_from}]", p.provenance or spec.provenance)
        for key, s in read
        if s is not None and (p := s.period_at(day)) is not None
    )
