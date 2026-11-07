"""Autoferrotranvieri apprentices accrue the scatti after their first 24 months.

Art. 22 c. 9 (p. 150 of the CCNL TPL testo integrato): "L'intero periodo di
apprendistato professionalizzante è utile ai fini della maturazione
dell'anzianità di servizio, con esclusione dei primi 24 mesi ai soli fini
della maturazione degli aumenti periodici di anzianità."  The caller states
the months that count: an apprentice hired in January 2022 has 26 of them
by March 2026, one biennium, 21.46 at level 140; with the first 24 months
counted too it would be two.
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

_HIRED = date(2022, 1, 1)


def _seniority(months: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="autoferrotranvieri-internavigatori",
                level_code="140",
                contract_type=Apprentice(months_elapsed=50),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact(
                    months, date(2026, 3, 1), SenioritySource.EMPLOYER_RECORDS
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


@pytest.mark.parametrize(("months", "amount"), [(26, "21.46"), (22, "0")])
def test_the_apprentice_takes_the_scatti_of_the_level(months: int, amount: str) -> None:
    """26 counting months: one biennium; 22: none yet."""
    assert _seniority(months) == Decimal(amount)
