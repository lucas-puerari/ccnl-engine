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
    assert set(ordinary) == {"holiday", "night", "night_holiday"}
    for work, expected in (("holiday", holiday), ("night", night)):
        premium = ordinary[work].rate.period_at(date(2026, 3, 10))
        assert premium is not None
        assert premium.value is not None
        assert Decimal(8) * Decimal(10) * premium.value == Decimal(expected)


@pytest.mark.parametrize(
    ("subsector", "overtime", "holiday", "night"),
    [
        ("agricoli", "25.00", "24.17", "27.62"),
        ("florovivaisti", "25.80", "27.62", "33.14"),
    ],
)
def test_period_routes_all_three_events(
    subsector: str, overtime: str, holiday: str, night: str
) -> None:
    """With national Area1 fallback EUR 1533 / 169, 8h at 35/40/48%.

    The event explicitly states EUR 10/hour for its two overtime hours.
    Provincial wages may differ from the national fallback.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector=subsector),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area1",
            opening_state=PeriodState.zero(),
            events=(
                OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal(10)),
                HolidayWorkEvent(date(2026, 3, 19), hours=Decimal(8)),
                NightShiftEvent(date(2026, 3, 20), hours=Decimal(8)),
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
