"""Employer charges the run accrues on its contribution base."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.contribution.inail.services import inail_premium
from ccnl_engine.period.step.services import RunEvents

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.period.step.services import RunAmounts

__all__ = ["run_employer_charges"]


def run_employer_charges(
    ctx: RunContext, events: RunEvents, run: RunAmounts
) -> RunEvents:
    """Add the INAIL premium of the run to its events.

    Returns:
        ``events`` with the item, entry and decision of the premium, as
        they are without the employer's INAIL rate.
    """
    base = run.inps_base(ctx.monthly_gross + events.totals.inps_base)
    premium = inail_premium(ctx, base)
    if not premium.decisions:
        return events
    totals = events.totals
    return RunEvents(
        replace(totals, decisions=totals.decisions + premium.decisions),
        events.items + premium.items,
        events.entries + premium.entries,
    )
