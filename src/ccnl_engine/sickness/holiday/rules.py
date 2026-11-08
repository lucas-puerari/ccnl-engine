"""The national holidays a CCNL holiday target in a sickness covers."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.calendar.holiday.models import NationalHolidays
    from ccnl_engine.employer.inputs import EmployerProfile
    from ccnl_engine.sickness.holiday.models import SicknessHoliday
    from ccnl_engine.sickness.integration.models import SicknessRules

__all__ = ["covered_holidays", "covered_target_holidays", "gross_holiday_boundary"]

_SUNDAY = 6


def gross_holiday_boundary(
    target: SicknessHoliday | None, holidays: frozenset[date], day: date, previous: date
) -> bool:
    """Keep gross-basis holiday pay separate from adjacent ordinary sick pay.

    Returns:
        Whether a segment must end at this day boundary.
    """
    return bool(
        target and target.gross_basis and (day in holidays or previous in holidays)
    )


def covered_holidays(
    rules: SicknessRules,
    calendar: NationalHolidays,
    year: int,
    employer: EmployerProfile | None = None,
) -> frozenset[date]:
    """Return the holidays the target of ``rules`` applies on.

    The weekday holidays of ``year`` and of the two years before, the span
    an episode of the run can reach, but those the clause leaves out; a
    holiday on a Sunday is paid by its own quota (L. 260/1949 art. 5).

    Returns:
        Their dates; none without a holiday target.
    """
    return covered_target_holidays(rules.holiday, calendar, year, employer)


def covered_target_holidays(
    target: SicknessHoliday | None,
    calendar: NationalHolidays,
    year: int,
    employer: EmployerProfile | None = None,
) -> frozenset[date]:
    """Return the weekday national holidays eligible for this target.

    Returns:
        The covered dates, or none when no holiday clause is present.
    """
    if target is None:
        return frozenset()
    covered = calendar.model_copy(
        update={
            "holidays": tuple(
                h for h in calendar.holidays if h.day not in target.excluded_days
            )
        }
    )
    days = set().union(*(covered.in_year(y) for y in range(year - 2, year + 1)))
    patron = None if employer is None else employer.patron_saint_day
    if target.includes_patron_saint and patron is not None:
        month, day = (int(part) for part in patron.split("-"))
        for y in range(year - 2, year + 1):
            try:
                days.add(date(y, month, day))
            except ValueError:  # 29 February in a non-leap year
                continue
    return frozenset(day for day in days if day.weekday() != _SUNDAY)
