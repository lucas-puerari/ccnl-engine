"""Employer and employee eligibility for a conditional solidarity fund."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import FixedTerm

if TYPE_CHECKING:
    from ccnl_engine.fund.solidarity.models import SolidarityFund
    from ccnl_engine.period.context.services import RunContext

__all__ = ["covered_fund", "solidarity_coverage_issue"]


def covered_fund(ctx: RunContext) -> SolidarityFund | None:
    """Withhold a fund that needs unconfirmed employer eligibility.

    Returns:
        The agreement's fund only when employer coverage is confirmed or
        the fund is unconditional.
    """
    fund = ctx.contract.ccnl.parameters.solidarity_fund
    if fund is not None and fund.requires_employer_coverage:
        return fund if ctx.request.employer.solidarity_fund_covered is True else None
    return fund


def solidarity_coverage_issue(ctx: RunContext) -> CalculationIssue | None:
    """Report unknown employer eligibility for a fund on permanent non-executives.

    Returns:
        A missing-fact blocker only when the fund could charge this worker.
    """
    fund = ctx.contract.ccnl.parameters.solidarity_fund
    if fund is None or not fund.requires_employer_coverage:
        return None
    if ctx.request.employer.solidarity_fund_covered is not None:
        return None
    if isinstance(ctx.request.contract_type, FixedTerm) and not fund.covers_fixed_term:
        return None
    if ctx.worker_category == WorkerCategory.DIRIGENTE and not fund.covers_executives:
        return None
    return CalculationIssue(
        code="missing_fact",
        message="Employer solidarity fund coverage is unknown; "
        "its ordinary contribution is withheld.",
        status=CalculationStatus.INCOMPLETE,
        fact="solidarity_fund_covered",
        capability="inps_employer",
    )
