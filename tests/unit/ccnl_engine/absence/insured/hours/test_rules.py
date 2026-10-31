"""The pay of the hours of a leave, each at the hourly base of its day."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.hours.rules import hours_pay

if TYPE_CHECKING:
    from ccnl_engine.working_time.hourly.policies import HourlyTerms


def test_each_hour_asks_the_base_of_its_day_for_its_capability() -> None:
    """3 + 2.5 hours at 12.00 within the span; the hour after it is left out."""
    asked: list[tuple[date, str, str]] = []

    def base(day: date, field: str, capability: str) -> SimpleNamespace:
        asked.append((day, field, capability))
        return SimpleNamespace(rate=Decimal(12))

    hourly = cast("HourlyTerms", SimpleNamespace(base=base))
    items = (
        LeaveHours(date(2026, 3, 2), Decimal(3)),
        LeaveHours(date(2026, 3, 3), Decimal("2.5")),
        LeaveHours(date(2026, 4, 1), Decimal(1)),
    )
    span = (date(2026, 3, 1), date(2026, 3, 31))

    assert hours_pay(items, span, hourly, "nursing_rest", "code") == Decimal(66)
    assert asked == [
        (date(2026, 3, 2), "the hourly base of LeaveHours.hours", "nursing_rest"),
        (date(2026, 3, 3), "the hourly base of LeaveHours.hours", "nursing_rest"),
    ]
