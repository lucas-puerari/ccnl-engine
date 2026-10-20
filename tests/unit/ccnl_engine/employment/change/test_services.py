"""The employment in force on a date and the hours of a rateo."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.employment.change.services import (
    hours_ratio,
    in_force_on,
    rateo_scale,
)
from ccnl_engine.employment.fact.inputs import WeeklyHours
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule


def _employment(hours: int | None) -> Employment:
    return Employment(
        ccnl_id="commercio-confcommercio",
        level_code="4",
        contract_type=Permanent(),
        weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
        full_time_weekly_hours=None if hours is None else WeeklyHours(Decimal(40)),
    )


_FULL, _HALF = _employment(40), _employment(20)
_TIMELINE = ((date.min, _FULL), (date(2026, 7, 1), _HALF))
_SCHEDULE = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="thirteenth",
    payment_month=12,
    accrual_window_start_month=1,
)


def _accrual(outside: frozenset[date]) -> ExtraMonthAccrual:
    return ExtraMonthAccrual.of(_SCHEDULE, 2026, non_accruing_days=outside)


def test_the_employment_in_force_on_a_day() -> None:
    """The latest entry dated on or before the day."""
    assert in_force_on(_TIMELINE, date(2026, 6, 30)) is _FULL
    assert in_force_on(_TIMELINE, date(2026, 7, 1)) is _HALF
    assert in_force_on(((date(2026, 7, 1), _HALF),), date(2026, 1, 1)) is _HALF


def test_the_hours_ratio() -> None:
    """Weekly over full-time hours, one when not stated."""
    assert hours_ratio(_HALF) == Decimal("0.5")
    assert hours_ratio(_employment(None)) == 1


def test_six_months_full_and_six_half_paid_at_half() -> None:
    """(6 x 1 + 6 x 0.5) / (12 x 0.5) = 1.5."""
    assert rateo_scale(_accrual, _TIMELINE, _HALF) == Decimal("1.5")


def test_the_same_months_paid_at_full() -> None:
    """(6 x 1 + 6 x 0.5) / (12 x 1) = 0.75."""
    assert rateo_scale(_accrual, _TIMELINE, _FULL) == Decimal("0.75")


def test_no_change_of_hours_or_nothing_accrued_is_one() -> None:
    """Same hours everywhere, or a window with nothing accrued."""
    assert rateo_scale(_accrual, ((date.min, _FULL),), _FULL) == 1
    window = _accrual(frozenset()).window
    every_day = frozenset(
        date.fromordinal(o)
        for o in range(window.start.toordinal(), window.end.toordinal() + 1)
    )

    def nothing(outside: frozenset[date]) -> ExtraMonthAccrual:
        return _accrual(every_day | outside)

    assert rateo_scale(nothing, _TIMELINE, _HALF) == 1


def test_a_scale_must_be_above_zero() -> None:
    """A rateo paid at no hours is a defect, not a value."""
    with pytest.raises(ValueError, match="scale"):
        replace(_accrual(frozenset()), scale=Decimal(0))
