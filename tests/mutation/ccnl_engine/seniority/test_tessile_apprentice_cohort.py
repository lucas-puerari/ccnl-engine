"""Hand oracle: the apprentice increment of Tessile moda artigianato, March 2027.

- Art. 67 (CCNL 2017, p. 78): "Apprendisti 5,16 euro" a biennium.
- Renewal of 16 July 2024 (p. 23, punto 14): from 1 January 2025 "6 euro,
  non rapportato alla percentuale di progressione retributiva"; for the
  tessile, abbigliamento, calzaturiero and pulitintolavanderie sectors "Agli
  apprendisti in forza alla data di sottoscrizione [...] continua a trovare
  applicazione la disciplina [...] vigente alla data di assunzione".

Two level 4 apprentices, one biennium matured by March 2027.
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


def _seniority(hired: date, months: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2027, 3),
            payment_date=date(2027, 3, 27),
            employment=Employment(
                ccnl_id="tessile-moda-artigianato-confartigianato",
                level_code="4",
                contract_type=Apprentice(months_elapsed=months),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(5)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("hired", "months", "amount"),
    [
        (date(2024, 7, 16), 32, "5.16"),
        (date(2024, 7, 17), 32, "6.00"),
        (date(2025, 2, 1), 25, "6.00"),
    ],
)
def test_the_apprentices_in_service_at_signature_keep_516(
    hired: date, months: int, amount: str
) -> None:
    """Hired by 16 July 2024: 5.16; later: 6.00."""
    assert _seniority(hired, months) == Decimal(amount)
