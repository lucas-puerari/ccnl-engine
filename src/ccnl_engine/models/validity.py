"""Validity period and time series primitives.

Every economic value in ccnl-engine is represented as a :class:`TimeSeries`:
an ordered, contiguous sequence of :class:`ValidityPeriod` objects. Each period
carries a scalar ``value`` (always a :class:`~decimal.Decimal`) that is valid
from ``valid_from`` (inclusive) until ``valid_until`` (exclusive). The last
period in a series is open-ended (``valid_until=None``).
"""

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator


class ValidityPeriod(BaseModel):
    """A single time-bounded value within a :class:`TimeSeries`.

    Attributes:
        valid_from: First day (inclusive) for which the value applies.
        valid_until: First day (exclusive) after which the value no longer
            applies. ``None`` means the period is open-ended.
        value: The scalar value, always stored as :class:`~decimal.Decimal`.
            JSON sources must encode this as a string (e.g. ``"1257.46"``)
            to avoid floating-point precision loss.
    """

    valid_from: date
    valid_until: date | None
    value: Decimal

    @model_validator(mode="after")
    def _check_dates(self) -> Self:
        """Ensure valid_until, when set, is strictly after valid_from."""
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            msg = (
                f"valid_until ({self.valid_until}) must be strictly after "
                f"valid_from ({self.valid_from})"
            )
            raise ValueError(msg)
        return self


class TimeSeries(BaseModel):
    """An ordered, contiguous, open-ended sequence of :class:`ValidityPeriod` objects.

    Invariants enforced at construction time:

    1. At least one period.
    2. Periods are sorted ascending by ``valid_from``.
    3. No gaps: each period's ``valid_until`` equals the next period's
       ``valid_from``.
    4. Only the last period may have ``valid_until=None``.
    5. The last period *must* have ``valid_until=None`` (open-ended).
    """

    periods: list[ValidityPeriod]

    @model_validator(mode="after")
    def _check_series(self) -> Self:
        """Validate the period sequence."""
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
        """Return the value in effect on *day*.

        Args:
            day: The reference date.

        Returns:
            The ``value`` of the :class:`ValidityPeriod` that contains *day*.

        Raises:
            ValueError: If *day* precedes the start of the series.
        """
        for period in self.periods:
            if period.valid_from <= day and (
                period.valid_until is None or day < period.valid_until
            ):
                return period.value
        msg = f"no value for {day}: series starts on {self.periods[0].valid_from}"
        raise ValueError(msg)
