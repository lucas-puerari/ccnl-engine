"""Missing eligible holiday counts for workers paid by the hour."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def paid_holiday_issue(ctx: RunContext) -> CalculationIssue | None:
    """Report an unknown count only when this run posts a holiday-capable hourly pay.

    Returns:
        An incomplete missing-fact issue, or ``None`` when the count is stated
        (including zero) or this run cannot pay the holiday quota.
    """
    spec = ctx.contract.ccnl.parameters.hourly_pay
    if (
        ctx.proration.hourly is None
        or not ctx.proration.posts_pay
        or spec is None
        or spec.holiday_hours is None
        or ctx.request.paid_holiday_days is not None
    ):
        return None
    return CalculationIssue(
        code="paid_holiday_days_unknown",
        capability="base_salary",
        message=(
            "eligible paid holiday days are unknown: hourly holiday pay is "
            "omitted; state paid_holiday_days, including zero when none are due"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact="paid_holiday_days",
    )
