"""Missing sub-sector input for work premiums."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.event.facade import OvertimeEvent

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

SUBSECTOR_FACT = "subsector"


def subsector_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of the sub-sector bands left out.

    Returns:
        An incomplete issue naming ``subsector`` when the CCNL sets its
        overtime bands by sub-sector, the employer does not state its own
        and the run prices an overtime event from the bands, else ``None``.
    """
    priced = any(
        isinstance(e, OvertimeEvent) and e.multiplier is None
        for e in ctx.request.events
    )
    if not (ctx.contract.subsector_unknown and priced):
        return None
    return CalculationIssue(
        code="subsector_unknown",
        capability="overtime",
        message=(
            "the CCNL sets its overtime premiums by sub-sector and the "
            "employer does not state its own: the overtime shown is priced "
            "with the first table of the CCNL; state EmployerProfile.subsector"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=SUBSECTOR_FACT,
    )
