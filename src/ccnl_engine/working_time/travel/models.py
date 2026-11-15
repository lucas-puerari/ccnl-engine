"""The CCNL daily travel allowance (indennità di trasferta) and its bands."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["CcnlTravelAllowance", "TravelAllowanceBand", "TravelQuotas"]


class TravelAllowanceBand(BaseModel):
    """Daily travel allowance of the CCNL for a span of hours away.

    Attributes:
        hours_from: First hour of the span (at least this many hours).
        hours_until: Hours the span stays below; ``None`` for no limit.
        hours_from_exclusive: Whether the span starts above ``hours_from``
            (Studi art. 115: a mission "superiore alle 8 ore").
        hours_until_inclusive: Whether the span includes ``hours_until``.
        italy: Daily amount of a trasferta in Italy.
        abroad: Daily amount of a trasferta abroad.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hours_from: Decimal = Field(ge=Decimal(0))
    hours_until: Decimal | None = None
    hours_from_exclusive: bool = False
    hours_until_inclusive: bool = False
    italy: TimeSeries
    abroad: TimeSeries

    def holds(self, hours: Decimal) -> bool:
        """Return whether ``hours`` away fall in the span.

        Returns:
            Whether ``hours`` is past ``hours_from`` (or at it, unless
            exclusive) and below ``hours_until`` (or at it, if inclusive).
        """
        lower = (
            hours > self.hours_from
            if self.hours_from_exclusive
            else hours >= self.hours_from
        )
        upper = self.hours_until is None or (
            hours <= self.hours_until
            if self.hours_until_inclusive
            else hours < self.hours_until
        )
        return lower and upper


class TravelQuotas(BaseModel):
    """CCNL amounts of a trasferta by its meals and lodging.

    Federmeccanica art. 7 (Sez. Quarta, Titolo I): "Trasferta intera" for
    two meals and the overnight stay, otherwise a "Quota per il pasto
    meridiano o serale" for each meal and a "Quota per il pernottamento",
    each due on its own conditions (distance, return times).

    Attributes:
        whole: Amount of a day with both meals and the overnight stay.
        meal: Amount of each meal.
        overnight: Amount of the overnight stay.
        provenance: Source of the amounts.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    whole: TimeSeries
    meal: TimeSeries
    overnight: TimeSeries
    provenance: RuleProvenance | None = None


class CcnlTravelAllowance(BaseModel):
    """CCNL amounts of the daily travel allowance (indennità di trasferta).

    Attributes:
        bands: Spans of hours away with their amounts; fewer hours than the
            first span give no allowance.
        tfr_base: What of the allowance enters the TFR base: ``"none"``,
            ``"whole"``, or ``"above_exempt"`` (the part above the IRPEF
            exemption, Logistica art. 62 c. 7); ``None`` when the CCNL states
            none (Studi art. 115), and the event must state it.
        mission_duration: Whether the bands are read on the hours of the
            whole mission (``TravelAllowanceEvent.mission_hours``) instead of
            the hours away of a day.
        habitual_discount: Share the diaria drops by for travel habitual to
            the job; ``long_mission_discount`` for a mission over a calendar
            month.  Both together lower it once (Studi art. 115: 10%).
        night_allowance: Amount for each day of at least
            :attr:`night_from_hours` away (Logistica art. 16: 0.93 per
            trasferta of 18 to 24 hours), pay of the period that enters the
            TFR base; ``None`` without one.
        night_from_hours: Hours away from which the night allowance is due.
        quotas: Amounts by meals and lodging in place of the bands of hours
            (Federmeccanica); ``bands`` is then empty.
        minimum_share: Share of the daily minimum of the level each day of
            trasferta is paid, in place of bands and quotas (Lavoro
            domestico art. 33 c. 2: "una diaria giornaliera, pari al 20%
            della retribuzione minima tabellare giornaliera"); ``None``
            without one.
        minimum_divisor: Divisor of the monthly minimum that gives the daily
            one (Lavoro domestico, chiarimento a verbale 1: 1/26).
        provenance: Source and status of the amounts.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bands: tuple[TravelAllowanceBand, ...] = ()
    tfr_base: Literal["none", "whole", "above_exempt"] | None = None
    mission_duration: bool = False
    habitual_discount: Decimal = Field(default=Decimal(0), ge=Decimal(0), le=Decimal(1))
    long_mission_discount: Decimal = Field(
        default=Decimal(0), ge=Decimal(0), le=Decimal(1)
    )
    night_allowance: TimeSeries | None = None
    night_from_hours: Decimal = Decimal(18)
    quotas: TravelQuotas | None = None
    minimum_share: Decimal | None = Field(default=None, gt=Decimal(0), le=Decimal(1))
    minimum_divisor: Decimal = Field(default=Decimal(26), gt=Decimal(0))
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _bands_or_quotas(self) -> Self:
        kinds = (
            bool(self.bands),
            self.quotas is not None,
            self.minimum_share is not None,
        )
        if sum(kinds) != 1:
            msg = (
                "a travel allowance has bands of hours, quotas or a share of "
                "the daily minimum, exactly one"
            )
            raise ValueError(msg)
        return self

    def band_of(self, hours: Decimal) -> TravelAllowanceBand | None:
        """Return the span of ``hours`` away.

        Returns:
            The band holding ``hours``, ``None`` below the first.
        """
        return next((b for b in self.bands if b.holds(hours)), None)
