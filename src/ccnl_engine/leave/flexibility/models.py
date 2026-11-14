"""Permits a flexible working time adds to the worker.

Studi professionali art. 92: the weekly hours may be averaged over six
months; a worker whose week goes over the normal hours earns "un
incremento dei permessi retribuiti" of 30 minutes a week up to 44 hours and
of 60 minutes over 44 and up to 48, not absorbed by other reductions; the
hours not taken are "pagate con la maggiorazione prevista per le ore di
straordinario [...] entro e non oltre il sesto mese successivo a quello
corrispondente il termine del programma annuale di flessibilità".
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance  # noqa: TC001

__all__ = ["FlexibilityBand", "FlexibilityPermits"]

_MINUTES = Decimal(60)
_ZERO = Decimal(0)


class FlexibilityBand(BaseModel):
    """The permit a week earns up to a number of hours worked.

    Attributes:
        up_to_hours: Hours worked in the week the band reaches, included.
        minutes: Minutes of permit the week earns.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    up_to_hours: Decimal = Field(gt=0)
    minutes: Decimal = Field(gt=0)


class FlexibilityPermits(BaseModel):
    """The permits of a yearly programme of flexibility.

    Attributes:
        normal_weekly_hours: Normal hours of the week; a week over them
            earns the permit of its band.
        bands: Bands by hours worked, in ascending order; a week over the
            last band earns nothing (beyond the regime).
        payout_months_after: Months after the last month of the programme
            year whose pay settles the hours not taken.
        premium_band: Code of the overtime band whose premium the hours
            not taken are paid with.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    normal_weekly_hours: Decimal = Field(gt=0)
    bands: tuple[FlexibilityBand, ...] = Field(min_length=1)
    payout_months_after: int = Field(ge=0, le=12)
    premium_band: str
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _ascending(self) -> Self:
        limits = [b.up_to_hours for b in self.bands]
        if limits != sorted(limits) or limits[0] <= self.normal_weekly_hours:
            msg = "flexibility bands must ascend above the normal weekly hours"
            raise ValueError(msg)
        return self

    def hours_for(self, worked: Decimal) -> Decimal:
        """Return the permit hours a week of ``worked`` hours earns.

        Returns:
            The minutes of the first band reaching ``worked``, in hours; 0
            up to the normal hours and beyond the last band.
        """
        if worked <= self.normal_weekly_hours:
            return _ZERO
        band = next((b for b in self.bands if worked <= b.up_to_hours), None)
        return _ZERO if band is None else band.minutes / _MINUTES
