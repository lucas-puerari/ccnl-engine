"""Reduced employer INPS contributions of agriculture in disadvantaged zones.

INPS circ. 43/2026 par. 7: the employer contributions of the agricultural
employers of the zones "particolarmente svantaggiate (ex montani)" are cut
by 75%, those of the "svantaggiate" by 68%; the cut does not apply to the
0.30% of art. 25 c. 4 L. 845/1978.  Which zone the land lies in is known to
the employer only:
:attr:`~ccnl_engine.payroll.employment.inputs_employer.EmployerProfile.agricultural_zone`
states it.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from ccnl_engine.primitives import NonNegativeRate, PercentageRate  # noqa: TC001
from ccnl_engine.provenance.source.models_chain import RuleProvenance  # noqa: TC001

if TYPE_CHECKING:
    from ccnl_engine.tax.contribution.models import InpsRates

__all__ = ["AgriculturalZone", "ZoneReduction", "with_zone_reduction"]


class AgriculturalZone(StrEnum):
    """Zone of the agricultural land, for the reduced contributions.

    Attributes:
        ORDINARY: No reduction.
        DISADVANTAGED: A "zona svantaggiata": 68% less.
        MOUNTAIN: A "zona particolarmente svantaggiata (ex montana)": 75% less.
    """

    ORDINARY = "ordinary"
    DISADVANTAGED = "disadvantaged"
    MOUNTAIN = "mountain"


class ZoneReduction(BaseModel):
    """The cut of the employer contributions of the disadvantaged zones.

    Attributes:
        disadvantaged: Share cut in a zona svantaggiata.
        mountain: Share cut in a zona particolarmente svantaggiata.
        excluded_rate: Part of the employer rate the cut does not touch
            (the 0.30% of art. 25 c. 4 L. 845/1978).
        provenance: Where the cuts are read from.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    disadvantaged: PercentageRate
    mountain: PercentageRate
    excluded_rate: NonNegativeRate
    provenance: RuleProvenance | None = None

    def share(self, zone: AgriculturalZone) -> Decimal:
        """Return the share of the employer contributions cut in ``zone``.

        Returns:
            Zero in an ordinary zone.
        """
        if zone is AgriculturalZone.DISADVANTAGED:
            return self.disadvantaged
        if zone is AgriculturalZone.MOUNTAIN:
            return self.mountain
        return Decimal(0)


def with_zone_reduction(rates: InpsRates, zone: AgriculturalZone | None) -> InpsRates:
    """Return ``rates`` of an employer of ``zone``.

    Each employer rate ``r`` becomes ``r - share x (r - excluded)``, the IVS
    rate ``ivs x (1 - share)``: the cut reaches every employer contribution
    but the excluded 0.30%, which stays in the non-IVS part.

    Returns:
        ``rates`` of a sector without the cut or of an ordinary zone; the
        cut rates of a disadvantaged zone; with the zone unknown, ``rates``
        flagged ``zone_reduction_open``, for a ``missing_fact`` issue.
    """
    cut = rates.zone_reduction
    if cut is None:
        return rates
    if zone is None:
        return rates.model_copy(update={"zone_reduction_open": True})
    share = cut.share(zone)
    if not share:
        return rates

    def reduced(rate: Decimal) -> Decimal:
        return rate - share * (rate - cut.excluded_rate)

    return rates.model_copy(
        update={
            "employer_rate": reduced(rates.employer_rate),
            "employer_ivs_rate": rates.employer_ivs_rate * (1 - share),
            "employer_rate_by_category": {
                c: reduced(r) for c, r in rates.employer_rate_by_category.items()
            },
            "employer_fixed_term_rate_by_category": {
                c: reduced(r)
                for c, r in rates.employer_fixed_term_rate_by_category.items()
            },
        }
    )
