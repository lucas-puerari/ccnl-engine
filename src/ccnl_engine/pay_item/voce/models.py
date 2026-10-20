"""The payslip voce of a pay item, as properties of every pay item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.pay_item.voce import rules as voce

if TYPE_CHECKING:
    from decimal import Decimal

__all__ = ["VoceView"]


class VoceView:
    """The voce properties every pay item has (see :mod:`.rules`)."""

    __slots__ = ()

    @property
    def voce_code(self) -> str:
        """Engine code of the payslip voce, for a provider's mapping."""
        return voce.voce_code(self)  # type: ignore[arg-type]

    @property
    def unit(self) -> voce.VoceUnit:
        """Unit the payslip counts the quantity of the item in."""
        return voce.unit(self)  # type: ignore[arg-type]

    @property
    def voce_quantity(self) -> Decimal:
        """Quantity the payslip prints, in :attr:`unit`."""
        return voce.measure(self)  # type: ignore[arg-type]

    @property
    def rate(self) -> Decimal | None:
        """Amount per unit of :attr:`voce_quantity`, ``None`` for none."""
        return voce.unit_rate(self)  # type: ignore[arg-type]

    @property
    def side(self) -> voce.VoceSide:
        """Payslip column: competenza, trattenuta, employer or figurative."""
        return voce.side(self)  # type: ignore[arg-type]
