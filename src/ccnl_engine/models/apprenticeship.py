"""Apprenticeship rule models.

Two variants: percentage-based (``type="percentage"``) and
under-classification (``type="under_classification"``). Use the
:data:`Apprenticeship` union annotation; Pydantic selects the variant
via the ``"type"`` discriminator.
"""

from collections.abc import Sequence
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


class ApprenticeshipPeriod(BaseModel):
    """A single time-bounded entry in a percentage-based apprenticeship table."""

    months_from: int
    months_until: int | None
    percentage: Decimal

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        if self.months_until is not None and self.months_until <= self.months_from:
            msg = (
                f"months_until ({self.months_until}) must be strictly greater "
                f"than months_from ({self.months_from})"
            )
            raise ValueError(msg)
        return self


class UnderClassificationPeriod(BaseModel):
    """A single time-bounded entry in an under-classification apprenticeship table."""

    months_from: int
    months_until: int | None
    pay_level_code: str

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        if self.months_until is not None and self.months_until <= self.months_from:
            msg = (
                f"months_until ({self.months_until}) must be strictly greater "
                f"than months_from ({self.months_from})"
            )
            raise ValueError(msg)
        return self


def _validate_period_sequence(
    periods: Sequence[ApprenticeshipPeriod | UnderClassificationPeriod],
) -> None:
    if not periods:
        msg = "apprenticeship periods must not be empty"
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


class ApprenticeshipPercentage(BaseModel):
    """Percentage-based apprenticeship rule."""

    type: Literal["percentage"] = "percentage"
    destination_level: str
    periods: list[ApprenticeshipPeriod]

    @model_validator(mode="after")
    def _check_periods(self) -> Self:
        _validate_period_sequence(self.periods)
        return self


class ApprenticeshipUnderClassification(BaseModel):
    """Under-classification apprenticeship rule."""

    type: Literal["under_classification"] = "under_classification"
    destination_level: str
    periods: list[UnderClassificationPeriod]

    @model_validator(mode="after")
    def _check_periods(self) -> Self:
        _validate_period_sequence(self.periods)
        return self


#: Discriminated union of all supported apprenticeship rule types.
Apprenticeship = Annotated[
    ApprenticeshipPercentage | ApprenticeshipUnderClassification,
    Field(discriminator="type"),
]
