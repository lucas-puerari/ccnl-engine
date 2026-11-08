"""The national holidays a CCNL holiday target in a sickness covers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.calendar.holiday.models import NationalHolidays
    from ccnl_engine.sickness.holiday.models import SicknessHoliday
    from ccnl_engine.sickness.integration.models import SicknessRules

__all__ = ["covered_holidays", "covered_target_holidays"]

_SUNDAY = 6


def covered_holidays(
    rules: SicknessRules, calendar: NationalHolidays, year: int
) -> frozenset[date]:
    """Return the holidays the target of ``rules`` applies on.

    The weekday holidays of ``year`` and of the two years before, the span
    an episode of the run can reach, but those the clause leaves out; a
    holiday on a Sunday is paid by its own quota (L. 260/1949 art. 5).

    Returns:
        Their dates; none without a holiday target.
    """
    return covered_target_holidays(rules.holiday, calendar, year)


def covered_target_holidays(
    target: SicknessHoliday | None, calendar: NationalHolidays, year: int
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
    days = frozenset().union(*(covered.in_year(y) for y in range(year - 2, year + 1)))
    return frozenset(day for day in days if day.weekday() != _SUNDAY)
