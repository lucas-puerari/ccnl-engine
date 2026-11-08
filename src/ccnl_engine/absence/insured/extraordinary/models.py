"""The INPS indemnity of the extraordinary leave and its yearly ceilings."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["ExtraordinaryLeaveRates", "YearCeiling"]


class YearCeiling(BaseModel):
    """The most an indemnity pays a day in a year.

    Attributes:
        year: The calendar year.
        amount: The daily maximum.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    amount: Decimal = Field(gt=Decimal(0))


class ExtraordinaryLeaveRates(BaseModel):
    """INPS indemnity of the extraordinary leave (art. 42 c. 5 D.Lgs. 151/2001).

    Attributes:
        daily_ceilings: The daily maximum of each year INPS published.
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    daily_ceilings: tuple[YearCeiling, ...]
    provenance: RuleProvenance

    def ceiling(self, year: int) -> Decimal | None:
        """Return the daily maximum of ``year``.

        Returns:
            The maximum, ``None`` for a year the bundle does not list.
        """
        return next((c.amount for c in self.daily_ceilings if c.year == year), None)
