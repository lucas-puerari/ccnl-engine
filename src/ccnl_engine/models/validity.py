"""Validity period and time series primitives."""

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator


class ValidityPeriod(BaseModel):
    """A single time-bounded value within a TimeSeries."""

    valid_from: date
    valid_until: date | None
    value: Decimal

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

    periods: list[ValidityPeriod]

    @model_validator(mode="after")
    def _check_series(self) -> Self:
        p = self.periods
        if not p:
            msg = "TimeSeries must contain at least one ValidityPeriod"
            raise ValueError(msg)
        for i in range(len(p) - 1):
            if p[i].valid_until is None:
                msg = (
                    f"only the last period may have valid_until=None "
                    f"(period {i} of {len(p)} is not the last)"
                )
                raise ValueError(msg)
            if p[i].valid_until != p[i + 1].valid_from:
                msg = (
                    f"gap between period {i} (valid_until={p[i].valid_until}) "
                    f"and period {i + 1} (valid_from={p[i + 1].valid_from})"
                )
                raise ValueError(msg)
        if p[-1].valid_until is not None:
            msg = (
                f"last period must be open-ended (valid_until=None), "
                f"got valid_until={p[-1].valid_until}"
            )
            raise ValueError(msg)
        return self

    def value_at(self, day: date) -> Decimal:
        """Return the value in effect on day."""
        for period in self.periods:
            if period.valid_from <= day and (
                period.valid_until is None or day < period.valid_until
            ):
                return period.value
        msg = f"no value for {day}: series starts on {self.periods[0].valid_from}"
        raise ValueError(msg)
