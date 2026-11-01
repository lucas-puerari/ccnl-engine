"""The scatti of Edilizia cooperative ANCPL belong to the impiegati.

Art. 83 (CCNL text 2000, p. 89): "l'impiegato ha diritto, per ogni biennio
d'anzianità [...] a 1 scatto biennale per un massimo di 5 scatti"; the operai
accrue the Anzianità professionale edile of Art. 69 (p. 78) through the Cassa
Edile. Level 4 holds both: hired January 2020, three bienni by March 2026,
3 x 9.62 = 28.86 for the impiegato, nothing for the operaio.
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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

_HIRED = date(2020, 1, 1)


def _seniority(category: WorkerCategory) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="edilizia-cooperative-ancpl",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                category=category,
            ),
            employer=EmployerProfile(headcount=Headcount(30)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("category", "amount"),
    [(WorkerCategory.IMPIEGATO, "28.86"), (WorkerCategory.OPERAIO, "0")],
)
def test_only_the_impiegato_accrues_the_scatti(
    category: WorkerCategory, amount: str
) -> None:
    """Art. 83 for the impiegato; the APE of the Cassa Edile for the operaio."""
    assert _seniority(category) == Decimal(amount)
