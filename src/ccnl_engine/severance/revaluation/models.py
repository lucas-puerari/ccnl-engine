"""Rules of the yearly TFR revaluation (art. 2120 c. 4 c.c.) and its tax."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import PercentageRate

_DECEMBER = 12

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
        monthly: Indexes of the months of the year ISTAT has published,
            from January, in the base of :attr:`december`; a termination
            within the year revalues the fund on the index of its month
            (art. 2120 c. 5 c.c.).
    """

    model_config = ConfigDict(extra="forbid")

    previous_december: Decimal = Field(gt=Decimal(0))
    december: Decimal | None = Field(default=None, gt=Decimal(0))
    link_coefficient: Decimal = Field(gt=Decimal(0))
    monthly: tuple[Annotated[Decimal, Field(gt=Decimal(0))], ...] = Field(
        default=(), max_length=12
    )
    provenance: RuleProvenance | None = None

    def month_increase(self, month: int) -> Decimal | None:
        """Return the increase of the index of ``month`` over December before.

        Returns:
            ``index * link_coefficient / previous_december - 1``, unrounded,
            the index of December being :attr:`december` when
            :attr:`monthly` stops before it; ``None`` while the month is not
            published.
        """
        if month <= len(self.monthly):
            index: Decimal | None = self.monthly[month - 1]
        else:
            index = self.december if month == _DECEMBER else None
        if index is None:
            return None
        return index * self.link_coefficient / self.previous_december - 1

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

    def fraction_rate(self, months: int) -> Decimal | None:
        """Return the rate of ``months`` of the year, at a termination.

        Art. 2120 c. 5 c.c.: the index increase is that of the month of the
        termination over December of the year before, and the fixed 1.5%
        is due for the months of service of the year (a fraction of 15
        days or more counts as a whole month).

        Args:
            months: Whole months of the year counted, 0 to 12.

        Returns:
            ``fixed * months / 12 + index_share * increase of the month``,
            unrounded; zero for no month; ``None`` while the index of the
            month is not published.
        """
        if months == 0:
            return Decimal(0)
        increase = self.price_index.month_increase(months)
        if increase is None:
            return None
        return self.rate.fixed * months / _DECEMBER + self.rate.index_share * increase
