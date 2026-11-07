"""When the trattamento integrativo speciale applies and on what base.

L. 199/2025 art. 1 cc. 18-20: 15% of the gross pay of night work and holiday
overtime, 1 January - 30 September 2026, food service, tourism and thermal
establishments, private sector, 2025 income up to 40,000, on request.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.regime.models import EmployerActivity, EmploymentSector
from ccnl_engine.regime.requirement.rules import RegimeFacts
from ccnl_engine.working_time.inputs import (
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftKind,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.tourism.rules import SpecialSupplement, special_supplement

_FACTS = RegimeFacts(
    prior_income=Decimal(30_000),
    activity=EmployerActivity.TOURISM,
    special_supplement=True,
)
_DAY = date(2026, 3, 10)
_RATE = CalculationDecision(
    capability="night_work",
    status=CalculationStatus.FINAL,
    reason_code="ccnl_supplement_applied",
    rule="r",
    rule_version="2026",
    inputs={"hourly_base_rate": Decimal(10)},
    amount=Decimal(15),
)
_NIGHT = NightShiftEvent(_DAY, hours=Decimal(6))


def _run(event: object, facts: RegimeFacts = _FACTS) -> SpecialSupplement | None:
    return special_supplement(event, Decimal(15), (_RATE,), facts)


def test_night_hours_pay_15_percent_of_hour_and_premium() -> None:
    """6 h x 10 + 15 = 75, 15% = 11.25."""
    assert _run(_NIGHT) == SpecialSupplement("paid", Decimal("11.25"), Decimal(75))


@pytest.mark.parametrize(
    "event",
    [
        OvertimeEvent(_DAY, Decimal(2), kind=OvertimeKind.HOLIDAY),
        OvertimeEvent(_DAY, Decimal(2), kind=OvertimeKind.NIGHT),
        OvertimeEvent(_DAY, Decimal(2), kind=OvertimeKind.NIGHT_HOLIDAY),
    ],
)
def test_holiday_and_night_overtime_pay_on_their_gross(event: OvertimeEvent) -> None:
    """The overtime gross, 15 here, the hour included: 2.25."""
    assert _run(event) == SpecialSupplement("paid", Decimal("2.25"), Decimal(15))


@pytest.mark.parametrize(
    "event",
    [
        OvertimeEvent(_DAY, Decimal(2)),
        OvertimeEvent(_DAY, Decimal(2), kind=OvertimeKind.REST_DAY),
        HolidayWorkEvent(_DAY, hours=Decimal(8)),
        ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY),
        NightShiftEvent(date(2025, 12, 31), hours=Decimal(6)),
        NightShiftEvent(date(2026, 10, 1), hours=Decimal(6)),
        "not an event",
    ],
)
def test_other_work_and_dates_outside_the_window_pay_none(event: object) -> None:
    """Weekday or rest-day overtime, daytime work, before 2026 or after 30/9."""
    assert _run(event) is None


@pytest.mark.parametrize(
    "event",
    [
        HolidayWorkEvent(_DAY, hours=Decimal(6), kind=HolidayWorkKind.NIGHT_HOLIDAY),
        ShiftWorkEvent(_DAY, hours=Decimal(6), kind=ShiftKind.NIGHT),
        NightShiftEvent(date(2026, 1, 1), hours=Decimal(6)),
        NightShiftEvent(date(2026, 9, 30), hours=Decimal(6)),
    ],
)
def test_ordinary_night_work_counts(event: object) -> None:
    """Night holiday hours and night shifts, the first and last day."""
    found = _run(event)
    assert found is not None
    assert found.reason == "paid"


@pytest.mark.parametrize(
    "facts",
    [
        replace(_FACTS, special_supplement=False),
        replace(_FACTS, withholding_agent=False),
        replace(_FACTS, sector=EmploymentSector.PUBLIC),
        replace(_FACTS, activity=EmployerActivity.OTHER),
    ],
)
def test_no_request_or_out_of_scope_pays_none(facts: RegimeFacts) -> None:
    """No request, no withholding agent, public sector, another activity."""
    assert _run(_NIGHT, facts) is None


@pytest.mark.parametrize(
    ("facts", "reason"),
    [
        (replace(_FACTS, activity=None), "activity_unknown"),
        (replace(_FACTS, prior_income=None), "income_unknown"),
        (replace(_FACTS, prior_income=Decimal("40000.01")), "income_above_cap"),
    ],
)
def test_what_stops_it(facts: RegimeFacts, reason: str) -> None:
    """An unknown activity or income, or an income above 40,000."""
    assert _run(_NIGHT, facts) == SpecialSupplement(reason)


def test_forty_thousand_is_within_the_cap() -> None:
    """'non superiore [...] a 40.000 euro'."""
    found = _run(_NIGHT, replace(_FACTS, prior_income=Decimal(40_000)))
    assert found is not None
    assert found.reason == "paid"


def test_night_hours_without_hours_or_rate_have_no_base() -> None:
    """A caller-supplied amount without hours, or no hourly base."""
    no_hours = NightShiftEvent(_DAY, supplement_amount=Decimal(15))
    assert _run(no_hours) == SpecialSupplement("base_unknown")
    assert special_supplement(_NIGHT, Decimal(15), (), _FACTS) == SpecialSupplement(
        "base_unknown"
    )
