"""The CCNL terms a run pays a trasferta with."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.working_time.travel.models import CcnlTravelAllowance

__all__ = ["TravelTerms"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class TravelTerms:
    """The CCNL travel allowance a run pays a trasferta with.

    Attributes:
        rules: CCNL amounts and TFR rule, ``None`` when the CCNL has none.
        ruleset: Ruleset identifier of the CCNL.
        monthly_minimum: Monthly minimum of the level, for a share of it.
        monthly_pay: Monthly retribuzione di fatto, for a share of it.
        monthly_normal: Monthly minimum and seniority increments, the
            normale retribuzione of a share of it.
    """

    rules: CcnlTravelAllowance | None
    ruleset: str
    monthly_minimum: Decimal = _ZERO
    monthly_pay: Decimal = _ZERO
    monthly_normal: Decimal = _ZERO

    def monthly(self, base: str) -> Decimal:
        """Return the monthly pay a share of the daily pay is taken of.

        Returns:
            The minimum, the normale retribuzione or the retribuzione di fatto.
        """
        if base == "minimum":
            return self.monthly_minimum
        return self.monthly_normal if base == "normal" else self.monthly_pay
