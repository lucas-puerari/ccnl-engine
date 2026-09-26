"""Unit tests for PayrollSchedule domain type."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import PayrollSchedule


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
