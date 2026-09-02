"""Apprenticeship rule models.

A CCNL carries a list of *tracks*. Each track applies to one or more
destination levels and is either percentage-based (``type="percentage"``)
or under-classification (``type="under_classification"``). Use the
:data:`ApprenticeshipTrack` union annotation; Pydantic selects the variant
via the ``"type"`` discriminator.
"""

from collections.abc import Sequence
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_ONE = Decimal(1)
_ZERO = Decimal(0)


class ApprenticeshipPeriod(BaseModel):
    """A single time-bounded entry in a percentage-based apprenticeship table."""

    model_config = ConfigDict(extra="forbid")

    months_from: int = Field(ge=0)
    months_until: int | None
    percentage: Decimal

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        _check_month_bounds(self.months_from, self.months_until)
        if not (_ZERO < self.percentage <= _ONE):
            msg = f"percentage must be in (0, 1], got {self.percentage}"
            raise ValueError(msg)
        return self


class UnderClassificationPeriod(BaseModel):
    """A single time-bounded entry in an under-classification apprenticeship table.

    ``levels_below`` is the number of classification levels (by ``order``)
    below the destination level at which the apprentice is paid; ``0`` means
    the destination level itself. ``midpoint_to_destination`` pays the
    arithmetic mean between that level and the destination level.
    """

    model_config = ConfigDict(extra="forbid")

    months_from: int = Field(ge=0)
    months_until: int | None
    levels_below: int = Field(ge=0)
    midpoint_to_destination: bool = False

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        _check_month_bounds(self.months_from, self.months_until)
        return self


def _check_month_bounds(months_from: int, months_until: int | None) -> None:
    if months_until is not None and months_until <= months_from:
        msg = (
            f"months_until ({months_until}) must be strictly greater "
            f"than months_from ({months_from})"
        )
        raise ValueError(msg)


def _validate_period_sequence(
    periods: Sequence[ApprenticeshipPeriod | UnderClassificationPeriod],
) -> None:
    if not periods:
        msg = "apprenticeship periods must not be empty"
        raise ValueError(msg)
    if periods[0].months_from != 0:
        msg = (
            f"first apprenticeship period must start at months_from=0, "
            f"got {periods[0].months_from}"
        )
        raise ValueError(msg)
    for i in range(len(periods) - 1):
        if periods[i].months_until is None:
            msg = (
                f"only the last period may have months_until=None "
                f"(period {i} is not the last)"
            )
            raise ValueError(msg)
        if periods[i].months_until != periods[i + 1].months_from:
            msg = (
                f"gap between period {i} (months_until={periods[i].months_until}) "
                f"and period {i + 1} (months_from={periods[i + 1].months_from})"
            )
            raise ValueError(msg)
    if periods[-1].months_until is not None:
        msg = "last apprenticeship period must be open-ended (months_until=None)"
        raise ValueError(msg)


def _validate_destination_levels(levels: Sequence[str]) -> None:
    if not levels:
        msg = "destination_levels must not be empty"
        raise ValueError(msg)
    if len(levels) != len(set(levels)):
        msg = f"destination_levels must be unique, got: {list(levels)}"
        raise ValueError(msg)


class ApprenticeshipPercentage(BaseModel):
    """Percentage-based apprenticeship track."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["percentage"] = "percentage"
    name: str
    destination_levels: list[str]
    periods: list[ApprenticeshipPeriod]

    @model_validator(mode="after")
    def _check(self) -> Self:
        _validate_destination_levels(self.destination_levels)
        _validate_period_sequence(self.periods)
        return self


class ApprenticeshipUnderClassification(BaseModel):
    """Under-classification apprenticeship track."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["under_classification"] = "under_classification"
    name: str
    destination_levels: list[str]
    periods: list[UnderClassificationPeriod]

    @model_validator(mode="after")
    def _check(self) -> Self:
        _validate_destination_levels(self.destination_levels)
        _validate_period_sequence(self.periods)
        return self


#: Discriminated union of all supported apprenticeship track types.
ApprenticeshipTrack = Annotated[
    ApprenticeshipPercentage | ApprenticeshipUnderClassification,
    Field(discriminator="type"),
]
