"""Unit tests for calculate_year() and WorkCalendar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import ExtraMonthSchedule, WorkCalendar
from ccnl_engine.payroll.domain.events import AbsenceEvent

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


class TestExtraMonthSchedule:
    """ExtraMonthSchedule stores name and payment month."""

    def test_stored_fields(self) -> None:
        """Name and payment_month are stored and retrievable."""
        s = ExtraMonthSchedule(name="tredicesima", payment_month=12)
        assert s.name == "tredicesima"
        assert s.payment_month == 12

    def test_frozen(self) -> None:
        """ExtraMonthSchedule is immutable."""
        s = ExtraMonthSchedule(name="tredicesima", payment_month=12)
        with pytest.raises(AttributeError):
            s.payment_month = 6  # type: ignore[misc]


class TestWorkCalendar:
    """WorkCalendar stores year and extra-month schedule."""

    def test_default_extra_months_empty(self) -> None:
        """WorkCalendar with no extra months has an empty tuple."""
        cal = WorkCalendar(year=_YEAR)
        assert cal.year == _YEAR
        assert cal.extra_months == ()

    def test_explicit_extra_months(self) -> None:
        """Explicitly supplied extra months are stored."""
        sched = ExtraMonthSchedule(name="tredicesima", payment_month=12)
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
        """from_additional_months(14) produces two extra schedules."""
        cal = WorkCalendar.from_additional_months(_YEAR, 14)
        assert len(cal.extra_months) == 2

    def test_from_additional_months_12(self) -> None:
        """from_additional_months(12) produces no extra schedules."""
        cal = WorkCalendar.from_additional_months(_YEAR, 12)
        assert cal.extra_months == ()

    def test_from_additional_months_below_12(self) -> None:
        """from_additional_months(11) also produces no extra schedules."""
        cal = WorkCalendar.from_additional_months(_YEAR, 11)
        assert cal.extra_months == ()

    def test_frozen(self) -> None:
        """WorkCalendar is immutable."""
        cal = WorkCalendar(year=_YEAR)
        with pytest.raises(AttributeError):
            cal.year = 2025  # type: ignore[misc]


class TestYearCalculationResult:
    """YearCalculationResult stores period results and aggregated totals."""

    def test_frozen(self) -> None:
        """YearCalculationResult is immutable."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        with pytest.raises(AttributeError):
            result.year = 2025  # type: ignore[misc]

    def test_year_stored(self) -> None:
        """Year matches the requested year."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        assert result.year == _YEAR

    def test_calendar_year_mismatch_raises(self) -> None:
        """calendar.year differing from year raises ValueError."""
        cal = WorkCalendar(year=2025)
        with pytest.raises(ValueError, match=r"calendar\.year=2025"):
            calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)


class TestCalculateYear:
    """calculate_year() chains calculate_period across all 12 periods."""

    def test_produces_12_period_results(self) -> None:
        """Full-year run produces exactly 12 period results."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        assert len(result.period_results) == 12

    def test_annual_gross_equals_sum_of_periods(self) -> None:
        """annual_gross is the exact sum of all period_gross values."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        expected = sum((r.period_gross for r in result.period_results), Decimal(0))
        assert result.annual_gross == expected

    def test_annual_net_equals_sum_of_periods(self) -> None:
        """annual_net is the exact sum of all period_net values."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        expected = sum((r.period_net for r in result.period_results), Decimal(0))
        assert result.annual_net == expected

    def test_annual_employer_cost_equals_sum_of_periods(self) -> None:
        """annual_employer_cost is the exact sum of all period_employer_cost values."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        expected = sum(
            (r.period_employer_cost for r in result.period_results), Decimal(0)
        )
        assert result.annual_employer_cost == expected

    def test_state_threaded_across_periods(self) -> None:
        """Closing state of period N is the opening state of period N+1."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        for i in range(1, 12):
            prev = result.period_results[i - 1]
            curr = result.period_results[i]
            assert curr.closing_state.months_closed == (
                prev.closing_state.months_closed + 1
            )

    def test_months_closed_reaches_12(self) -> None:
        """After 12 periods months_closed equals 12."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        assert result.period_results[-1].closing_state.months_closed == 12

    def test_period_ids_are_in_order(self) -> None:
        """Period results are ordered January to December."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        for i, pr in enumerate(result.period_results, start=1):
            assert pr.period_id.month == i
            assert pr.period_id.year == _YEAR

    def test_explicit_contract_type(self) -> None:
        """An explicitly supplied contract_type is used instead of the default."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            calendar=cal,
            contract_type=Permanent(),
        )
        assert len(result.period_results) == 12

    def test_period_events_injected(self) -> None:
        """Events supplied in period_events are applied to the correct period."""
        cal = WorkCalendar(year=_YEAR)
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            calendar=cal,
            period_events={3: (absence,)},
        )
        # March gross must be lower than January gross (same base minus absence)
        jan_gross = result.period_results[0].period_gross
        mar_gross = result.period_results[2].period_gross
        assert mar_gross < jan_gross

    def test_all_period_gross_values_positive(self) -> None:
        """With no events all 12 period_gross values are positive."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        for r in result.period_results:
            assert r.period_gross > Decimal(0)

    def test_gross_ytd_accumulates_correctly(self) -> None:
        """gross_ytd in December closing state equals annual_gross."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        dec_state = result.period_results[-1].closing_state
        assert dec_state.gross_ytd == result.annual_gross
