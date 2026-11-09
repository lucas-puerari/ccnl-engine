"""Art. 14(2): 2 hours at EUR 10 inside = EUR 20, not EUR 25.

Outside the adopted arrangement, 2 daytime hours = 2 x 10 x 1.25 =
EUR 25; 2 night hours (22:00-06:00) = 2 x 10 x 1.50 = EUR 30.
The caller splits hours at the boundary of the written arrangement.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.pay_item.facade import OvertimeEarning

_DAY = date(2026, 3, 10)
_START = date(2026, 1, 1)


def _pay(*kinds: OvertimeKind) -> tuple[Decimal, set[str]]:
    events = tuple(OvertimeEvent(_DAY, Decimal(2), Decimal(10), kind=k) for k in kinds)
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="lavoro-domestico-convivente-orario-ridotto",
                level_code="B",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_START, None),
                seniority=SeniorityFact.since(_START, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                weekly_hours=WeeklyHours(Decimal(20)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(100)), events=events
            ),
        )
    )
    amount = sum(
        (item.amount for item in result.pay_items if isinstance(item, OvertimeEarning)),
        Decimal(0),
    )
    bands = {
        str(decision.inputs["band_code"])
        for decision in result.decisions
        if decision.reason_code == "ccnl_overtime_band_applied"
    }
    return amount, bands


@pytest.mark.parametrize(
    ("kind", "amount", "band"),
    [
        (OvertimeKind.SUPPLEMENTARY, "20.00", "OT_IN_ARRANGEMENT"),
        (OvertimeKind.WEEKDAY, "25.00", "OT_DIURNO"),
        (OvertimeKind.NIGHT, "30.00", "OT_NOTTURNO"),
        (OvertimeKind.HOLIDAY, "32.00", "OT_FESTIVO"),
    ],
)
def test_extra_hours_use_the_adopted_arrangement_and_time_band(
    kind: OvertimeKind, amount: str, band: str
) -> None:
    """At EUR 10/hour, two hours pay 20 plain, 25 day, 30 night or 32 holiday."""
    assert _pay(kind) == (Decimal(amount), {band})


def test_hours_crossing_the_arrangement_boundary_are_split() -> None:
    """Two inside and two outside at night pay 20 + 30 = EUR 50, not 60."""
    assert _pay(OvertimeKind.SUPPLEMENTARY, OvertimeKind.NIGHT) == (
        Decimal("50.00"),
        {"OT_IN_ARRANGEMENT", "OT_NOTTURNO"},
    )
