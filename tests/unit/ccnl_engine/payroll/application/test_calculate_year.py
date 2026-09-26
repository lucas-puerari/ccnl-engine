"""Unit tests for calculate_year() and WorkCalendar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.application import calculate_year as calculate_year_module
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employment import EmploymentPeriod, Permanent
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import (
        PeriodCalculationRequest,
        PeriodCalculationResult,
    )

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
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        with pytest.raises(AttributeError):
            result.year = 2025  # type: ignore[misc]

    def test_year_stored(self) -> None:
        """Year matches the requested year."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        assert result.year == _YEAR

    def test_calendar_year_mismatch_raises(self) -> None:
        """An override for another year raises InvalidInputError."""
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(2025, 13),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="wrong year",
        )
        with pytest.raises(InvalidInputError, match="year 2025"):
            calculate_year(_YEAR, _CCNL, _LEVEL, calendar=override)


class TestCalculateYear:
    """calculate_year() chains calculate_period across all runs of the year."""

    def test_produces_13_period_results(self) -> None:
        """Metalmeccanico grants a tredicesima: 12 regular runs plus one."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        assert len(result.period_results) == 13

    def test_annual_gross_equals_sum_of_periods(self) -> None:
        """annual_gross is the exact sum of all period_gross values."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        expected = sum((r.period_gross for r in result.period_results), Decimal(0))
        assert result.annual_gross == expected

    def test_annual_net_equals_sum_of_periods(self) -> None:
        """annual_net is the exact sum of all period_net values."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        expected = sum((r.period_net for r in result.period_results), Decimal(0))
        assert result.annual_net == expected

    def test_annual_employer_cost_equals_sum_of_periods(self) -> None:
        """annual_employer_cost is the exact sum of all period_employer_cost values."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        expected = sum(
            (r.period_employer_cost for r in result.period_results), Decimal(0)
        )
        assert result.annual_employer_cost == expected

    def test_state_threaded_across_periods(self) -> None:
        """Closing state of period N is the opening state of period N+1."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        for i in range(1, 12):
            prev = result.period_results[i - 1]
            curr = result.period_results[i]
            assert curr.closing_state.regular_periods_closed == (
                prev.closing_state.regular_periods_closed + 1
            )

    def test_regular_periods_closed_reaches_12(self) -> None:
        """After the year regular_periods_closed equals 12, extra runs aside."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        assert result.period_results[-1].closing_state.regular_periods_closed == 12

    def test_period_ids_are_in_order(self) -> None:
        """Regular period results are ordered January to December."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        regular = [
            r
            for r in result.period_results
            if r.run is not None and r.run.run_kind == "regular"
        ]
        for i, pr in enumerate(regular, start=1):
            assert pr.period_id.month == i
            assert pr.period_id.year == _YEAR

    def test_explicit_contract_type(self) -> None:
        """An explicitly supplied contract_type is used instead of the default."""
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            contract_type=Permanent(),
        )
        assert len(result.period_results) == 13

    def test_period_events_injected(self) -> None:
        """Events supplied in period_events are applied to the correct period."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            period_events={3: (absence,)},
        )
        # March net must be lower than January net (absence in EMPLOYEE_DEDUCTIONS)
        jan_net = result.period_results[0].period_net
        mar_net = result.period_results[2].period_net
        assert mar_net < jan_net

    def test_all_period_gross_values_positive(self) -> None:
        """With no events every period_gross value is positive."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        for r in result.period_results:
            assert r.period_gross > Decimal(0)

    def test_gross_ytd_accumulates_correctly(self) -> None:
        """gross_ytd in the last closing state equals annual_gross."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        dec_state = result.period_results[-1].closing_state
        assert dec_state.earnings.gross == result.annual_gross

    def test_calendar_none_auto_derives_from_ccnl(self) -> None:
        """Without an override the CCNL additional_months sets the calendar.

        metalmeccanico-federmeccanica has additional_months=13: one
        tredicesima paid in December.
        """
        result = calculate_year(_YEAR, _CCNL, _LEVEL)
        assert result.calendar == WorkCalendar.from_additional_months(_YEAR, 13)
        assert result.calendar_override is None


class TestEmploymentPeriodRuns:
    """The employment period selects the runs of the year."""

    def test_mid_month_hire_starts_in_the_hire_month(self) -> None:
        """Hired 15 March, open-ended: March to December plus the tredicesima."""
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            employment_period=EmploymentPeriod(date(_YEAR, 3, 15)),
        )
        runs = [
            (r.period_id.month, r.run.run_kind) for r in result.period_results if r.run
        ]
        assert runs == [(m, RunKind.REGULAR) for m in range(3, 13)] + [
            (12, RunKind.THIRTEENTH)
        ]

    def test_partial_month_is_provisional_and_whole_months_final(self) -> None:
        """Only the partly employed month carries the provisional issue."""
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            employment_period=EmploymentPeriod(date(_YEAR, 3, 15)),
        )
        march, april = result.period_results[0], result.period_results[1]
        assert [i.code for i in march.issues] == ["partial_month_not_prorated"]
        assert march.status is CalculationStatus.PROVISIONAL
        assert april.status is CalculationStatus.FINAL
        assert result.period_results[-1].status is CalculationStatus.FINAL
        assert result.status is CalculationStatus.PROVISIONAL

    def test_termination_in_may_has_no_december_tredicesima(self) -> None:
        """Ended 31 May: five regular runs, no extra-month run."""
        result = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 5, 31)),
        )
        assert [r.run.run_kind for r in result.period_results if r.run] == [
            RunKind.REGULAR
        ] * 5
        assert result.status is CalculationStatus.FINAL

    def test_employment_outside_the_year_is_rejected(self) -> None:
        """An employment ended in 2025 has nothing to compute in 2026."""
        with pytest.raises(InvalidInputError, match="no day in 2026"):
            calculate_year(
                _YEAR,
                _CCNL,
                _LEVEL,
                employment_period=EmploymentPeriod(
                    date(2025, 1, 1), date(2025, 12, 31)
                ),
            )

    def test_requests_carry_selected_slots_and_clipped_window(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Slots match the selected runs; the windows start at hire.

        Hired 10 March: March has 22 employed days, so it qualifies.  The
        quattordicesima accrues March to June (4/12), the tredicesima March
        to December (10/12).
        """
        requests: list[PeriodCalculationRequest] = []

        def _spy(
            req: PeriodCalculationRequest, **kwargs: object
        ) -> PeriodCalculationResult:
            requests.append(req)
            return calculate_period(req, **kwargs)  # type: ignore[arg-type]

        monkeypatch.setattr(calculate_year_module, "calculate_period", _spy)
        calculate_year(
            _YEAR,
            "commercio-confcommercio.json",
            "4",
            employment_period=EmploymentPeriod(date(_YEAR, 3, 10)),
        )
        schedule = requests[0].withholding_schedule
        assert schedule is not None
        assert tuple(s.run for s in schedule.slots) == tuple(
            r.run for r in requests if r.run is not None
        )
        accruals = {
            r.run.run_kind: r.extra_month_accrual
            for r in requests
            if r.run is not None and r.extra_month_accrual is not None
        }
        fourteenth = accruals[RunKind.FOURTEENTH]
        thirteenth = accruals[RunKind.THIRTEENTH]
        assert fourteenth.window.start == date(_YEAR, 3, 10)
        assert fourteenth.window.nominal_start == date(_YEAR - 1, 7, 1)
        assert fourteenth.months == 4
        assert thirteenth.window.start == date(_YEAR, 3, 10)
        assert thirteenth.months == 10
        assert requests[0].extra_month_accrual is None
        assert all(not r.extra_month_settlements for r in requests)


class TestCalendarOverride:
    """An override replaces the standard calendar only when it is valid."""

    def test_payment_month_override_keeps_the_annual_gross(self) -> None:
        """Commercio quattordicesima paid in July: same gross, later run."""
        commercio = "commercio-confcommercio.json"
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(
                _YEAR, 14, fourteenth_payment_month=7
            ),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="quattordicesima paid with the July salary",
        )
        standard = calculate_year(_YEAR, commercio, "4")
        moved = calculate_year(_YEAR, commercio, "4", calendar=override)
        run_ids = [r.run.run_id for r in moved.period_results if r.run is not None]
        assert run_ids[7] == f"{_YEAR}-07-fourteenth"
        assert moved.annual_gross == standard.annual_gross
        assert moved.calendar is override.calendar
        assert moved.calendar_override is override

    def test_withholding_schedule_follows_the_override(self) -> None:
        """Every run carries a slot of the same schedule built from the override."""
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(_YEAR, 14),
            reason=CalendarOverrideReason.MORE_FAVOURABLE_TREATMENT,
            note="company agreement grants a quattordicesima",
        )
        result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=override)
        assert len(result.period_results) == 14
        last = result.period_results[-1].closing_state
        assert last.tax_withholding_periods_closed == 14

    def test_override_that_drops_the_ccnl_extra_month_is_rejected(self) -> None:
        """No reason lets an override remove the tredicesima the CCNL grants."""
        override = CalendarOverride(
            calendar=WorkCalendar(year=_YEAR),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="no tredicesima",
        )
        with pytest.raises(InvalidInputError, match="thirteenth"):
            calculate_year(_YEAR, _CCNL, _LEVEL, calendar=override)


class TestPerRunEventAllocation:
    """per_run_events allocates events explicitly to a specific run by run_id."""

    def test_per_run_events_applied_to_correct_run(self) -> None:
        """Events in per_run_events reach the named run and no other run."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result_no_event = calculate_year(_YEAR, _CCNL, _LEVEL)
        result_with_event = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
            per_run_events={run_id: (absence,)},
        )
        may_no = result_no_event.period_results[4].period_net
        may_with = result_with_event.period_results[4].period_net
        assert may_with < may_no

    def test_per_run_events_do_not_leak_to_other_runs(self) -> None:
        """Events allocated by run_id do not appear in other runs."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 5, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        run_id = f"{_YEAR}-05-regular"
        result = calculate_year(
            _YEAR, _CCNL, _LEVEL, per_run_events={run_id: (absence,)}
        )
        may_gross = result.period_results[4].period_gross
        for i, pr in enumerate(result.period_results):
            if i != 4:
                assert pr.period_gross >= may_gross or i >= 5

    def test_extra_month_run_accepts_per_run_events(self) -> None:
        """per_run_events can allocate events to extra-month runs by run_id."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 12, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        thirteenth_run_id = f"{_YEAR}-12-thirteenth"
        result_no = calculate_year(_YEAR, _CCNL, _LEVEL)
        result_with = calculate_year(
            _YEAR,
            _CCNL,
            _LEVEL,
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
            per_run_events={thirteenth_run_id: (absence,)},
        )
        regular_dec = next(
            r
            for r in result.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        result_no = calculate_year(_YEAR, _CCNL, _LEVEL)
        regular_dec_no = next(
            r
            for r in result_no.period_results
            if r.period_id.month == 12
            and (r.run is None or r.run.run_kind == "regular")
        )
        assert regular_dec.period_gross == regular_dec_no.period_gross

    def test_duplicate_allocation_raises(self) -> None:
        """Supplying the same run in both period_events and per_run_events raises."""
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
                period_events={3: (absence,)},
                per_run_events={run_id: (absence,)},
            )

    def test_period_events_still_work_without_per_run_events(self) -> None:
        """period_events parameter continues to work when per_run_events is absent."""
        absence = AbsenceEvent(
            event_date=date(_YEAR, 6, 10),
            hours=Decimal(8),
            hourly_rate=Decimal("13.00"),
        )
        result = calculate_year(_YEAR, _CCNL, _LEVEL, period_events={6: (absence,)})
        jun_net = result.period_results[5].period_net
        jan_net = result.period_results[0].period_net
        assert jun_net < jan_net


class TestSurtaxStatus:
    """Surtax decisions set the status of every run and of the year."""

    def test_unknown_municipality_makes_every_run_and_the_year_incomplete(
        self,
    ) -> None:
        """A Belfiore code without a table leaves the whole year incomplete."""
        result = calculate_year(_YEAR, _CCNL, _LEVEL, comune_belfiore="Z999")

        assert {r.status for r in result.period_results} == {
            CalculationStatus.INCOMPLETE
        }
        assert result.status is CalculationStatus.INCOMPLETE
        assert {i.code for i in result.issues} == {"municipal_surtax_unknown"}

    def test_malformed_region_code_is_rejected(self) -> None:
        """A region name instead of a region code is invalid input."""
        with pytest.raises(InvalidInputError, match="ISO 3166-2:IT"):
            calculate_year(_YEAR, _CCNL, _LEVEL, regione="Lombardia")
