"""Validity period and time series primitives."""

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.engine.primitives import validate_open_sequence
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


class ValidityPeriod(BaseModel):
    """A single time-bounded value within a TimeSeries.

    ``provenance`` overrides the provenance inherited from the owning domain
    object when the value in this period came from a different source page or
    was extracted differently.  ``None`` means "inherit from the owner".
    """

    model_config = ConfigDict(extra="forbid")

    valid_from: date
    valid_until: date | None
    value: Decimal
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_dates(self) -> Self:
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            msg = (
                f"valid_until ({self.valid_until}) must be strictly after "
                f"valid_from ({self.valid_from})"
            )
            raise ValueError(msg)
        return self


class TimeSeries(BaseModel):
    """Ordered, contiguous, open-ended sequence of ValidityPeriod objects."""

    model_config = ConfigDict(extra="forbid")

    periods: list[ValidityPeriod]

    @model_validator(mode="after")
    def _check_series(self) -> Self:
        validate_open_sequence(
            self.periods,
            lambda p: p.valid_from,
            lambda p: p.valid_until,
            "TimeSeries periods",
        )
        return self

    def value_at(self, day: date) -> Decimal:
        """Return the value in effect on day.

        Returns:
            The Decimal value in effect on the given date.

        Raises:
            ValueError: If the date precedes the start of the series.
        """
        for period in self.periods:
            if period.valid_from <= day and (
                period.valid_until is None or day < period.valid_until
            ):
                return period.value
        msg = f"no value for {day}: series starts on {self.periods[0].valid_from}"
        raise ValueError(msg)
