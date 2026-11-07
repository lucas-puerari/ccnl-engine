"""Calzaturiero apprentices take the scatti of their level at their percentage.

Art. 23 (p. 52 of the CCNL 17 July 2024): "L'anzianità durante il rapporto di
apprendistato è utile per la maturazione e per la corresponsione degli
aumenti periodici di anzianità. Gli aumenti saranno commisurati alle stesse
percentuali del minimo contrattuale."  Level 6: 9.94 a triennio; 40 months
of seniority, one triennio: 80% in months 0-9 (7.95), 90% in months 10-19
(8.946 -> 8.95), 100% from month 20 (9.94).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import (
    Apprentice,
    EmploymentPeriod,
    NoPensionFund,
    SeniorityFact,
    SenioritySource,
)


def _seniority(months_elapsed: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="calzaturiero-assocalzaturifici",
                level_code="6",
                contract_type=Apprentice(months_elapsed=months_elapsed),
                employment_period=EmploymentPeriod(date(2022, 11, 1), None),
                seniority=SeniorityFact(
                    40, date(2026, 3, 1), SenioritySource.EMPLOYER_RECORDS
                ),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("months_elapsed", "amount"), [(5, "7.95"), (15, "8.95"), (25, "9.94")]
)
def test_the_scatto_follows_the_apprenticeship_percentage(
    months_elapsed: int, amount: str
) -> None:
    """One triennio at level 6, at 80%, 90% and 100%."""
    assert _seniority(months_elapsed) == Decimal(amount)
