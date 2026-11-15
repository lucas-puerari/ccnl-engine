"""The share of the employer rate a contribution exemption does not cut.

The exemptions of 2025-2026 (INPS circ. 90/2025, 91/2025, 10/2026,
82/2026) cut the employer contributions except the INAIL premiums, the
Fondo di Tesoreria TFR, the solidarity funds of D.Lgs. 148/2015 artt. 26,
27, 29 and 40 (the FIS among them), the 0.30% of L. 845/1978 art. 25 c. 4
for continuing training, and the solidarity and non-pension contributions.
:class:`ReliefExclusion` is the part of an employer tier rate those items
make up.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import NonNegativeRate

__all__ = ["ReliefExclusion"]


class ReliefExclusion(BaseModel):
    """The part of an employer tier rate no exemption cuts.

    Attributes:
        rate: The part of the tier rate, for the categories not listed.
        fund_rate: The part of :attr:`rate` that is the employer share of
            the FIS or of a solidarity fund, which a fund in place of the
            FIS replaces and the cut of art. 29 c. 8-bis lowers.
        rate_by_category: The part of the rate of a category, ``None`` when
            the sources do not break that rate down.
        provenance: The exemption circular and the rate table it is read
            against.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: NonNegativeRate
    fund_rate: NonNegativeRate = Decimal(0)
    rate_by_category: dict[WorkerCategory, NonNegativeRate | None] = {}
    provenance: RuleProvenance

    def for_category(self, category: WorkerCategory | None) -> Decimal | None:
        """Return the excluded part of the rate of ``category``.

        Returns:
            The rate of the category when listed, else :attr:`rate`;
            ``None`` when the sources leave the category open.
        """
        if category is not None and category in self.rate_by_category:
            return self.rate_by_category[category]
        return self.rate

    def with_fund(self, employer_rate: Decimal) -> ReliefExclusion:
        """Return the exclusion with the fund share set to ``employer_rate``.

        Returns:
            The exclusion of a tier whose FIS share a solidarity fund
            replaces, or whose FIS rate is cut: every known rate moved by
            the difference.
        """
        delta = employer_rate - self.fund_rate
        by_category = {
            category: None if rate is None else rate + delta
            for category, rate in self.rate_by_category.items()
        }
        return self.model_copy(
            update={
                "rate": self.rate + delta,
                "fund_rate": employer_rate,
                "rate_by_category": by_category,
            }
        )
