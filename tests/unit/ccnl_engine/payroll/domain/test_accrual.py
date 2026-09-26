"""Extra-month accrual: qualifying months counted from dates, not from runs."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
    absence_days,
)
from ccnl_engine.payroll.domain.calendar import (
    AccrualWindow,
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.payroll.domain.employment import EmploymentPeriod

_THIRTEENTH = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH, name="tredicesima", payment_month=12
)
_FOURTEENTH = ExtraMonthSchedule(
    kind=ExtraMonthKind.FOURTEENTH,
    name="quattordicesima",
    payment_month=6,
    accrual_window_start_month=7,
)
_HALF_FOURTEENTH = ExtraMonthSchedule(
    kind=ExtraMonthKind.FOURTEENTH,
    name="quattordicesima",
    payment_month=6,
    accrual_window_start_month=7,
    max_fraction=Decimal("0.5"),
)


def _months(schedule: ExtraMonthSchedule, employment: EmploymentPeriod | None) -> int:
    return ExtraMonthAccrual.of(schedule, 2026, employment).months


class TestMonthAccrualRule:
    """A month qualifies when its accruing days reach the threshold."""

    def test_default_threshold_is_fifteen_days_with_a_source(self) -> None:
        """The engine default is documented as not coming from CCNL data."""
        assert DEFAULT_MONTH_ACCRUAL_RULE.min_days == 15
        assert "not read from CCNL data" in DEFAULT_MONTH_ACCRUAL_RULE.source

    @pytest.mark.parametrize("min_days", [0, 29])
    def test_threshold_outside_a_month_is_rejected(self, min_days: int) -> None:
        """A threshold above 28 would drop a February worked in full."""
        with pytest.raises(ValueError, match="min_days"):
            MonthAccrualRule(min_days=min_days)

    @pytest.mark.parametrize(
        ("hired_on", "months"),
        [
            pytest.param(date(2026, 3, 17), 10, id="15-days-in-march-count"),
            pytest.param(date(2026, 3, 18), 9, id="14-days-in-march-do-not"),
            pytest.param(date(2026, 12, 20), 0, id="12-days-in-december"),
        ],
    )
    def test_fraction_of_month_at_hire(self, hired_on: date, months: int) -> None:
        """March has 31 days: hire on the 17th leaves 15, on the 18th 14."""
        assert _months(_THIRTEENTH, EmploymentPeriod(hired_on)) == months

    def test_fraction_of_month_at_termination(self) -> None:
        """Ended 14 June: June has 14 days and does not count; Jan-May do."""
        employment = EmploymentPeriod(date(2020, 1, 1), date(2026, 6, 14))
        assert _months(_THIRTEENTH, employment) == 5

    def test_suspending_absence_removes_days(self) -> None:
        """An aspettativa of 20 days in April leaves 10: April does not count."""
        window = _THIRTEENTH.accrual_window(2026)
        days = absence_days(date(2026, 4, 1), date(2026, 4, 20))
        rule = DEFAULT_MONTH_ACCRUAL_RULE
        assert rule.qualifying_months(window, non_accruing_days=days) == 11

    def test_termination_before_the_window_start_accrues_nothing(self) -> None:
        """A window opening after the last day of employment has no month."""
        window = AccrualWindow(
            nominal_start=date(2026, 7, 1),
            start=date(2026, 7, 1),
            end=date(2027, 6, 30),
        )
        rule = DEFAULT_MONTH_ACCRUAL_RULE
        assert rule.qualifying_months(window, ended_on=date(2026, 6, 30)) == 0


class TestExtraMonthAccrual:
    """The rateo of one extra month for one employment."""

    def test_full_window_without_employment_dates(self) -> None:
        """No employment period means employed over the whole window."""
        accrual = ExtraMonthAccrual.of(_FOURTEENTH, 2026)
        assert accrual.months == 12
        assert accrual.fraction == Decimal(1)
        assert accrual.ended_on is None

    def test_hire_in_march_clips_the_quattordicesima_window(self) -> None:
        """Hired 10 March 2026: July 2025 to February 2026 are not employed."""
        assert _months(_FOURTEENTH, EmploymentPeriod(date(2026, 3, 10))) == 4

    def test_hire_before_the_window_accrues_prior_year_months(self) -> None:
        """Hired 1 October 2025: October 2025 to June 2026, nine months."""
        assert _months(_FOURTEENTH, EmploymentPeriod(date(2025, 10, 1))) == 9

    def test_termination_after_the_window_is_not_recorded(self) -> None:
        """An end after the payment month does not cut the window."""
        employment = EmploymentPeriod(date(2020, 1, 1), date(2026, 9, 30))
        accrual = ExtraMonthAccrual.of(_FOURTEENTH, 2026, employment)
        assert accrual.months == 12
        assert accrual.ended_on is None

    def test_termination_inside_the_window_is_recorded(self) -> None:
        """Ended 30 September: the next quattordicesima has three months."""
        employment = EmploymentPeriod(date(2026, 7, 1), date(2026, 9, 30))
        accrual = ExtraMonthAccrual.of(_FOURTEENTH, 2027, employment)
        assert accrual.months == 3
        assert accrual.ended_on == date(2026, 9, 30)
        assert accrual.fraction == Decimal("0.25")

    def test_fraction_includes_the_contractual_share(self) -> None:
        """Half a quattordicesima with six months: 6/12 of 0.5."""
        employment = EmploymentPeriod(date(2026, 1, 1))
        accrual = ExtraMonthAccrual.of(_HALF_FOURTEENTH, 2026, employment)
        assert accrual.fraction == Decimal("0.25")

    @pytest.mark.parametrize(
        ("months", "max_fraction", "match"),
        [
            (13, Decimal(1), "accrued months"),
            (-1, Decimal(1), "accrued months"),
            (6, Decimal(0), "max_fraction"),
        ],
    )
    def test_invalid_values_are_rejected(
        self, months: int, max_fraction: Decimal, match: str
    ) -> None:
        """Months stay within a window and the share within (0, 1]."""
        with pytest.raises(ValueError, match=match):
            ExtraMonthAccrual(
                kind=ExtraMonthKind.THIRTEENTH,
                window=_THIRTEENTH.accrual_window(2026),
                months=months,
                max_fraction=max_fraction,
            )


def test_absence_days_spans_the_range_inclusive() -> None:
    """Both ends are absence days; a reversed range is empty."""
    assert len(absence_days(date(2026, 4, 1), date(2026, 4, 20))) == 20
    assert absence_days(date(2026, 4, 2), date(2026, 4, 1)) == frozenset()
