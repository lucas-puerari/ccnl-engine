"""Missing employer activity when an agreement can incur CIGO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def cigo_activity_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return an issue only when the CCNL can incur activity-specific CIGO.

    Returns:
        A provisional issue when a covered employer has not stated its
        activity; otherwise ``None``. The sector-only amount remains shown.
    """
    if (
        ctx.request.employer.activity is not None
        or not ctx.contract.ccnl.meta.cigo_activities
    ):
        return None
    return CalculationIssue(
        code="cigo_activity_unknown",
        capability="inps_employer",
        message=(
            "the employer may owe an activity-dependent CIGO contribution; "
            "the sector rate shown does not include that difference: "
            "state EmployerProfile.activity"
        ),
        status=CalculationStatus.PROVISIONAL,
        fact="activity",
    )
