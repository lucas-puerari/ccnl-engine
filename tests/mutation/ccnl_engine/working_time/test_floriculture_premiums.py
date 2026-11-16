"""Art. 43-44, FLAI 2022-2025 PDF pp. 48-49: two distinct wage tables.

At a stated contractual hourly wage of EUR 10, two overtime hours cost
EUR 25.00 (agricultural) or EUR 25.80 (floriculture). Eight ordinary
holiday hours add EUR 28.00 or EUR 32.00; eight ordinary night hours
add EUR 32.00 or EUR 38.40. The ordinary hour is separate from its premium.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)
from ccnl_engine.working_time.subsector.rules import with_subsector


@pytest.mark.parametrize(
    ("subsector", "overtime", "holiday", "night", "holiday_overtime", "night_holiday"),
    [
        ("agricoli", "25.00", "28.00", "32.00", "28.00", "29.00"),
        ("florovivaisti", "25.80", "32.00", "38.40", "30.00", "31.00"),
    ],
)
def test_hand_computed_hours_by_subsector(
    subsector: str,
    overtime: str,
    holiday: str,
    night: str,
    holiday_overtime: str,
    night_holiday: str,
) -> None:
    """EUR 10/hour: 2h x (1 + overtime premium), 8h x ordinary premium.

    Holiday and night overtime each cost 2h x (1 + the printed premium).
    """
    ccnl, missing = with_subsector(
        load_ccnl("operai-agricoli-florovivaisti"), subsector, WorkerCategory.OPERAIO
    )
    assert not missing
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    bands = CCNLOvertimeBands.of(ccnl, 2026, "Area1")
    for kind, expected in (
        ("weekday", overtime),
        ("holiday", holiday_overtime),
        ("night_holiday", night_holiday),
    ):
        event = OvertimeEvent(
            date(2026, 3, 10), Decimal(2), Decimal(10), kind=OvertimeKind(kind)
        )
        rate = resolve_overtime_rate(event, bands)
        assert rate.derived
        assert rate.multiplier * event.hours * Decimal(10) == Decimal(expected)
    ordinary = {band.work.value: band for band in supplements.supplement_bands}
    shifts = (
        {"night_shift", "night_holiday_shift"}
        if subsector == "agricoli"
        else {"night_shift"}
    )
    assert set(ordinary) == {"holiday", "night", "night_holiday", *shifts}
    for work, expected in (("holiday", holiday), ("night", night)):
        historical = ordinary[work].rate.period_at(date(2022, 6, 1))
        assert historical is not None  # The cited 2022-2025 text starts in 2022.
        premium = ordinary[work].rate.period_at(date(2026, 3, 10))
        assert premium is not None
        assert premium.value is not None
        assert Decimal(8) * Decimal(10) * premium.value == Decimal(expected)


@pytest.mark.parametrize(
    ("subsector", "month", "overtime", "holiday", "night"),
    [
        ("agricoli", 3, "25.00", "24.17", "27.62"),
        ("florovivaisti", 6, "25.80", "29.70", "35.64"),
    ],
)
def test_period_routes_all_three_events(
    subsector: str, month: int, overtime: str, holiday: str, night: str
) -> None:
    """March agricultural Area 1: EUR 1458.61 / 169, 8h at 35/40%.

    June floriculture Area 1 uses its printed EUR 9.28033 hourly floor:
    8 x 9.28033 x .40 = EUR 29.70, x .48 = EUR 35.64.
    The event explicitly states EUR 10/hour for its two overtime hours.
    Provincial wages may differ from the national fallback.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector=subsector),
            period_id=PeriodId(year=2026, month=month),
            payment_date=date(2026, month, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area1",
            opening_state=PeriodState.zero(),
            events=(
                OvertimeEvent(date(2026, month, 10), Decimal(2), Decimal(10)),
                HolidayWorkEvent(date(2026, month, 19), hours=Decimal(8)),
                NightShiftEvent(date(2026, month, 20), hours=Decimal(8)),
            ),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    amounts = {
        decision.capability: decision.amount
        for decision in result.decisions
        if decision.reason_code
        in {
            "ccnl_overtime_band_applied",
            "ccnl_supplement_applied",
        }
    }
    assert amounts == {
        "overtime": Decimal(overtime),
        "holiday_work": Decimal(holiday),
        "night_work": Decimal(night),
    }


@pytest.mark.parametrize(
    ("level", "floor", "premium"),
    [
        ("Area1", "9.28033", "29.70"),
        ("Area2", "8.50259", "27.21"),
        ("Area3", "7.9876", "25.56"),
    ],
)
def test_signed_floriculture_hourly_floor(level: str, floor: str, premium: str) -> None:
    """June Annex 1: 8 holiday hours x printed hourly floor x 40%.

    Area 1: 8 x 9.28033 x .40 = 29.70; Area 2: 27.21;
    Area 3: 25.56, each rounded to cents. No /169 conversion.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector="florovivaisti"),
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code=level,
            opening_state=PeriodState.zero(),
            events=(HolidayWorkEvent(date(2026, 6, 19), hours=Decimal(8)),),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    decision = next(
        d for d in result.decisions if d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(premium)
    assert decision.inputs["hourly_minimum"] == Decimal(floor)
    assert "hourly_divisor" not in decision.inputs


def test_floriculture_overtime_derives_hourly_floor() -> None:
    """Two June Area 1 hours: 2 x EUR 9.28033 x 1.29 = EUR 23.94.

    An unstated overtime hourly rate must use the floriculture table,
    not agricultural monthly EUR 1533 / 169.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector="florovivaisti"),
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area1",
            opening_state=PeriodState.zero(),
            events=(OvertimeEvent(date(2026, 6, 10), Decimal(2)),),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    decision = next(
        d for d in result.decisions if d.reason_code == "ccnl_overtime_band_applied"
    )
    assert decision.amount == Decimal("23.94")


def test_earlier_floriculture_hourly_floor() -> None:
    """Area 1, March 2026: the 2025 Tabella n. 2, never 1458.61 / 169.

    Accordo of 27/10/2023: 8 x 8.83 x .40 = 28.26.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector="florovivaisti"),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area1",
            opening_state=PeriodState.zero(),
            events=(HolidayWorkEvent(date(2026, 3, 19), hours=Decimal(8)),),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    decision = next(
        d for d in result.decisions if d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.inputs["hourly_minimum"] == Decimal("8.83")
    assert decision.amount == Decimal("28.26")


@pytest.mark.parametrize(
    ("day", "floor"),
    [
        (date(2022, 12, 31), None),
        (date(2024, 3, 19), Decimal("8.41")),
        (date(2025, 1, 1), Decimal("8.83")),
        (date(2026, 6, 1), Decimal("9.28033")),
    ],
)
def test_floriculture_hourly_table_by_date(day: date, floor: Decimal | None) -> None:
    """CCNL 23/5/2022, accordo 27/10/2023 and verbale 28/5/2026, Area 1."""
    ccnl, _ = with_subsector(
        load_ccnl("operai-agricoli-florovivaisti"),
        "florovivaisti",
        WorkerCategory.OPERAIO,
    )
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    period = supplements.hourly_minimum_by_level["Area1"].period_at(day)
    assert (None if period is None else period.value) == floor
