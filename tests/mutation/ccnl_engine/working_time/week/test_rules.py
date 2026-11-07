"""The hourly divisor of the normal week stated, swapped into the CCNL."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import WeeklyHours
from ccnl_engine.working_time.models import TimeSupplements, WeekDivisor
from ccnl_engine.working_time.week.rules import with_week_divisor

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_DAY = date(2026, 3, 10)


def _ccnl() -> CCNL:
    return load_ccnl("commercio-confcommercio")


def test_the_week_of_45_hours_divides_by_195() -> None:
    """Every period with a divisor reads 195; the week becomes 45."""
    ccnl = with_week_divisor(_ccnl(), WeeklyHours(Decimal(45)))
    periods = ccnl.parameters.hourly_divisor.periods

    assert {p.value for p in periods if p.value is not None} == {Decimal(195)}
    assert ccnl.parameters.hourly_divisor.value_at(_DAY) == Decimal(195)
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    assert supplements.hourly_divisor_weekly_hours == 45
    period = ccnl.parameters.hourly_divisor.period_at(_DAY)
    assert period is not None
    assert period.provenance is not None
    assert period.provenance.location is not None
    assert "45 ore" in (period.provenance.location.quote or "")


def test_the_occhiali_six_by_six_week_divides_by_156() -> None:
    """Art. 54 of the 2026 renewal: 173 for 40 hours, 156 for the 6x6."""
    ccnl = with_week_divisor(
        load_ccnl("occhiali-occhialeria-industria"), WeeklyHours(Decimal(36))
    )

    assert ccnl.parameters.hourly_divisor.value_at(_DAY) == Decimal(156)


@pytest.mark.parametrize("hours", [None, Decimal(40), Decimal(38)])
def test_a_week_without_a_divisor_of_its_own_keeps_the_ccnl(
    hours: Decimal | None,
) -> None:
    """Not stated, the CCNL week, or a week the CCNL sets no divisor for."""
    ccnl = _ccnl()
    week = None if hours is None else WeeklyHours(hours)
    assert with_week_divisor(ccnl, week) is ccnl


def test_a_ccnl_without_week_divisors_is_unchanged() -> None:
    """Chimica sets one divisor whatever the week."""
    ccnl = load_ccnl("chimica-farmaceutica-federchimica")
    assert with_week_divisor(ccnl, WeeklyHours(Decimal(42))) is ccnl


def test_a_ccnl_without_work_rules_is_unchanged() -> None:
    """No time supplements: nothing to swap."""
    ccnl = _ccnl().model_copy(update={"work_rules": None})
    assert with_week_divisor(ccnl, WeeklyHours(Decimal(45))) is ccnl


def test_work_rules_without_time_supplements_are_unchanged() -> None:
    """Work rules that set no time supplements: nothing to swap."""
    ccnl = _ccnl()
    assert ccnl.work_rules is not None
    rules = ccnl.work_rules.model_copy(update={"time_supplements": None})
    bare = ccnl.model_copy(update={"work_rules": rules})
    assert with_week_divisor(bare, WeeklyHours(Decimal(45))) is bare


def test_a_gap_in_the_divisor_stays_a_gap() -> None:
    """A period without a divisor does not take the one of the week."""
    ccnl = _ccnl()
    series = ccnl.parameters.hourly_divisor
    gap = series.periods[0].model_copy(update={"value": None})
    params = ccnl.parameters.model_copy(
        update={"hourly_divisor": series.model_copy(update={"periods": (gap,)})}
    )
    swapped = with_week_divisor(
        ccnl.model_copy(update={"parameters": params}), WeeklyHours(Decimal(45))
    )
    assert swapped.parameters.hourly_divisor.periods[0].value is None


def _divisor(week: int) -> WeekDivisor:
    rules = _ccnl().work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    provenance = rules.time_supplements.week_divisors[0].provenance
    return WeekDivisor(weekly_hours=week, divisor=Decimal(182), provenance=provenance)


@pytest.mark.parametrize(
    ("own", "weeks"),
    [(None, (42,)), (40, (40,)), (40, (42, 42))],
)
def test_week_divisors_need_the_ccnl_week_and_distinct_weeks(
    own: int | None, weeks: tuple[int, ...]
) -> None:
    """Without the CCNL week, with it again, or one week twice: rejected."""
    with pytest.raises(ValidationError, match="week_divisors"):
        TimeSupplements(
            hourly_divisor_weekly_hours=own,
            week_divisors=tuple(_divisor(w) for w in weeks),
        )


def test_distinct_week_divisors_are_accepted() -> None:
    """40 for the CCNL divisor, 42 and 45 apart."""
    supplements = TimeSupplements(
        hourly_divisor_weekly_hours=40, week_divisors=(_divisor(42), _divisor(45))
    )
    assert [w.weekly_hours for w in supplements.week_divisors] == [42, 45]
