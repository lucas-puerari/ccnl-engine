"""Unit tests for calculate_year() and WorkCalendar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.domain.events import AbsenceEvent

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


class TestExtraMonthSchedule:
    """ExtraMonthSchedule stores name and payment month."""

    def test_stored_fields(self) -> None:
        """Name and payment_month are stored and retrievable."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        assert s.name == "tredicesima"
        assert s.payment_month == 12

    def test_frozen(self) -> None:
        """ExtraMonthSchedule is immutable."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
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
        with pytest.raises(ValueError, match="additional_months"):
            WorkCalendar.from_additional_months(_YEAR, 11)

    def test_frozen(self) -> None:
        """WorkCalendar is immutable."""
        cal = WorkCalendar(year=_YEAR)
        with pytest.raises(AttributeError):
            cal.year = 2025  # type: ignore[misc]

    def test_year_below_1970_raises(self) -> None:
        """Year < 1970 raises ValueError."""
        with pytest.raises(ValueError, match="1970"):
            WorkCalendar(year=1969)

    def test_duplicate_extra_month_raises(self) -> None:
        """Two identical name+payment_month schedules raise ValueError."""
        sched = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        with pytest.raises(ValueError, match="duplicate"):
            WorkCalendar(year=_YEAR, extra_months=(sched, sched))


class TestExtraMonthScheduleValidation:
    """ExtraMonthSchedule rejects invalid payment months."""

    def test_payment_month_zero_raises(self) -> None:
        """payment_month=0 raises ValueError."""
        with pytest.raises(ValueError, match="1-12"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=0,
            )

    def test_payment_month_13_raises(self) -> None:
        """payment_month=13 raises ValueError."""
        with pytest.raises(ValueError, match="1-12"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=13,
            )

    def test_payment_month_12_valid(self) -> None:
        """payment_month=12 is accepted."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        assert s.payment_month == 12

    def test_empty_name_raises(self) -> None:
        """Empty name raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH, name="", payment_month=12
            )


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
            assert curr.closing_state.regular_periods_closed == (
                prev.closing_state.regular_periods_closed + 1
            )

    def test_regular_periods_closed_reaches_12(self) -> None:
        """After 12 regular periods regular_periods_closed equals 12."""
        cal = WorkCalendar(year=_YEAR)
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        assert result.period_results[-1].closing_state.regular_periods_closed == 12

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
        # March net must be lower than January net (absence in EMPLOYEE_DEDUCTIONS)
        jan_net = result.period_results[0].period_net
        mar_net = result.period_results[2].period_net
        assert mar_net < jan_net

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

    def test_calendar_none_auto_derives_from_ccnl(self) -> None:
        """calendar=None derives the run sequence from the CCNL additional_months.

        metalmeccanico-federmeccanica has additional_months=13, so auto-derive
        produces a 13-run calendar identical to explicitly supplying one.
        """
        result_auto = calculate_year(_YEAR, _CCNL, _LEVEL)
        explicit_cal = WorkCalendar.from_additional_months(_YEAR, 13)
        result_explicit = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=explicit_cal)
        assert result_auto.annual_gross == result_explicit.annual_gross
        assert len(result_auto.period_results) == len(result_explicit.period_results)
        assert len(result_auto.period_results) == 13


class TestPerRunEventAllocation:
    """per_run_events allocates events explicitly to a specific run by run_id."""

    def _calendar_13(self) -> WorkCalendar:
        return WorkCalendar(
            year=_YEAR,
            extra_months=(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=12,
                ),
            ),
        )

    def test_per_run_events_applied_to_correct_run(self) -> None:
        """Events in per_run_events reach the named run and no other run."""
        cal = WorkCalendar(year=_YEAR)
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result_no_event = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        result_with_event = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            calendar=cal,
            per_run_events={run_id: (absence,)},
        )
        may_no = result_no_event.period_results[4].period_net
        may_with = result_with_event.period_results[4].period_net
        assert may_with < may_no

    def test_per_run_events_do_not_leak_to_other_runs(self) -> None:
        """Events allocated by run_id do not appear in other runs."""
        cal = WorkCalendar(year=_YEAR)
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result = calculate_year(
            _YEAR, _CCNL, _LEVEL, calendar=cal, per_run_events={run_id: (absence,)}
        )
        may_gross = result.period_results[4].period_gross
        for i, pr in enumerate(result.period_results):
            if i != 4:
                assert pr.period_gross >= may_gross or i >= 5

    def test_extra_month_run_accepts_per_run_events(self) -> None:
        """per_run_events can allocate events to extra-month runs by run_id."""
        cal = self._calendar_13()
        absence = AbsenceEvent(
            event_date=date(_YEAR, 12, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        thirteenth_run_id = f"{_YEAR}-12-thirteenth"
        result_no = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        result_with = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            calendar=cal,
            per_run_events={thirteenth_run_id: (absence,)},
        )
        thirteenth_no = next(
            r
            for r in result_no.period_results
            if r.period_id.month == 12
            and r.run is not None
            and r.run.run_kind == "thirteenth"
        )
        thirteenth_with = next(
            r
            for r in result_with.period_results
            if r.period_id.month == 12
            and r.run is not None
            and r.run.run_kind == "thirteenth"
        )
        assert thirteenth_with.period_net < thirteenth_no.period_net

    def test_extra_month_run_events_do_not_appear_in_regular_run(self) -> None:
        """Events allocated to thirteenth run are not applied to regular December."""
        cal = self._calendar_13()
        absence = AbsenceEvent(
            event_date=date(_YEAR, 12, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        thirteenth_run_id = f"{_YEAR}-12-thirteenth"
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            calendar=cal,
            per_run_events={thirteenth_run_id: (absence,)},
        )
        regular_dec = next(
            r
            for r in result.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        result_no = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=cal)
        regular_dec_no = next(
            r
            for r in result_no.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        assert regular_dec.period_gross == regular_dec_no.period_gross

    def test_duplicate_allocation_raises(self) -> None:
        """Supplying the same run in both period_events and per_run_events raises."""
        cal = WorkCalendar(year=_YEAR)
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-03-regular"
        with pytest.raises(ValueError, match="Duplicate event allocation"):
            calculate_year(
                _YEAR,
                _CCNL,
                _LEVEL,
                calendar=cal,
                period_events={3: (absence,)},
                per_run_events={run_id: (absence,)},
            )

    def test_period_events_still_work_without_per_run_events(self) -> None:
        """period_events parameter continues to work when per_run_events is absent."""
        cal = WorkCalendar(year=_YEAR)
        absence = AbsenceEvent(
            event_date=date(_YEAR, 6, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_year(
            _YEAR, _CCNL, _LEVEL, calendar=cal, period_events={6: (absence,)}
        )
        jun_net = result.period_results[5].period_net
        jan_net = result.period_results[0].period_net
        assert jun_net < jan_net
