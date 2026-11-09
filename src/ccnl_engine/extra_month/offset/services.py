"""Art. 143: credit extra remuneration already paid at contract entry."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.extra_month.offset.models import FourteenthPriorExtraOffset
    from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
    from ccnl_engine.period.context.services import RunContext


_MISSING = CalculationIssue(
    code="prior_extra_month_unknown",
    capability="base_salary",
    message=(
        "The fourteenth may be reduced by extra remuneration months received "
        "at contract entry; state Employment.prior_extra_month_amount "
        "(zero if none, excluding merit bonuses). The displayed amount "
        "is before offset."
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="prior_extra_month_amount",
)


def prior_extra_issue(
    rule: FourteenthPriorExtraOffset | None,
    employment: EmploymentPeriod | None,
    amount: Decimal | None,
) -> CalculationIssue | None:
    """Require the historical amount only if the worker could have received it.

    Returns:
        A missing-fact issue for a pre-entry (or undated) worker whose amount
        is unknown; otherwise ``None``.
    """
    if rule is None or (
        employment is not None and employment.started_on > rule.entry_on
    ):
        return None
    return _MISSING if amount is None else None


def run_offset_issue(ctx: RunContext) -> CalculationIssue | None:
    """Flag an unknown historical credit only when this run pays a fourteenth.

    Returns:
        The missing-fact issue for an eligible worker, if any.
    """
    if not (
        (
            ctx.payment.run_id.kind == "fourteenth"
            and ctx.accrual is not None
            and ctx.accrual.accrued > 0
        )
        or any(
            s.kind is ExtraMonthKind.FOURTEENTH and s.accrued > 0
            for s in ctx.settlements
        )
    ):
        return None
    return prior_extra_issue(
        ctx.contract.ccnl.parameters.fourteenth_prior_extra_offset,
        ctx.request.employment_period,
        ctx.request.prior_extra_month_amount,
    )


def offset_fourteenth(
    chain: MonthlyPayChain,
    rule: FourteenthPriorExtraOffset | None,
    employment: EmploymentPeriod | None,
    amount: Decimal | None,
    fraction: Decimal,
) -> MonthlyPayChain:
    """Pay only the positive difference, proportional to accrued twelfths.

    The offset is against the total fourteenth, not just its base salary.
    Unknown amounts leave the unadjusted sum visible with a missing-fact issue.

    Returns:
        The chain with the credit removed, never below zero.
    """
    if (
        rule is None
        or amount is None
        or amount == 0
        or (employment is not None and employment.started_on > rule.entry_on)
    ):
        return chain
    remaining = money(amount * fraction)
    base = chain.base - min(chain.base, remaining)
    remaining -= chain.base - base
    seniority = chain.seniority - min(chain.seniority, remaining)
    remaining -= chain.seniority - seniority
    allowances = []
    for allowance, value in chain.allowances:
        adjusted = value - min(value, remaining)
        remaining -= value - adjusted
        allowances.append((allowance, adjusted))
    return replace(chain, base=base, seniority=seniority, allowances=tuple(allowances))


def offset_terms(
    ctx: RunContext,
) -> tuple[FourteenthPriorExtraOffset | None, EmploymentPeriod | None, Decimal | None]:
    """Return the offset clause, employment and stated amount of the run.

    Returns:
        The arguments :func:`settle_extra_months` takes for the offset.
    """
    return (
        ctx.contract.ccnl.parameters.fourteenth_prior_extra_offset,
        ctx.request.employment_period,
        ctx.request.prior_extra_month_amount,
    )


def with_offset_issue(
    settlement: ExtraMonthSettlement, ctx: RunContext
) -> ExtraMonthSettlement:
    """Add the missing-fact issue of an unknown prior extra month, if any.

    Returns:
        ``settlement``, with the issue appended when :func:`run_offset_issue`
        reports one.
    """
    issue = run_offset_issue(ctx)
    if issue is None:
        return settlement
    return replace(settlement, issues=(*settlement.issues, issue))
