"""INPS 2026 table A: effective hourly pay selects the live-in contribution band.

With 20 weekly hours (86.6667 per month), a full-time-scale B worker has
(983.16 + 199.80) / (20 * 52 / 12) * 13 / 12 = 14.79 effective EUR/hour,
above 11.70: contribution EUR 2.34/hour (worker 0.59). Reduced-hours B has
(702.25 + 199.80) / (20 * 52 / 12) * 13 / 12 = 11.28, between 9.61 and
11.70: EUR 1.92/hour (worker 0.48). INPS circ. 9/2026, table A, PDF p. 3;
CCNL domestic 2026 tables B and F, signed PDF p. 59.
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
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    ("agreement", "gross", "worker", "employer"),
    [
        ("lavoro-domestico-convivente", "983.16", "0.59", "1.75"),
        ("lavoro-domestico-convivente-orario-ridotto", "702.25", "0.48", "1.44"),
    ],
)
def test_bundled_live_in_hourly_inps_band(
    agreement: str, gross: str, worker: str, employer: str
) -> None:
    """The 14.79 and 11.28 effective rates select the third and second bands."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 20),
            employment=Employment(
                ccnl_id=agreement,
                level_code="B",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(Decimal(20)),
                roles=frozenset(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(20 * 52) / 12)
            ),
        )
    )
    assert result.period_gross == Decimal(gross)
    assert {
        component.name: component.rate
        for component in result.contribution_breakdown.components
    } == {
        "domestic_employee_per_hour": Decimal(worker),
        "domestic_employer_per_hour": Decimal(employer),
    }
