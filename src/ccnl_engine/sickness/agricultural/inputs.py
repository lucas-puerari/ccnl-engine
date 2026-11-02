"""The days in the agricultural lists of an operaio agricolo a tempo determinato."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.validators import require_int

__all__ = ["AgriculturalDays"]

_FEATURE = "sickness"


@dataclass(frozen=True, slots=True)
class AgriculturalDays:
    """The days an operaio agricolo a tempo determinato is registered for.

    INPS pays the sickness for as many days as the registration in the
    elenchi nominativi, at most 180 a year, with 51 days of the year before
    or 51 of the current year before the illness (then at most 30).

    Attributes:
        previous_year: Days of registration in the elenchi of the year
            before the illness.
        current_year: Days of registration of the year of the illness,
            before its first day.

    Raises:
        InvalidInputError: When a count is not an int in [0, 366].
    """

    previous_year: int
    current_year: int

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("previous_year", "current_year"):
            require_int(
                getattr(self, name),
                f"AgriculturalDays.{name}",
                feature=_FEATURE,
                minimum=0,
                maximum=366,
            )
