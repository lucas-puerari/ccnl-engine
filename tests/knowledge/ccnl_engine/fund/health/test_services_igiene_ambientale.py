"""Igiene ambientale art. 65 lett. B: FASDA, 84.50 EUR a quarter, then 101.

"A decorrere dal versamento trimestrale del 16 ottobre 2023 [...] € 84,50 per
ogni lavoratore dipendente" and, from 1 October 2026, "5,50 euro per 12
mensilità (16,50 euro trimestrali)" more (2025 consolidated text and ipotesi
of 9 December 2025, pp. 165-166): 338 and 404 EUR a year on the employer.
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

_HIRED = date(2026, 1, 1)


def _fasda(month: int) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id="igiene-ambientale-utilitalia",
                level_code="C1",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), contractual_funds=frozenset({"fasda"})
            ),
        )
    )
    return {
        e.entry_id.removeprefix("fasda_").split("_")[-1]: e.amount
        for e in result.ledger_entries
        if e.entry_id.startswith("fasda_")
    }


@pytest.mark.parametrize(
    ("month", "employer", "solidarity"),
    [(9, "28.17", "2.82"), (10, "33.67", "3.37")],
)
def test_fasda_charges_a_twelfth_of_the_year(
    month: int, employer: str, solidarity: str
) -> None:
    """338 EUR a year to September 2026, 404 from October, with 10% solidarity."""
    assert _fasda(month) == {
        "er": Decimal(employer),
        "solidarity": Decimal(solidarity),
    }
