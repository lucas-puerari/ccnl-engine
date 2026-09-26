"""Unit tests for PayrollSchedule domain type."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.extra_month_schedule import (
    AccrualWindow,
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.schedule import PayrollSchedule, WithholdingSchedule


class TestPayrollScheduleFromCalendar:
    """PayrollSchedule.from_calendar builds the correct run sequence."""

    def test_no_extra_months_produces_12_regular_runs(self) -> None:
        """A calendar with no extra months produces exactly 12 regular runs."""
        cal = WorkCalendar(year=2026)
        schedule = PayrollSchedule.from_calendar(cal)
        assert len(schedule.runs) == 12
        assert all(r.run_kind == "regular" for r in schedule.runs)

    def test_regular_runs_cover_all_months(self) -> None:
        """Months 1-12 appear in order in the regular run sequence."""
        cal = WorkCalendar(year=2026)
        schedule = PayrollSchedule.from_calendar(cal)
        assert [r.month for r in schedule.runs] == list(range(1, 13))

    def test_tredicesima_adds_thirteenth_run_in_december(self) -> None:
        """A tredicesima in December produces 13 runs with a thirteenth in December."""
        cal = WorkCalendar(
            year=2026,
            extra_months=(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=12,
                ),
            ),
        )
        schedule = PayrollSchedule.from_calendar(cal)
        assert len(schedule.runs) == 13
        thirteenth_runs = [r for r in schedule.runs if r.run_kind == "thirteenth"]
        assert len(thirteenth_runs) == 1
        assert thirteenth_runs[0].month == 12

    def test_quattordicesima_adds_fourteenth_run(self) -> None:
        """A quattordicesima in July produces 14 runs with a fourteenth in July."""
        cal = WorkCalendar(
            year=2026,
            extra_months=(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=12,
                ),
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.FOURTEENTH,
                    name="quattordicesima",
                    payment_month=7,
                ),
            ),
        )
        schedule = PayrollSchedule.from_calendar(cal)
        assert len(schedule.runs) == 14
        fourteenth_runs = [r for r in schedule.runs if r.run_kind == "fourteenth"]
        assert len(fourteenth_runs) == 1
        assert fourteenth_runs[0].month == 7

    def test_extra_run_inserted_after_regular_month(self) -> None:
        """The thirteenth run appears directly after the regular December run."""
        cal = WorkCalendar(
            year=2026,
            extra_months=(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=12,
                ),
            ),
        )
        schedule = PayrollSchedule.from_calendar(cal)
        dec_regular_idx = next(
            i
            for i, r in enumerate(schedule.runs)
            if r.run_kind == "regular" and r.month == 12
        )
        assert schedule.runs[dec_regular_idx + 1].run_kind == "thirteenth"

    def test_year_propagated_correctly(self) -> None:
        """All runs carry the calendar year."""
        cal = WorkCalendar(year=2025)
        schedule = PayrollSchedule.from_calendar(cal)
        assert all(r.year == 2025 for r in schedule.runs)


class TestPayrollScheduleValidation:
    """PayrollSchedule rejects invalid run configurations."""

    def test_duplicate_run_id_raises(self) -> None:
        """Duplicate run_id in the runs tuple raises ValueError."""
        run = PayrollRun.regular(2026, 1)
        with pytest.raises(ValueError, match="duplicate"):
            PayrollSchedule(year=2026, runs=(run, run))

    def test_run_year_mismatch_raises(self) -> None:
        """A run belonging to a different year raises ValueError."""
        run = PayrollRun.regular(2025, 1)
        with pytest.raises(ValueError, match="year"):
            PayrollSchedule(year=2026, runs=(run,))


class TestExtraMonthScheduleValidation:
    """ExtraMonthSchedule rejects invalid field values."""

    def test_invalid_accrual_window_start_raises(self) -> None:
        """accrual_window_start_month outside 1-12 raises ValueError."""
        with pytest.raises(ValueError, match="accrual_window_start_month"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=12,
                accrual_window_start_month=0,
            )

    def test_invalid_max_fraction_raises(self) -> None:
        """max_fraction <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="max_fraction"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=12,
                max_fraction=Decimal(0),
            )


class TestWorkCalendarFromAdditionalMonths:
    """WorkCalendar.from_additional_months handles all supported cases."""

    def test_fractional_quattordicesima_sets_max_fraction(self) -> None:
        """additional_months=13.5 produces a quattordicesima with max_fraction=0.5."""
        cal = WorkCalendar.from_additional_months(2026, Decimal("13.5"))
        assert len(cal.extra_months) == 2
        fourteenth = next(
            s for s in cal.extra_months if s.kind == ExtraMonthKind.FOURTEENTH
        )
        assert fourteenth.max_fraction == Decimal("0.5")

    def test_duplicate_extra_month_raises(self) -> None:
        """Two schedules with the same kind raise ValueError."""
        sched = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        with pytest.raises(ValueError, match="duplicate"):
            WorkCalendar(year=2026, extra_months=(sched, sched))

    def test_duplicate_kind_different_payment_months_raises(self) -> None:
        """Two THIRTEENTH schedules in different payment months raise ValueError."""
        sched_june = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima-june",
            payment_month=6,
        )
        sched_dec = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima-dec",
            payment_month=12,
        )
        with pytest.raises(ValueError, match="duplicate"):
            WorkCalendar(year=2026, extra_months=(sched_june, sched_dec))

    def test_fourteenth_without_thirteenth_raises(self) -> None:
        """A FOURTEENTH schedule without THIRTEENTH raises ValueError."""
        sched = ExtraMonthSchedule(
            kind=ExtraMonthKind.FOURTEENTH,
            name="quattordicesima",
            payment_month=6,
        )
        with pytest.raises(ValueError, match="fourteenth month requires a thirteenth"):
            WorkCalendar(year=2026, extra_months=(sched,))


class TestScheduleForEmployment:
    """Only the runs of months the employment overlaps are kept."""

    _CALENDAR = WorkCalendar.from_additional_months(2026, 14)

    def _runs(self, period: EmploymentPeriod) -> list[tuple[int, str]]:
        schedule = PayrollSchedule.from_calendar(self._CALENDAR, period)
        return [(r.month, r.run_kind) for r in schedule.runs]

    def test_no_employment_keeps_every_run(self) -> None:
        """Without an employment period the full calendar applies."""
        schedule = PayrollSchedule.from_calendar(self._CALENDAR, None)
        assert schedule.run_count.value == 14

    def test_three_months_outside_both_payment_months(self) -> None:
        """July to September: three regular runs and no extra month."""
        period = EmploymentPeriod(date(2026, 7, 1), date(2026, 9, 30))
        assert self._runs(period) == [(m, RunKind.REGULAR) for m in (7, 8, 9)]

    def test_hire_after_june_drops_the_quattordicesima(self) -> None:
        """An open-ended hire on 15 July keeps the December tredicesima only."""
        runs = self._runs(EmploymentPeriod(date(2026, 7, 15)))
        assert [m for m, kind in runs if kind is RunKind.REGULAR] == list(range(7, 13))
        assert [(m, k) for m, k in runs if k is not RunKind.REGULAR] == [
            (12, RunKind.THIRTEENTH)
        ]

    def test_end_in_june_keeps_the_june_quattordicesima(self) -> None:
        """An employment ending on 10 June overlaps the payment month."""
        runs = self._runs(EmploymentPeriod(date(2026, 1, 1), date(2026, 6, 10)))
        assert runs[-2:] == [(6, RunKind.REGULAR), (6, RunKind.FOURTEENTH)]
        assert (12, RunKind.THIRTEENTH) not in runs

    def test_employment_outside_the_year_has_no_run(self) -> None:
        """An employment ended in 2025 has no run in 2026."""
        period = EmploymentPeriod(date(2025, 1, 1), date(2025, 12, 31))
        assert PayrollSchedule.from_calendar(self._CALENDAR, period).runs == ()

    def test_withholding_slots_follow_the_selected_runs(self) -> None:
        """A short employment has one withholding slot per selected run."""
        period = EmploymentPeriod(date(2026, 5, 1), date(2026, 7, 31))
        schedule = PayrollSchedule.from_calendar(self._CALENDAR, period)
        withholding = WithholdingSchedule.for_runs(schedule, self._CALENDAR)
        assert tuple(s.run for s in withholding.slots) == schedule.runs
        assert withholding.run_count.value == 4


class TestAccrualWindow:
    """An extra month accrues over dates that never precede the hire date."""

    _FOURTEENTH = ExtraMonthSchedule(
        kind=ExtraMonthKind.FOURTEENTH,
        name="quattordicesima",
        payment_month=6,
        accrual_window_start_month=7,
    )
    _THIRTEENTH = ExtraMonthSchedule(
        kind=ExtraMonthKind.THIRTEENTH, name="tredicesima", payment_month=12
    )

    def test_cross_year_window_without_hire_date(self) -> None:
        """A July to June quattordicesima starts in the previous year."""
        window = self._FOURTEENTH.accrual_window(2026)
        assert window == AccrualWindow(
            nominal_start=date(2025, 7, 1),
            start=date(2025, 7, 1),
            end=date(2026, 6, 30),
        )

    def test_cross_year_window_is_clipped_to_the_hire_date(self) -> None:
        """A worker hired on 10 March 2026 accrues from 10 March only."""
        window = self._FOURTEENTH.accrual_window(2026, date(2026, 3, 10))
        assert window.nominal_start == date(2025, 7, 1)
        assert window.start == date(2026, 3, 10)

    def test_hire_before_the_window_keeps_the_nominal_start(self) -> None:
        """A hire before 1 January leaves the tredicesima window unchanged."""
        window = self._THIRTEENTH.accrual_window(2026, date(2020, 5, 4))
        assert window.start == date(2026, 1, 1)
        assert window.end == date(2026, 12, 31)

    def test_unordered_dates_are_rejected(self) -> None:
        """A start after the end cannot form a window."""
        with pytest.raises(ValueError, match="nominal_start <= start <= end"):
            AccrualWindow(
                nominal_start=date(2026, 1, 1),
                start=date(2026, 7, 1),
                end=date(2026, 6, 30),
            )
