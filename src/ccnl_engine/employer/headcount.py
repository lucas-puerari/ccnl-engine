"""The headcount of the employer, the size its INPS tiers read."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.validators import require_int

__all__ = ["Headcount"]

_FEATURE = "employer"


@dataclass(frozen=True, slots=True)
class Headcount:
    """Employer headcount used to select INPS contribution tiers.

    At least one: the worker being paid is an employee of the employer.

    Attributes:
        value: Number of employees, ``>= 1``. For the CIGO 50-person
            threshold art. 13(2) requires the previous calendar year's
            average (or the closing count of the first month for a new
            employer). The engine uses this supplied value directly; it
            does not derive or validate that statutory average.

    Raises:
        InvalidInputError: When ``value`` is not an int or is below 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.value, "Headcount.value", feature=_FEATURE, minimum=1)
