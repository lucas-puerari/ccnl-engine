"""Unit tests for the employment fact value objects."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    EmploymentPeriod,
    WeeklyHours,
    WorkPattern,
    check_pattern_hours,
    check_within_full_time,
)
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import (
    SeniorityFact,
    SenioritySource,
)

_START = date(2026, 3, 1)
_SENIORITY = SeniorityFact(36, _START, SenioritySource.PAYSLIP)


class TestWeeklyHours:
    """Weekly hours are a positive Decimal of at most two places, up to 168."""

    @pytest.mark.parametrize("value", ["25", "37.5", "37.25", "168"])
    def test_accepts_positive_hundredths(self, value: str) -> None:
        """Whole, half and quarter hours up to a whole week are valid."""
        assert WeeklyHours(Decimal(value)).value == Decimal(value)

    @pytest.mark.parametrize("value", ["0", "-40", "168.01"])
    def test_rejects_out_of_range(self, value: str) -> None:
        """Zero, negative or more than a week of hours are impossible."""
        with pytest.raises(
            InvalidInputError, match=r"WeeklyHours\.value must be a finite Decimal"
        ):
            WeeklyHours(Decimal(value))

    def test_rejects_more_than_two_places(self) -> None:
        """A thousandth of an hour is not a contracted hour."""
        with pytest.raises(InvalidInputError, match="at most two decimal places"):
            WeeklyHours(Decimal("37.125"))

    def test_keeps_the_stated_exponent(self) -> None:
        """Trailing zeros are allowed and the value is not re-quantized."""
        assert str(WeeklyHours(Decimal("37.50")).value) == "37.50"

    @pytest.mark.parametrize("value", [True, 40, 37.5, "3"])
    def test_rejects_non_decimal(self, value: object) -> None:
        """Bools, ints, floats and strings are not silently coerced."""
        with pytest.raises(
            InvalidInputError, match=r"WeeklyHours\.value must be a finite Decimal"
        ):
            WeeklyHours(value)  # type: ignore[arg-type]


_MON_WED = (Decimal(8), Decimal(8), Decimal(8), *(Decimal(0),) * 4)


class TestWorkPattern:
    """A pattern states the weekday hours, the months worked, or both."""

    def test_weekday_hours_sum_to_the_week(self) -> None:
        """Eight hours Monday to Wednesday are 24 hours a week."""
        pattern = WorkPattern(weekday_hours=_MON_WED)
        assert pattern.weekly_hours == Decimal(24)
        assert pattern.works_in(8)

    def test_a_list_of_days_is_stored_as_a_tuple(self) -> None:
        """A list is accepted and normalised, as other public collections."""
        pattern = WorkPattern(weekday_hours=list(_MON_WED))  # type: ignore[arg-type]
        assert pattern.weekday_hours == _MON_WED

    def test_months_without_days_state_no_weekly_hours(self) -> None:
        """A vertical part time over the year leaves the week to weekly_hours."""
        pattern = WorkPattern(months=frozenset(range(1, 7)))
        assert pattern.weekly_hours is None
        assert pattern.works_in(6)
        assert not pattern.works_in(7)

    def test_idle_days_are_the_days_of_the_months_not_worked(self) -> None:
        """Only the days of months outside the pattern are idle."""
        pattern = WorkPattern(months=frozenset({1}))
        idle = pattern.idle_days(date(2026, 1, 30), date(2026, 2, 2))
        assert idle == {date(2026, 2, 1), date(2026, 2, 2)}

    def test_no_idle_day_without_months(self) -> None:
        """A weekday pattern works every month."""
        pattern = WorkPattern(weekday_hours=_MON_WED)
        assert pattern.idle_days(date(2026, 1, 1), date(2026, 12, 31)) == frozenset()

    def test_rejects_an_empty_pattern(self) -> None:
        """A pattern stating nothing is a mistake, not a full time."""
        with pytest.raises(InvalidInputError, match="weekday_hours, months or both"):
            WorkPattern()

    @pytest.mark.parametrize(
        "days",
        [
            (Decimal(8),) * 6,
            (Decimal(0),) * 7,
            (Decimal(25), *(Decimal(0),) * 6),
            (Decimal(-1), *(Decimal(8),) * 6),
            (Decimal("7.125"), *(Decimal(0),) * 6),
        ],
    )
    def test_rejects_invalid_weekday_hours(self, days: tuple[Decimal, ...]) -> None:
        """Seven days of 0-24 hundredths of hours, at least one worked."""
        with pytest.raises(InvalidInputError, match=r"WorkPattern\.weekday_hours"):
            WorkPattern(weekday_hours=days)

    @pytest.mark.parametrize("months", [frozenset(), frozenset({0}), frozenset({13})])
    def test_rejects_invalid_months(self, months: frozenset[int]) -> None:
        """At least one month, each from 1 to 12."""
        with pytest.raises(InvalidInputError, match=r"WorkPattern\.months"):
            WorkPattern(months=months)

    def test_rejects_a_mutable_set_of_months(self) -> None:
        """The input is immutable, as Employment.roles."""
        with pytest.raises(InvalidInputError, match=r"WorkPattern\.months"):
            WorkPattern(months={1, 2})  # type: ignore[arg-type]


class TestCheckPatternHours:
    """Weekday hours must sum to the contracted weekly hours."""

    @pytest.mark.parametrize("pattern", [None, WorkPattern(months=frozenset({1}))])
    def test_nothing_to_check_without_weekday_hours(
        self, pattern: WorkPattern | None
    ) -> None:
        """Without days the weekly hours are not compared."""
        check_pattern_hours(None, pattern)

    def test_accepts_matching_hours(self) -> None:
        """24 weekday hours match 24 weekly hours."""
        check_pattern_hours(
            WeeklyHours(Decimal(24)), WorkPattern(weekday_hours=_MON_WED)
        )

    @pytest.mark.parametrize("weekly", [None, WeeklyHours(Decimal(20))])
    def test_rejects_missing_or_different_hours(
        self, weekly: WeeklyHours | None
    ) -> None:
        """The weekly hours are the single source of the part-time ratio."""
        with pytest.raises(InvalidInputError, match="sum to 24 hours a week"):
            check_pattern_hours(weekly, WorkPattern(weekday_hours=_MON_WED))


class TestContributableHours:
    """Contributable hours are a finite, non-negative Decimal."""

    def test_accepts_zero(self) -> None:
        """A period without paid hours has zero contributable hours."""
        assert ContributableHours(Decimal(0)).value == Decimal(0)

    def test_rejects_negative(self) -> None:
        """Negative hours would produce negative contributions."""
        with pytest.raises(InvalidInputError, match="must be a finite Decimal >= 0"):
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


class TestEmploymentPeriodMonths:
    """Month overlap and coverage decide which runs a year computes."""

    _PERIOD = EmploymentPeriod(started_on=date(2026, 3, 15), ended_on=date(2026, 9, 30))

    @pytest.mark.parametrize(
        ("month", "overlaps", "covers"),
        [
            pytest.param(2, False, False, id="before-hire"),
            pytest.param(3, True, False, id="hire-month"),
            pytest.param(6, True, True, id="whole-month"),
            pytest.param(9, True, True, id="ends-on-last-day"),
            pytest.param(10, False, False, id="after-end"),
        ],
    )
    def test_month_overlap_and_coverage(
        self, month: int, *, overlaps: bool, covers: bool
    ) -> None:
        """A month overlaps with one employed day and is covered with all."""
        assert self._PERIOD.overlaps_month(2026, month) is overlaps
        assert self._PERIOD.covers_month(2026, month) is covers

    @pytest.mark.parametrize(
        ("month", "span"),
        [
            pytest.param(2, None, id="before-hire"),
            pytest.param(3, (date(2026, 3, 15), date(2026, 3, 31)), id="hire-month"),
            pytest.param(6, (date(2026, 6, 1), date(2026, 6, 30)), id="whole-month"),
            pytest.param(10, None, id="after-end"),
        ],
    )
    def test_span_in_month_clips_to_the_employment(
        self, month: int, span: tuple[date, date] | None
    ) -> None:
        """The employed span of a month starts at hire and stops at the end."""
        assert self._PERIOD.span_in_month(2026, month) == span

    def test_open_ended_span_runs_to_the_month_end(self) -> None:
        """Without an end date the span of a later month is the whole month."""
        period = EmploymentPeriod(started_on=_START)
        assert period.span_in_month(2028, 2) == (date(2028, 2, 1), date(2028, 2, 29))

    def test_end_inside_month_is_partial(self) -> None:
        """An employment ending on 15 May overlaps May without covering it."""
        period = EmploymentPeriod(started_on=_START, ended_on=date(2026, 5, 15))
        assert period.overlaps_month(2026, 5)
        assert not period.covers_month(2026, 5)

    def test_open_ended_covers_later_years(self) -> None:
        """Without an end date every later month is covered."""
        period = EmploymentPeriod(started_on=_START)
        assert period.covers_month(2030, 12)

    def test_clip_start_moves_to_hire_date(self) -> None:
        """A date before the hire date is clipped to it; a later one is kept."""
        assert self._PERIOD.clip_start(date(2025, 7, 1)) == date(2026, 3, 15)
        assert self._PERIOD.clip_start(date(2026, 4, 1)) == date(2026, 4, 1)


class TestWithinFullTime:
    """Contracted weekly hours never exceed full-time weekly hours."""

    @pytest.mark.parametrize(
        ("weekly", "full_time"),
        [
            (None, None),
            (WeeklyHours(Decimal(60)), None),
            (None, WeeklyHours(Decimal(40))),
        ],
    )
    def test_accepts_missing_values(
        self, weekly: WeeklyHours | None, full_time: WeeklyHours | None
    ) -> None:
        """Nothing to compare when either value is absent."""
        check_within_full_time(weekly, full_time)

    def test_accepts_equal_hours(self) -> None:
        """Full-time hours equal to the contract hours are valid."""
        check_within_full_time(WeeklyHours(Decimal(40)), WeeklyHours(Decimal(40)))

    def test_rejects_hours_above_full_time(self) -> None:
        """Sixty hours on a forty-hour full time is impossible."""
        with pytest.raises(InvalidInputError, match="must not exceed"):
            check_within_full_time(WeeklyHours(Decimal(60)), WeeklyHours(Decimal(40)))

    def test_period_request_rejects_hours_above_full_time(self) -> None:
        """The internal request enforces the same rule as the public facts."""
        with pytest.raises(InvalidInputError, match="must not exceed"):
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=1),
                payment_date=date(2026, 1, 27),
                ccnl_id="commercio-confcommercio",
                level_code="4",
                weekly_hours=WeeklyHours(Decimal(60)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
            )


class TestEmploymentValidation:
    """The public employment holds validated value objects."""

    def test_keeps_value_objects(self) -> None:
        """Every fact is stored as the value object given."""
        employment = Employment(
            ccnl_id="commercio-confcommercio",
            level_code="4",
            weekly_hours=WeeklyHours(Decimal(20)),
            full_time_weekly_hours=WeeklyHours(Decimal(40)),
            seniority=_SENIORITY,
            employment_period=EmploymentPeriod(started_on=_START),
            contract_type=Permanent(),
        )
        assert employment.weekly_hours == WeeklyHours(Decimal(20))
        assert employment.full_time_weekly_hours == WeeklyHours(Decimal(40))
        assert employment.seniority == _SENIORITY
        assert employment.employment_period == EmploymentPeriod(started_on=_START)

    def test_optional_facts_default_to_none(self) -> None:
        """Untracked facts stay ``None``."""
        employment = Employment(
            ccnl_id="commercio-confcommercio",
            level_code="4",
            contract_type=Permanent(),
        )
        assert employment.weekly_hours is None
        assert employment.full_time_weekly_hours is None
        assert employment.seniority is None
        assert employment.employment_period is None
        assert employment.sector is None

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"weekly_hours": 20}, id="raw-weekly-hours"),
            pytest.param({"full_time_weekly_hours": 40}, id="raw-full-time"),
            pytest.param({"seniority": 36}, id="raw-seniority"),
            pytest.param({"employment_period": _START}, id="raw-period"),
            pytest.param({"roles": {"caposquadra"}}, id="mutable-roles"),
            pytest.param({"contribution_history": "post_1995"}, id="raw-history"),
            pytest.param({"ccnl_id": 7}, id="non-str-slug"),
        ],
    )
    def test_rejects_values_of_the_wrong_type(self, kwargs: dict[str, object]) -> None:
        """A raw value in place of its value object fails at construction."""
        fields: dict[str, object] = {
            "ccnl_id": "commercio-confcommercio",
            "level_code": "4",
            "contract_type": Permanent(),
            **kwargs,
        }
        with pytest.raises(InvalidInputError, match="must be"):
            Employment(**fields)  # type: ignore[arg-type]


class TestCcnlIdentifier:
    """The CCNL is named by one id: its slug or its CNEL code."""

    @pytest.mark.parametrize("ccnl_id", ["commercio-confcommercio", "H011", "C01A"])
    def test_a_slug_or_a_cnel_code_is_kept_as_given(self, ccnl_id: str) -> None:
        """The id is stored unchanged; the repository resolves it on the run."""
        employment = Employment(
            ccnl_id=ccnl_id, level_code="4", contract_type=Permanent()
        )
        assert employment.ccnl_id == ccnl_id

    @pytest.mark.parametrize(
        "ccnl_id",
        [
            "commercio-confcommercio.json",
            "Commercio",
            "commercio.JSON",
            "-commercio",
            "N/A",
            "E04",
            "",
        ],
    )
    def test_a_malformed_id_is_rejected(self, ccnl_id: str) -> None:
        """A filename, mixed case, a leading hyphen or an empty id are not ids."""
        with pytest.raises(InvalidInputError, match="CCNL slug"):
            Employment(ccnl_id=ccnl_id, level_code="4", contract_type=Permanent())
