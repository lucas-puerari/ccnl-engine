"""National holidays with civil effects, as the bundle lists them."""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["NationalHoliday", "NationalHolidays", "easter_sunday"]

#: The day of a holiday: ``MM-DD`` or the Monday after Easter.
EASTER_MONDAY = "easter_monday"
_MONTH_DAY = re.compile(r"(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])")


def easter_sunday(year: int) -> date:
    """Return Easter Sunday of ``year`` in the Gregorian calendar.

    The anonymous Gregorian algorithm (Meeus, Astronomical Algorithms).

    Returns:
        The date of Easter Sunday.
    """
    a, b, c = year % 19, year // 100, year % 100
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month, day = divmod(h + ell - 7 * m + 114, 31)
    return date(year, month, day + 1)


class NationalHoliday(BaseModel):
    """One national holiday.

    Attributes:
        day: ``MM-DD``, or ``easter_monday`` for the Monday after Easter.
        name: Italian name of the holiday.
        valid_from: First date the day is a holiday; ``None`` when it is
            one in every year the bundle covers.
        provenance: The act that makes it a holiday.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day: str
    name: str = Field(min_length=1)
    valid_from: date | None = None
    provenance: RuleProvenance

    @field_validator("day")
    @classmethod
    def _check_day(cls, value: str) -> str:
        if value != EASTER_MONDAY and not _MONTH_DAY.fullmatch(value):
            msg = f"holiday day {value!r} is neither MM-DD nor {EASTER_MONDAY!r}"
            raise ValueError(msg)
        return value

    def on(self, year: int) -> date | None:
        """Return the date of the holiday in ``year``.

        Returns:
            The date; ``None`` before :attr:`valid_from`.
        """
        if self.day == EASTER_MONDAY:
            found = easter_sunday(year) + timedelta(days=1)
        else:
            month, day = (int(part) for part in self.day.split("-"))
            found = date(year, month, day)
        if self.valid_from is not None and found < self.valid_from:
            return None
        return found


class NationalHolidays(BaseModel):
    """The national holidays with civil effects, besides the Sundays.

    Attributes:
        schema_version: Version of the file format.
        description: What the list holds.
        suppressed_provenance: The act that suppressed the days the
            founding law still lists.
        holidays: The holidays, one per day.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    description: str = ""
    suppressed_provenance: RuleProvenance | None = None
    holidays: tuple[NationalHoliday, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_unique(self) -> Self:
        days = [h.day for h in self.holidays]
        if len(set(days)) != len(days):
            msg = f"national holidays list a day twice: {days}"
            raise ValueError(msg)
        return self

    def in_year(self, year: int) -> frozenset[date]:
        """Return the holidays of ``year``.

        Returns:
            Their dates, Sundays not included.
        """
        found = (h.on(year) for h in self.holidays)
        return frozenset(day for day in found if day is not None)

    def between(self, first: date, last: date) -> frozenset[date]:
        """Return the holidays from ``first`` to ``last``, both included.

        Returns:
            Their dates, Sundays not included.
        """
        found = (d for y in range(first.year, last.year + 1) for d in self.in_year(y))
        return frozenset(d for d in found if first <= d <= last)

    def is_holiday(self, day: date) -> bool:
        """Return whether ``day`` is a national holiday.

        Returns:
            ``True`` for a holiday of the list, Sundays not included.
        """
        return day in self.in_year(day.year)
