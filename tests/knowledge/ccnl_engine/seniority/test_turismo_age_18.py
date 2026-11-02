"""The Turismo scatti count the service after age 18 (Art. 158 c. 2, p. 140).

"L'anzianità utile ai fini della maturazione del primo scatto di anzianità è:
- quella maturata successivamente al compimento del diciottesimo anno di età
per il personale assunto a partire dal 1° giugno 1986". Level 4, hired
1 September 2019, March 2026: 78 months from the hire, two triennial scatti
of 33.05; born 10 May 2003, 57 months from the eighteenth birthday, one.
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
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

_HIRED = date(2019, 9, 1)


def _seniority(birth: date | None) -> Decimal:
    fact = SeniorityFact(
        months=0,
        as_of=_HIRED,
        source=SenioritySource.EMPLOYER_RECORDS,
        birth_date=birth,
    )
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="turismo-federalberghi",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=fact,
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("birth", "amount"),
    [(None, "66.10"), (date(2000, 1, 1), "66.10"), (date(2003, 5, 10), "33.05")],
)
def test_a_young_hire_counts_from_the_eighteenth_birthday(
    birth: date | None, amount: str
) -> None:
    """Two scatti from the hire; one from 10 May 2021."""
    assert _seniority(birth) == Decimal(amount)
