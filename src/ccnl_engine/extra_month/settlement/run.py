"""The extra-month settlement of one run, with the fourteenth offset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.extra_month.offset.services import offset_terms, with_offset_issue
from ccnl_engine.extra_month.settlement.services import settle_extra_months

if TYPE_CHECKING:
    from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
    from ccnl_engine.period.context.services import RunContext

__all__ = ["run_settlement"]


def run_settlement(ctx: RunContext) -> ExtraMonthSettlement:
    """Settle the extra months the run liquidates.

    The pre-existing extra month of the worker is credited against the
    fourteenth where the CCNL says so, and an unknown amount adds its
    missing-fact issue.

    Returns:
        The settlement of the run.
    """
    settlement = settle_extra_months(
        ctx.settlements,
        ctx.regular_chain,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.resolver,
        ctx.policy_context,
        *offset_terms(ctx),
    )
    return with_offset_issue(settlement, ctx)
