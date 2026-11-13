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


#: Code of the employer's local patron saint holiday in a clause's list.
PATRON = "patron"


def patron_day(
    clause: SundayHolidayPay | None,
    patron: str | None,
    year: int,
    dated: list[tuple[NationalHoliday, date | None]],
    rest_day: int,
) -> date | None:
    """Return the patron saint holiday when the clause pays its coincidence.

    Logistica Confetra art. 60 c. 1 b) 12) lists the patron of the place of
    work among the holidays whose fall on a Saturday, a Sunday or another
    holiday art. 60 c. 2 pays with a further day.

    Returns:
        The date of ``EmployerProfile.patron_saint_day`` in ``year`` when the
        clause lists ``patron`` and the day falls on the rest day, or on a
        Saturday or another national holiday under the clause's triggers;
        ``None`` otherwise or when the patron day is not stated.
    """
    if clause is None or PATRON not in clause.holidays or patron is None:
        return None
    month, day_of_month = (int(part) for part in patron.split("-"))
    day = date(year, month, day_of_month)
    if day.weekday() == rest_day:
        return day
    on_saturday = clause.on_saturday and day.weekday() == 5
    coincident = clause.on_coincident_holiday and any(
        other_day == day for _, other_day in dated
    )
    return day if on_saturday or coincident else None
