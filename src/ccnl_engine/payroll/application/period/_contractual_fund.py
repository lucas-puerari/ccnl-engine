"""Contractual contribution a CCNL owes a fund for every worker.

The amount is fixed per level and month (:class:`~ccnl_engine.contract.domain\
.fund_contribution.ContractualFundContribution`): a run that posts the monthly
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

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.payroll.domain.events import AbsenceEvent, SicknessEpisode
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.fund_contribution import (
        ContractualFundContribution,
    )
    from ccnl_engine.contract.domain.validity import TimeSeries
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
        paths: Limitation paths the run traversed.
        issue: Missing fact that leaves the amount out, if any.
    """

    amount: Decimal = _ZERO
    series: TimeSeries | None = None
    paths: frozenset[str] = frozenset()
    issue: CalculationIssue | None = None


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
    series = _series(spec, ctx)
    if series is None or (spec.categories and category not in spec.categories):
        return ContractualRun(issue=_UNCOVERED)
    if _short_fixed_term(spec, ctx):
        return _NONE
    with rule_scope(ruleset=ctx.contract.ccnl.meta.ccnl_id, feature=_FEATURE):
        monthly = series.value_at(ctx.contract.tctx.competence)
    if extra:
        months = _ZERO if ctx.accrual is None else Decimal(ctx.accrual.months)
        return ContractualRun(money(monthly * months / _TWELVE), series)
    return _monthly(spec, ctx, monthly, series)


def _pays_month(ctx: RunContext) -> bool:
    return ctx.run_kind in _PAYING_KINDS and ctx.proration.posted_by is None


def _series(spec: ContractualFundContribution, ctx: RunContext) -> TimeSeries | None:
    apprentice = isinstance(ctx.request.contract_type, Apprentice)
    if apprentice and spec.apprentice_monthly is not None:
        return spec.apprentice_monthly
    return spec.monthly_by_level.get(ctx.contract.level.code)


def _short_fixed_term(spec: ContractualFundContribution, ctx: RunContext) -> bool:
    """Return whether a fixed term too short for the clause owes nothing.

    A worker enrolled voluntarily owes it whatever the length; a fixed term
    without a stated end has not ended (``EmploymentPeriod.ended_on``).

    Returns:
        True when the fixed term lasts no more than the minimum months.
    """
    request = ctx.request
    period = request.employment_period
    if (
        spec.minimum_fixed_term_months is None
        or not isinstance(request.contract_type, FixedTerm)
        or isinstance(request.pension_fund, PensionFundEnrolment)
        or period is None
        or period.ended_on is None
    ):
        return False
    start = period.started_on
    year, month = divmod(start.month - 1 + spec.minimum_fixed_term_months, 12)
    first = date(start.year + year, month + 1, 1)
    month_end = date(first.year + first.month // 12, first.month % 12 + 1, 1) - _DAY
    # "superiore a tre mesi": the end must reach the same day three months on.
    return period.ended_on < first.replace(day=min(start.day, month_end.day))


def _monthly(
    spec: ContractualFundContribution,
    ctx: RunContext,
    monthly: Decimal,
    series: TimeSeries,
) -> ContractualRun:
    request = ctx.request
    hours, full = request.weekly_hours, request.full_time_weekly_hours
    part_time = hours is not None and full is not None and hours.value < full.value
    if spec.minimum_days_in_month is not None and (
        _worked_days(ctx) < spec.minimum_days_in_month
    ):
        return ContractualRun(series=series)
    partial = ctx.proration.partial and spec.minimum_days_in_month is None
    unruled = partial or (part_time and not spec.part_time_proportional)
    paths = frozenset(
        {f"{ctx.contract.ccnl.meta.ccnl_id}/{PARTIAL_VARIANT}"} if unruled else ()
    )
    if part_time and spec.part_time_proportional and hours and full:
        monthly = money(monthly * hours.value / full.value)
    return ContractualRun(monthly, series, paths)


def _worked_days(ctx: RunContext) -> int:
    """Return the calendar days worked in the month of the run.

    The days of employment in the month, less the sick days and the days of
    an absence without any pay (CNCE vademecum: "non si considerano utili
    [...] le giornate di assenza per malattia [...] e aspettativa non
    retribuita").

    Returns:
        The number of days.
    """
    month = ctx.request.period_id
    first = date(month.year, month.month, 1)
    last = date(month.year + month.month // 12, month.month % 12 + 1, 1) - _DAY
    span = ctx.proration.span or (first, last)
    days = {span[0] + _DAY * n for n in range((span[1] - span[0]).days + 1)}
    for event in ctx.request.events:
        if isinstance(event, SicknessEpisode):
            count = (event.ended_on - event.started_on).days + 1
            days -= {event.started_on + _DAY * n for n in range(count)}
        elif isinstance(event, AbsenceEvent) and event.no_pay_due:
            days -= set(event.days)
    return len(days)


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
    series = contractual_run(ctx).series
    if spec is None or series is None:
        return ()
    level = ctx.contract.level.code
    key = "apprentice" if series is spec.apprentice_monthly else level
    rule = f"{prefix}:contractual_fund_contribution[{key}]"
    periods = (series.period_at(ctx.contract.tctx.competence),)
    return tuple(
        (f"{rule}[{p.valid_from}]", p.provenance or spec.provenance)
        for p in periods
        if p is not None
    )
