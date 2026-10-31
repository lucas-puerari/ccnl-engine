"""What the run that closes an employment owes after its amounts.

The separate tax of the notice indemnity, at the rate of the TFR the run
settles, and the NASpI contribution of the end of the employment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.termination.naspi.services import naspi_dismissal
from ccnl_engine.termination.notice.settlement.services import notice_tax

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.decision.models import CalculationDecision, CalculationIssue
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["TerminationCharges", "termination_charges"]


@dataclass(frozen=True)
class TerminationCharges:
    """The notice tax and the NASpI contribution of the run."""

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()
    limitations: frozenset[str] = frozenset()


def termination_charges(
    ctx: RunContext,
    items: tuple[PayItem, ...],
    apart_inps: Decimal,
    settled_rate: Decimal | None,
) -> TerminationCharges:
    """Return the notice tax and the NASpI contribution of the run.

    Args:
        ctx: Context of the run.
        items: Pay items of the run's events.
        apart_inps: Employee INPS of the pay taxed apart.
        settled_rate: Rate the computed TFR settlement taxed with.

    Returns:
        Their items, entries, decisions, issues and limitation paths.
    """
    notice = notice_tax(ctx, items, apart_inps, settled_rate)
    naspi = naspi_dismissal(ctx)
    return TerminationCharges(
        items=naspi.items,
        entries=notice.entries + naspi.entries,
        decisions=notice.decisions + naspi.decisions,
        issues=notice.issues + naspi.issues,
        limitations=naspi.limitations,
    )
