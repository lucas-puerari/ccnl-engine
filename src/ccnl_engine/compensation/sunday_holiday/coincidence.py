"""Additional national-holiday dates paid by a CCNL coincidence clause."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.calendar.holiday.models import NationalHoliday
    from ccnl_engine.compensation.sunday_holiday.models import SundayHolidayPay


def extra_day(
    clause: SundayHolidayPay | None,
    holiday: NationalHoliday,
    day: date,
    dated: list[tuple[NationalHoliday, date | None]],
    rest_day: int,
) -> bool:
    """Return whether a clause additionally pays this Saturday or overlap.

    Returns:
        False on a non-Sunday compensatory rest day when the clause excludes
        it; otherwise whether a listed holiday falls on a Saturday or on
        another national-calendar holiday.
    """
    if clause is None or holiday.day not in clause.holidays:
        return False
    if (
        clause.exclude_compensatory_rest_day
        and day.weekday() != 6
        and day.weekday() == rest_day
    ):
        return False
    return (clause.on_saturday and day.weekday() == 5) or (
        clause.on_coincident_holiday
        and any(other_day == day and other is not holiday for other, other_day in dated)
    )
