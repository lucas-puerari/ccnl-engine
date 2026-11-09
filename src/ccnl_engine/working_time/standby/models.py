"""The CCNL standby (reperibilità) rates and bands."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance


class StandbyRates(BaseModel):
    """Standby pay (indennità di reperibilità) of one band of levels.

    Attributes:
        worked_day: Day of 16 hours on a working day; the hourly rate is it
            divided by :attr:`StandbyRules.hourly_divisor`.
        rest_day: Day of 24 hours on a rest day.
        holiday: Day of 24 hours on a public holiday.
        week: Week of 6 days.
        week_holiday: Week of 6 days with a public holiday.
        week_holiday_rest_day: Week of 6 days with a public holiday and a
            rest day.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    worked_day: TimeSeries
    rest_day: TimeSeries
    holiday: TimeSeries
    week: TimeSeries
    week_holiday: TimeSeries
    week_holiday_rest_day: TimeSeries


class StandbyBand(BaseModel):
    """The levels that share one set of standby rates.

    Attributes:
        levels: Level codes of the band.
        rates: Their rates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    levels: tuple[str, ...] = Field(min_length=1)
    rates: StandbyRates


class StandbyRules(BaseModel):
    """CCNL standby pay (reperibilità): rates per band, fee per call.

    Attributes:
        bands: Bands of levels with their rates; a level in none is not
            entitled.
        hourly_divisor: Hours the ``worked_day`` rate is divided by for an
            hour of standby.
        call_fee: Amount for each call followed by an intervention.
        in_tfr_base: Whether the standby pay enters the TFR base (art. 2120
            c. 2 c.c. lets the CCNL exclude it).
        turn_rate: Flat rate for a complete on-call turn, where the CCNL
            specifies turns rather than separate day and week rates.
        turn_hours: Duration of a complete turn in hours.
        minimum_turn_hours: Minimum allowed shorter turn in hours.
        short_turn_premium: Extra share paid on shorter turns pro rata.
        provenance: Source and status of the rules.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bands: tuple[StandbyBand, ...] = ()
    hourly_divisor: Decimal | None = Field(default=None, gt=Decimal(0))
    call_fee: TimeSeries | None = None
    in_tfr_base: bool
    turn_rate: TimeSeries | None = None
    turn_hours: Decimal | None = Field(default=None, gt=Decimal(0))
    minimum_turn_hours: Decimal | None = Field(default=None, gt=Decimal(0))
    short_turn_premium: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def require_band_rates_without_turn_rate(self) -> Self:
        """Require all legacy band inputs when there is no complete-turn rate.

        Returns:
            The validated standby rules.

        Raises:
            ValueError: If a non-turn ruleset lacks a band, divisor or call fee.
        """
        if self.turn_rate is None and (
            not self.bands or self.hourly_divisor is None or self.call_fee is None
        ):
            msg = (
                "standby rules without turn_rate require bands, "
                "hourly_divisor and call_fee"
            )
            raise ValueError(msg)
        return self

    def band_of(self, level_code: str) -> StandbyBand | None:
        """Return the band of a level.

        Returns:
            The band listing ``level_code``, ``None`` when none does.
        """
        return next((b for b in self.bands if level_code in b.levels), None)
