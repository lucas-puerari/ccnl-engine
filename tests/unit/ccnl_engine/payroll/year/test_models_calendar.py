"""Unit tests for WorkCalendar construction and validation."""

from __future__ import annotations

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.accrual.models_extra_month_schedule import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.payroll.year.models_calendar import WorkCalendar

_YEAR = 2026


class TestWorkCalendar:
    """WorkCalendar stores year and extra-month schedule."""

    def test_default_extra_months_empty(self) -> None:
        """WorkCalendar with no extra months has an empty tuple."""
        cal = WorkCalendar(year=_YEAR)
        assert cal.year == _YEAR
        assert cal.extra_months == ()

    def test_explicit_extra_months(self) -> None:
        """Explicitly supplied extra months are stored."""
        sched = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        cal = WorkCalendar(year=_YEAR, extra_months=(sched,))
        assert len(cal.extra_months) == 1
        assert cal.extra_months[0] is sched

    def test_from_additional_months_13(self) -> None:
        """from_additional_months(13) produces one extra schedule in December."""
        cal = WorkCalendar.from_additional_months(_YEAR, 13)
        assert len(cal.extra_months) == 1
        assert cal.extra_months[0].payment_month == 12
        assert cal.extra_months[0].name == "tredicesima"

    def test_from_additional_months_14(self) -> None:
        """from_additional_months(14) yields tredicesima in Dec, fourteenth in Jun."""
        cal = WorkCalendar.from_additional_months(_YEAR, 14)
        assert len(cal.extra_months) == 2
        thirteenth = cal.extra_months[0]
        fourteenth = cal.extra_months[1]
        assert thirteenth.payment_month == 12
        assert fourteenth.payment_month == 6

    def test_from_additional_months_12(self) -> None:
        """from_additional_months(12) produces no extra schedules."""
        cal = WorkCalendar.from_additional_months(_YEAR, 12)
        assert cal.extra_months == ()

    def test_from_additional_months_below_12_raises(self) -> None:
        """from_additional_months(11) raises ValueError — minimum is 12."""
        with pytest.raises(InvalidInputError, match="additional_months"):
            WorkCalendar.from_additional_months(_YEAR, 11)

    def test_frozen(self) -> None:
        """WorkCalendar is immutable."""
        cal = WorkCalendar(year=_YEAR)
        with pytest.raises(AttributeError):
            cal.year = 2025  # type: ignore[misc]

    def test_year_below_1970_raises(self) -> None:
        """Year < 1970 raises ValueError."""
        with pytest.raises(InvalidInputError, match="1970"):
            WorkCalendar(year=1969)

    def test_duplicate_extra_month_raises(self) -> None:
        """Two identical name+payment_month schedules raise ValueError."""
        sched = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        with pytest.raises(InvalidInputError, match="duplicate"):
            WorkCalendar(year=_YEAR, extra_months=(sched, sched))
