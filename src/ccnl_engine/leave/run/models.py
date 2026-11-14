"""Leave account after a run, with the indemnities it paid."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.settlement.models import LeaveSettlement
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem

__all__ = ["RunLeave"]


@dataclass(frozen=True)
class RunLeave:
    """Leave account after the run, with the indemnities it paid, if any.

    Attributes:
        account: The leave account the closing state carries.
        settlement: Indemnity of the residual leave, on a run that closes
            the employment, or of the permits at their deadline; ``None``
            on any other run.
        flexibility: Payment of the flexibility permits of a programme
            whose payout month is the run's, ``None`` otherwise.
    """

    account: LeaveAccount
    settlement: LeaveSettlement | None = None
    flexibility: LeaveSettlement | None = None

    @property
    def _paid(self) -> tuple[LeaveSettlement, ...]:
        return tuple(s for s in (self.settlement, self.flexibility) if s is not None)

    @property
    def items(self) -> tuple[PayItem, ...]:
        """Pay items of the indemnities."""
        return tuple(i for s in self._paid for i in s.items)

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        """Ledger entries of the indemnities."""
        return tuple(e for s in self._paid for e in s.entries)

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return ``totals`` with the account and the indemnities added.

        Returns:
            A copy of ``totals`` carrying the leave account, with the bases
            of the indemnities, their decisions and their issues added.
        """
        for settlement in self._paid:
            totals = replace(
                totals,
                inps_base=totals.inps_base + settlement.inps_base,
                tfr_base=totals.tfr_base + settlement.tfr_base,
                irpef_base=totals.irpef_base + settlement.irpef_base,
                decisions=(*totals.decisions, settlement.decision),
                issues=totals.issues + settlement.issues,
            )
        return replace(totals, leave=self.account)
