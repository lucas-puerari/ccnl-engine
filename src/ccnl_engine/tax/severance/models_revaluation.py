"""Rules of the yearly TFR revaluation (art. 2120 c. 4 c.c.) and its tax."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.primitives import PercentageRate
from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.models_chain import RuleProvenance

__all__ = [
    "TfrPriceIndex",
    "TfrRevaluationRate",
    "TfrRevaluationRules",
    "TfrSubstituteTax",
]


class TfrRevaluationRate(BaseModel):
    """Rate the TFR fund is revalued by at 31 December (art. 2120 c. 4 c.c.).

    Attributes:
        fixed: Fixed part of the rate, 1.5%.
        index_share: Share of the yearly increase of the price index, 75%.
    """

    model_config = ConfigDict(extra="forbid")

    fixed: PercentageRate
    index_share: PercentageRate
    provenance: RuleProvenance | None = None


class TfrPriceIndex(BaseModel):
    """ISTAT consumer price index for blue- and white-collar households (FOI).

    Without tobacco (L. 81/1992 art. 4 c. 1).  The increase of the year is
    the December index over the December index of the year before; when
    ISTAT changed the index base between them, the ratio is multiplied by
    the link coefficient from the old base to the new one.

    Attributes:
        previous_december: Index of December of the year before.
        december: Index of December of the year, ``None`` until ISTAT
            publishes it (mid-January of the next year).
        link_coefficient: Link coefficient between the bases of the two
            indexes, ``1`` when they share one.
    """

    model_config = ConfigDict(extra="forbid")

    previous_december: Decimal = Field(gt=Decimal(0))
    december: Decimal | None = Field(default=None, gt=Decimal(0))
    link_coefficient: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance | None = None

    def increase(self) -> Decimal | None:
        """Return the yearly increase of the index, as a fraction.

        Returns:
            ``december * link_coefficient / previous_december - 1``,
            unrounded; ``None`` while the December index is not published.
        """
        if self.december is None:
            return None
        ratio = self.december * self.link_coefficient / self.previous_december
        return ratio - 1


class TfrSubstituteTax(BaseModel):
    """Substitute tax on the revaluation (D.Lgs. 47/2000 art. 11 cc. 3-4).

    The employer applies it to the revaluation of each year and charges it
    to the TFR fund; it is not withheld from the pay of the run.

    Attributes:
        rate: Tax rate, 17%.
    """

    model_config = ConfigDict(extra="forbid")

    rate: PercentageRate
    provenance: RuleProvenance | None = None


class TfrRevaluationRules(BaseModel):
    """Revaluation of the TFR fund at 31 December of one year.

    Attributes:
        year: Year whose 31 December the rules revalue the fund at.
        rate: Fixed part and index share of the rate.
        price_index: The FOI indexes of the year and of the year before.
        substitute_tax: Tax charged on the revaluation.
        ruleset: Identity of the data file.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    rate: TfrRevaluationRate
    price_index: TfrPriceIndex
    substitute_tax: TfrSubstituteTax
    ruleset: RulesetIdentity | None = None

    def annual_rate(self) -> Decimal | None:
        """Return the revaluation rate of the year, unrounded.

        Returns:
            ``fixed + index_share * increase``; ``None`` while the December
            index of the year is not published.
        """
        increase = self.price_index.increase()
        if increase is None:
            return None
        return self.rate.fixed + self.rate.index_share * increase
