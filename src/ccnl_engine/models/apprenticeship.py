"""Apprenticeship rule models.

CCNL contracts define apprenticeship salary rules in one of two ways:

* **Percentage** (``type="percentage"``): the apprentice's gross salary is a
  percentage of the destination level's full salary. The percentage may step
  up at defined month thresholds.
* **Under-classification** (``type="under_classification"``): the apprentice
  is paid at a lower classification level whose code is listed in the contract
  table. The pay level may change at defined month thresholds.

Use :data:`Apprenticeship` as the annotation; pydantic selects the correct
variant via the ``"type"`` discriminator.
"""

from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


class ApprenticeshipPeriod(BaseModel):
    """A single time-bounded entry in a percentage-based apprenticeship table.

    Attributes:
        months_from: Inclusive lower bound (months elapsed since hire).
        months_until: Exclusive upper bound; ``None`` means open-ended
            (applies until the apprenticeship ends).
        percentage: Fraction of the destination level's salary to pay,
            e.g. ``Decimal("0.80")`` for 80 %.
    """

    months_from: int
    months_until: int | None
    percentage: Decimal

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        """Ensure months_until, when set, is strictly greater than months_from."""
        if self.months_until is not None and self.months_until <= self.months_from:
            msg = (
                f"months_until ({self.months_until}) must be strictly greater "
                f"than months_from ({self.months_from})"
            )
            raise ValueError(msg)
        return self


class UnderClassificationPeriod(BaseModel):
    """A single time-bounded entry in an under-classification apprenticeship table.

    Attributes:
        months_from: Inclusive lower bound (months elapsed since hire).
        months_until: Exclusive upper bound; ``None`` means open-ended.
        pay_level_code: Code of the CCNL level at which the apprentice is
            paid during this period. Must exist in the parent CCNL's levels.
    """

    months_from: int
    months_until: int | None
    pay_level_code: str

    @model_validator(mode="after")
    def _check_bounds(self) -> Self:
        """Ensure months_until, when set, is strictly greater than months_from."""
        if self.months_until is not None and self.months_until <= self.months_from:
            msg = (
                f"months_until ({self.months_until}) must be strictly greater "
                f"than months_from ({self.months_from})"
            )
            raise ValueError(msg)
        return self


class ApprenticeshipPercentage(BaseModel):
    """Percentage-based apprenticeship rule.

    Attributes:
        type: Discriminator literal — always ``"percentage"``.
        destination_level: Code of the CCNL level the apprentice is training
            towards (used to look up the base salary).
        periods: Ordered, contiguous period entries. The last entry must be
            open-ended (``months_until=None``).
    """

    type: Literal["percentage"]
    destination_level: str
    periods: list[ApprenticeshipPeriod]

    @model_validator(mode="after")
    def _check_periods(self) -> Self:
        """Validate that periods are non-empty and contiguous."""
        p = self.periods
        if not p:
            msg = "apprenticeship periods must not be empty"
            raise ValueError(msg)
        for i in range(len(p) - 1):
            if p[i].months_until is None:
                msg = (
                    f"only the last period may have months_until=None "
                    f"(period {i} is not the last)"
                )
                raise ValueError(msg)
            if p[i].months_until != p[i + 1].months_from:
                msg = (
                    f"gap between period {i} (months_until={p[i].months_until}) "
                    f"and period {i + 1} (months_from={p[i + 1].months_from})"
                )
                raise ValueError(msg)
        if p[-1].months_until is not None:
            msg = "last apprenticeship period must be open-ended (months_until=None)"
            raise ValueError(msg)
        return self


class ApprenticeshipUnderClassification(BaseModel):
    """Under-classification apprenticeship rule.

    Attributes:
        type: Discriminator literal — always ``"under_classification"``.
        destination_level: Code of the CCNL level the apprentice is training
            towards.
        periods: Ordered, contiguous period entries. The last entry must be
            open-ended (``months_until=None``).
    """

    type: Literal["under_classification"]
    destination_level: str
    periods: list[UnderClassificationPeriod]

    @model_validator(mode="after")
    def _check_periods(self) -> Self:
        """Validate that periods are non-empty and contiguous."""
        p = self.periods
        if not p:
            msg = "apprenticeship periods must not be empty"
            raise ValueError(msg)
        for i in range(len(p) - 1):
            if p[i].months_until is None:
                msg = (
                    f"only the last period may have months_until=None "
                    f"(period {i} is not the last)"
                )
                raise ValueError(msg)
            if p[i].months_until != p[i + 1].months_from:
                msg = (
                    f"gap between period {i} (months_until={p[i].months_until}) "
                    f"and period {i + 1} (months_from={p[i + 1].months_from})"
                )
                raise ValueError(msg)
        if p[-1].months_until is not None:
            msg = "last apprenticeship period must be open-ended (months_until=None)"
            raise ValueError(msg)
        return self


#: Discriminated union of all supported apprenticeship rule types.
Apprenticeship = Annotated[
    ApprenticeshipPercentage | ApprenticeshipUnderClassification,
    Field(discriminator="type"),
]
