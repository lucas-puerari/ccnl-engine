"""Which runs settle the extra months and which days do not accrue them."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.accrual.services_extra_month_qualification import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.employment.inputs_fact import EmploymentPeriod
from ccnl_engine.payroll.event.facade import AbsenceEvent, OvertimeEvent
from ccnl_engine.payroll.year.models_calendar import WorkCalendar

_YEAR = 2026


def test_employment_ending_in_a_later_year_settles_nothing() -> None:
    """An end in 2027 is not a termination of the 2026 payroll."""
    calendar = WorkCalendar.from_additional_months(_YEAR, 14)
    employment = EmploymentPeriod(date(2020, 1, 1), date(2027, 3, 31))
    assert termination_settlements(calendar, employment, frozenset()) == {}
    assert termination_settlements(calendar, None, frozenset()) == {}


def test_only_flagged_absence_days_are_collected() -> None:
    """Flagged absences count whatever run they belong to; others do not."""
    flagged = AbsenceEvent(
        event_date=date(_YEAR, 4, 1),
        hours=Decimal(8),
        hourly_rate=Decimal(10),
        suspends_accrual=True,
    )
    unflagged = AbsenceEvent(
        event_date=date(_YEAR, 5, 1), hours=Decimal(8), hourly_rate=Decimal(10)
    )
    overtime = OvertimeEvent(
        event_date=date(_YEAR, 5, 2), hours=Decimal(1), hourly_rate=Decimal(10)
    )
    days = non_accruing_days((unflagged, overtime, flagged))
    assert days == frozenset({date(_YEAR, 4, 1)})
