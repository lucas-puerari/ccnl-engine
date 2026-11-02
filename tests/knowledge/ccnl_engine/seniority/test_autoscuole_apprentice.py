"""Autoscuole apprentices accrue the scatti of their level (p. 50, punto 5 h).

"L'intero periodo di apprendistato professionalizzante è utile ai fini della
maturazione dell'anzianità aziendale, anche ai fini degli aumenti periodici di
anzianità; tali aumenti saranno corrisposti nelle misure previste dal livello
di appartenenza." Art. 17: level 3 14,98, level 2 14,46 a biennium.
Destination level 3, hired January 2023: one biennium by March 2026.
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

_HIRED = date(2023, 1, 1)


def _seniority(months: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="autoscuole-unasca",
                level_code="3",
                contract_type=Apprentice(months_elapsed=months),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(5),
                contractual_funds=frozenset({"fondo_est", "ente_bilaterale"}),
            ),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(("months", "amount"), [(38, "14.98"), (20, "14.46")])
def test_the_apprentice_takes_the_scatto_of_his_level(months: int, amount: str) -> None:
    """Third period at level 3; second period one level below, at level 2."""
    assert _seniority(months) == Decimal(amount)
