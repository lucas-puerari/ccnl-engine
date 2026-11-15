"""The contribution exemption of one run.

The exemption cuts the employer contributions of the run less the part of
the rate no exemption cuts (:class:`~ccnl_engine.contribution.exemption.
models.ReliefExclusion`), by the share of the measure, up to the cap of the
month.  INPS circ. 90/2025 par. 4 and 91/2025 par. 4 compute it on the
contributions due net of the compensations of the TFR conferred (D.Lgs.
252/2005 art. 10), so it applies after them.  The cap is that of the
month's denuncia: the regular or termination run of the month takes it, a
separate extra-month or adjustment run takes none and says so.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contribution.exemption.inputs import EXEMPTION_FEATURE
from ccnl_engine.contribution.exemption.mothers import mothers_decisions
from ccnl_engine.contribution.exemption.rules import (
    measure_rule,
    month_cap,
    months_of,
)
from ccnl_engine.contribution.results import ContributionComponent
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import Apprentice, FixedTerm
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.fund.solidarity.services import (
    EMPLOYER_COMPONENT as SOLIDARITY_EMPLOYER,
)
from ccnl_engine.leave.services import part_time_ratio
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.run.types import RunKind
from ccnl_engine.sickness.window.rules import months_after

if TYPE_CHECKING:
    from ccnl_engine.amount.types import _PeriodAmounts
    from ccnl_engine.contribution.exemption.inputs import (
        ContributionExemption,
        ExemptionMeasure,
    )
    from ccnl_engine.contribution.rate.models import InpsRates
    from ccnl_engine.contribution.results import ContributionBreakdown
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "EXEMPTION_COMPONENT",
    "ExemptionRun",
    "exempted",
    "exemption_decisions",
    "exemption_run",
    "with_exemption",
]

#: Component of the exemption in the INPS breakdown.
EXEMPTION_COMPONENT = "contribution_exemption"
_ZERO = Decimal(0)
_MONTHLY = frozenset({RunKind.REGULAR, RunKind.TERMINATION})


@dataclass(frozen=True)
class ExemptionRun:
    """The exemption of one run.

    Attributes:
        measure: The measure.
        share: Share of the contributions exempted.
        cap: Cap of the month, cut to the days and the part time.
        code: UniEmens <CodiceCausale>.
        monthly: The run carries the month's denuncia; ``False`` for a
            separate extra-month or adjustment run, which takes none.
    """

    measure: ExemptionMeasure
    share: Decimal
    cap: Decimal
    code: str
    monthly: bool = True


def _check(ctx: RunContext, exemption: ContributionExemption) -> None:
    """Reject a worker or a hire the measure excludes.

    Raises:
        InvalidInputError: For an apprentice, a domestic or public
            employment, a dirigente of a measure for other staff, or a hire
            after the last day of the measure.
    """
    rule = measure_rule(exemption)
    inps = ctx.contract.year_rules.inps
    reason = None
    if isinstance(ctx.request.contract_type, Apprentice):
        reason = "an apprentice takes no exemption"
    elif inps is None or inps.public_funds:
        reason = "the exemptions are for private employers, not domestic work"
    elif ctx.worker_category is WorkerCategory.DIRIGENTE and not rule.managers:
        reason = f"the {exemption.measure} exemption excludes the dirigenti"
    elif exemption.start > rule.last_start:
        reason = (
            f"the {exemption.measure} exemption takes hires until {rule.last_start}"
        )
    if reason is not None:
        msg = f"Employment.contribution_exemption: {reason}"
        raise InvalidInputError(msg, feature=EXEMPTION_FEATURE)


def exemption_run(ctx: RunContext) -> ExemptionRun | None:
    """Return the exemption of the run.

    Returns:
        The exemption when the month of the run falls within its months
        and the employment; ``None`` otherwise.
    """
    exemption = ctx.request.contribution_exemption
    if exemption is None:
        return None
    _check(ctx, exemption)
    competence = ctx.contract.tctx.competence
    first = competence.replace(day=1)
    last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    fixed = isinstance(ctx.request.contract_type, FixedTerm)
    months = months_of(exemption, fixed_term=fixed)
    ends = months_after(exemption.start, months) - timedelta(days=1)
    period = ctx.request.employment_period
    hired = first if period is None else period.started_on
    left = last if period is None or period.ended_on is None else period.ended_on
    start: date = max(first, exemption.start, hired)
    end: date = min(last, ends, left)
    if end < start:
        return None
    whole = start == first and end == last
    days = None if whole else (end - start).days + 1
    rule = measure_rule(exemption)
    cap = month_cap(rule.cap, days, part_time_ratio(ctx))
    monthly = ctx.run_kind in _MONTHLY
    return ExemptionRun(exemption.measure, exemption.share, cap, rule.code, monthly)


def _issue(code: str, message: str) -> CalculationIssue:
    return CalculationIssue(
        code=code,
        capability=EXEMPTION_FEATURE,
        message=message,
        status=CalculationStatus.PROVISIONAL,
        cause=IssueCause.RULE,
    )


#: The rate table does not break down the rate of the worker's category.
EXCLUSION_UNKNOWN = "contribution_exemption_exclusion_unknown"
#: A separate extra-month or adjustment run takes no exemption.
OTHER_RUN = "contribution_exemption_other_run"


def with_exemption(
    run: ExemptionRun | None,
    inps: InpsRates | None,
    category: WorkerCategory | None,
    breakdown: ContributionBreakdown,
) -> tuple[ContributionBreakdown, tuple[CalculationIssue, ...]]:
    """Return ``breakdown`` less the exemption of the run.

    The contributions of a solidarity fund on top of the sector rates are
    excluded with the part of the rate :attr:`InpsRates.relief_excluded`
    names.

    Returns:
        The breakdown with a negative employer component and the employer
        total cut by the exemption, never below zero; unchanged, with an
        issue, when the rates do not say what the exemption excludes or
        the run does not carry the month's denuncia.
    """
    if run is None or not breakdown.employer:
        return breakdown, ()
    if not run.monthly:
        message = (
            "contribution_exemption: the cap of the month is taken by its "
            "regular run; this run takes no exemption"
        )
        return breakdown, (_issue(OTHER_RUN, message),)
    exclusion = None if inps is None else inps.relief_excluded
    excluded = None if exclusion is None else exclusion.for_category(category)
    if excluded is None:
        message = (
            "contribution_exemption: the rate table does not say which part "
            "of the rate of the worker's category the exemption excludes; "
            "none is applied"
        )
        return breakdown, (_issue(EXCLUSION_UNKNOWN, message),)
    amounts = {c.name: c for c in breakdown.components}
    ordinary = amounts.get("non_ivs_employer")
    base = _ZERO if ordinary is None else ordinary.base
    fund = amounts.get(SOLIDARITY_EMPLOYER)
    outside = money(base * excluded) + (_ZERO if fund is None else fund.amount)
    eligible = max(_ZERO, breakdown.employer - outside)
    amount = min(money(eligible * run.share), run.cap, breakdown.employer)
    if not amount:
        return breakdown, ()
    component = ContributionComponent(
        EXEMPTION_COMPONENT, eligible, -run.share, -amount
    )
    exempted = replace(
        breakdown,
        employer=breakdown.employer - amount,
        components=(*breakdown.components, component),
    )
    return exempted, ()


def exempted(
    ctx: RunContext, amounts: _PeriodAmounts, breakdown: ContributionBreakdown
) -> tuple[_PeriodAmounts, ContributionBreakdown]:
    """Return the amounts and breakdown of the run less its exemption.

    Returns:
        The employer contributions cut by the exemption, with its issue.
    """
    rules = ctx.contract.year_rules.inps
    cut, issues = with_exemption(
        exemption_run(ctx), rules, ctx.worker_category, breakdown
    )
    if cut is breakdown and not issues:
        return amounts, breakdown
    updated = replace(
        amounts, inps_employer=cut.employer, issues=amounts.issues + issues
    )
    return updated, cut


#: Law of each measure, as the decision names it.
_LAW = {
    "young": "dl-60-2024-art22",
    "women": "dl-60-2024-art23",
    "zes": "dl-60-2024-art24",
    "mothers": "l-199-2025-art1-c210",
}


def exemption_decisions(
    ctx: RunContext, breakdown: ContributionBreakdown
) -> tuple[CalculationDecision, ...]:
    """Trace the exemption of the run.

    Returns:
        One decision with the amount exempted and the UniEmens code when
        the run falls within the months of an exemption; none otherwise.
    """
    run = exemption_run(ctx)
    if run is None:
        return mothers_decisions(ctx, breakdown)
    amount = -sum(
        (c.amount for c in breakdown.components if c.name == EXEMPTION_COMPONENT),
        _ZERO,
    )
    return (
        CalculationDecision(
            capability=EXEMPTION_FEATURE,
            status=CalculationStatus.FINAL,
            reason_code="contribution_exemption_applied",
            rule=_LAW[run.measure],
            rule_version=str(ctx.fiscal_year),
            inputs={
                "measure": str(run.measure),
                "share": str(run.share),
                "cap": str(run.cap),
                "code": run.code,
            },
            amount=amount,
        ),
        *mothers_decisions(ctx, breakdown),
    )
