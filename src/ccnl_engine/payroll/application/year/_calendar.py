"""Standard payroll calendar of a CCNL and the effective calendar of a year."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.extra_month_entitlement import ExtraMonthEntitlement

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride

__all__ = ["effective_calendar", "standard_calendar"]


def standard_calendar(ccnl: CCNL, year: int, as_of: date) -> WorkCalendar:
    """Return the calendar the CCNL grants for ``year``.

    Args:
        ccnl: The contract, whose ``additional_months`` sets the extra months.
        year: Tax year of the calendar.
        as_of: Date at which ``additional_months`` is read.

    Returns:
        :meth:`WorkCalendar.from_additional_months` of the CCNL entitlement,
        with the default payment months.
    """
    entitlement = ExtraMonthEntitlement.of(
        ccnl.parameters.additional_months.value_at(as_of)
    )
    return WorkCalendar.from_additional_months(year, entitlement)


def effective_calendar(
    ccnl: CCNL, year: int, override: CalendarOverride | None
) -> WorkCalendar:
    """Return the calendar a payroll year runs on.

    Args:
        ccnl: The contract of the year.
        year: Tax year.
        override: Validated replacement of the standard calendar, or ``None``.

    Returns:
        The standard calendar read on 1 January, or the override once
        :meth:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride.resolve`
        accepts it against that standard calendar.
    """
    standard = standard_calendar(ccnl, year, date(year, 1, 1))
    return standard if override is None else override.resolve(standard)
