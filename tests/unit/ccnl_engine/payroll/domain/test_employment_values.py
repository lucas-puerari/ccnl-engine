"""Unit tests for the employment fact value objects."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import EmploymentFacts
from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employment import (
    ContributableHours,
    EmploymentPeriod,
    SeniorityMonths,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_payroll import PeriodId

_START = date(2026, 3, 1)


class TestWeeklyHours:
    """Weekly hours are strictly positive."""

    def test_accepts_positive(self) -> None:
        """Positive hours are valid."""
        assert WeeklyHours(25).value == 25

    @pytest.mark.parametrize("value", [0, -40])
    def test_rejects_non_positive(self, value: int) -> None:
        """Zero or negative weekly hours are impossible."""
        with pytest.raises(InvalidInputError, match="weekly_hours must be > 0"):
            WeeklyHours(value)

    @pytest.mark.parametrize("value", [True, 1.5, "3"])
    def test_rejects_non_int(self, value: object) -> None:
        """Bools, floats and strings are not silently coerced."""
        with pytest.raises(InvalidInputError, match="weekly_hours must be an int"):
            WeeklyHours(value)  # type: ignore[arg-type]


class TestSeniorityMonths:
    """Seniority is a non-negative count of months."""

    def test_accepts_zero(self) -> None:
        """A new hire has zero months of service."""
        assert SeniorityMonths(0).value == 0

    def test_rejects_negative(self) -> None:
        """Negative service is impossible."""
        with pytest.raises(InvalidInputError, match="seniority_months must be >= 0"):
            SeniorityMonths(-12)


class TestContributableHours:
    """Contributable hours are a finite, non-negative Decimal."""

    def test_accepts_zero(self) -> None:
        """A period without paid hours has zero contributable hours."""
        assert ContributableHours(Decimal(0)).value == Decimal(0)

    def test_rejects_negative(self) -> None:
        """Negative hours would produce negative contributions."""
        with pytest.raises(InvalidInputError, match="must be >= 0"):
            ContributableHours(Decimal(-160))

    @pytest.mark.parametrize("value", [160.0, Decimal("NaN"), Decimal("Infinity")])
    def test_rejects_non_finite_or_non_decimal(self, value: object) -> None:
        """Floats and non-finite Decimals are rejected."""
        with pytest.raises(InvalidInputError, match="finite Decimal"):
            ContributableHours(value)  # type: ignore[arg-type]


class TestEmploymentPeriod:
    """The employment period cannot end before it starts."""

    def test_open_ended(self) -> None:
        """An open-ended period has no end date."""
        assert EmploymentPeriod(started_on=_START).ended_on is None

    def test_single_day(self) -> None:
        """Start and end on the same day is a valid one-day employment."""
        period = EmploymentPeriod(started_on=_START, ended_on=_START)
        assert period.ended_on == _START

    def test_rejects_end_before_start(self) -> None:
        """An end date before the start date is impossible."""
        with pytest.raises(InvalidInputError, match="must not precede"):
            EmploymentPeriod(started_on=_START, ended_on=date(2026, 2, 28))

    def test_from_dates_without_dates(self) -> None:
        """No dates means the period is not tracked."""
        assert EmploymentPeriod.from_dates(None, None) is None

    def test_from_dates_builds_period(self) -> None:
        """Both dates build a validated period."""
        end = date(2026, 9, 30)
        assert EmploymentPeriod.from_dates(_START, end) == EmploymentPeriod(
            started_on=_START, ended_on=end
        )

    def test_from_dates_rejects_end_without_start(self) -> None:
        """An end date without a start date cannot form a period."""
        with pytest.raises(InvalidInputError, match="requires started_on"):
            EmploymentPeriod.from_dates(None, date(2026, 9, 30))


class TestWithinFullTime:
    """Contracted weekly hours never exceed full-time weekly hours."""

    @pytest.mark.parametrize(
        ("weekly", "full_time"),
        [(None, None), (WeeklyHours(60), None), (None, WeeklyHours(40))],
    )
    def test_accepts_missing_values(
        self, weekly: WeeklyHours | None, full_time: WeeklyHours | None
    ) -> None:
        """Nothing to compare when either value is absent."""
        check_within_full_time(weekly, full_time)

    def test_accepts_equal_hours(self) -> None:
        """Full-time hours equal to the contract hours are valid."""
        check_within_full_time(WeeklyHours(40), WeeklyHours(40))

    def test_rejects_hours_above_full_time(self) -> None:
        """Sixty hours on a forty-hour full time is impossible."""
        with pytest.raises(InvalidInputError, match="must not exceed"):
            check_within_full_time(WeeklyHours(60), WeeklyHours(40))

    def test_period_request_rejects_hours_above_full_time(self) -> None:
        """The internal request enforces the same rule as the public facts."""
        with pytest.raises(InvalidInputError, match="must not exceed"):
            PeriodCalculationRequest(
                period_id=PeriodId(year=2026, month=1),
                payment_date=date(2026, 1, 27),
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                weekly_hours=WeeklyHours(60),
                full_time_weekly_hours=WeeklyHours(40),
            )


class TestEmploymentFactsValidation:
    """The public facts expose validated value objects."""

    def test_exposes_value_objects(self) -> None:
        """Every scalar fact is available as its value object."""
        facts = EmploymentFacts(
            weekly_hours=20,
            full_time_weekly_hours=40,
            contributable_hours=Decimal(86),
            seniority_months=36,
            started_on=_START,
        )
        assert facts.contracted_hours == WeeklyHours(20)
        assert facts.full_time_hours == WeeklyHours(40)
        assert facts.contributable == ContributableHours(Decimal(86))
        assert facts.seniority == SeniorityMonths(36)
        assert facts.period == EmploymentPeriod(started_on=_START)

    def test_optional_facts_default_to_none(self) -> None:
        """Untracked facts stay ``None``."""
        facts = EmploymentFacts()
        assert facts.contracted_hours is None
        assert facts.full_time_hours is None
        assert facts.contributable is None
        assert facts.seniority is None
        assert facts.period is None

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"weekly_hours": 0}, id="zero-weekly-hours"),
            pytest.param({"full_time_weekly_hours": 0}, id="zero-full-time"),
            pytest.param({"ended_on": date(2026, 9, 30)}, id="end-without-start"),
        ],
    )
    def test_rejects_impossible_facts(self, kwargs: dict[str, object]) -> None:
        """Impossible facts fail at construction."""
        with pytest.raises(InvalidInputError):
            EmploymentFacts(**kwargs)  # type: ignore[arg-type]
