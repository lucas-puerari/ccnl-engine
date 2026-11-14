"""The Distribuzione cooperativa scatti count the service from age 21.

Art. 182 c. 1 (testo ufficiale 2011, p. 195): "Per l'anzianità di servizio
maturata, a decorrere dal 21° anno di età, presso la stessa azienda [...] il
personale avrà diritto a dieci scatti triennali". Level 4, hired 1 September
2019, March 2026: 78 months from the hire, two triennial scatti of 19.93;
born 10 May 2001, 46 months from the twenty-first birthday, one.
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
                ccnl_id="distribuzione-cooperativa-ancc",
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
    [(None, "39.86"), (date(1990, 1, 1), "39.86"), (date(2001, 5, 10), "19.93")],
)
def test_a_young_hire_counts_from_the_twenty_first_birthday(
    birth: date | None, amount: str
) -> None:
    """Two scatti from the hire; one from 10 May 2022."""
    assert _seniority(birth) == Decimal(amount)
