"""Farmacie private Tabella C: the ISQ of Q2 and Q3 rises after 12 years.

"Q2 + 12 anni (*) € 130,00 / Q2 + 2 anni (*) € 100,00 [...] (*) Anzianità
complessiva maturata nel Livello 1° e nell'Area Q" (CCNL 7 September 2021,
p. 59), read on the months of service: 100 EUR up to 144, 130 EUR after.
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


def _isq(hired: date) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="farmacie-private-h121",
                level_code="Q3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
        )
    )
    return {
        i.item_id.removeprefix("allowance_").split("_2026")[0]: i.amount
        for i in result.pay_items
        if i.item_id.startswith("allowance_isq")
    }


@pytest.mark.parametrize(
    ("hired", "code", "amount"),
    [(date(2016, 1, 1), "isq", "100.00"), (date(2013, 1, 1), "isq_12", "130.00")],
)
def test_the_isq_follows_the_twelve_years(hired: date, code: str, amount: str) -> None:
    """Ten years of service pay 100 EUR, thirteen pay 130 EUR."""
    (paid,) = _isq(hired).items()
    assert paid == (code, Decimal(amount))
