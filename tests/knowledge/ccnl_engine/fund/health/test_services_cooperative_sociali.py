"""Cooperative sociali art. 87: the health contribution of 10 EUR a month.

"è dovuto un contributo per ogni lavoratore a carico dell'impresa pari a 5 €
mensili [...] A partire dal 1° gennaio 2025, il contributo [...] viene
incrementato di ulteriori 5 € mensili" (2025 coordinated text, p. 114), for
the workers "assunti a tempo indeterminato".
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
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

_HIRED = date(2026, 1, 1)


def _shares(contract: Permanent | FixedTerm) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="cooperative-sociali",
                level_code="C1",
                contract_type=contract,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(30),
                contractual_funds=frozenset({"sanita_integrativa"}),
            ),
        )
    )
    return {
        e.entry_id.removeprefix("sanita_integrativa_").split("_")[-1]: e.amount
        for e in result.ledger_entries
        if e.entry_id.startswith("sanita_integrativa_")
    }


@pytest.mark.parametrize(
    ("contract", "shares"),
    [
        (Permanent(), {"er": Decimal("10.00"), "solidarity": Decimal("1.00")}),
        (FixedTerm(renewals=0), {}),
    ],
)
def test_the_contribution_is_owed_on_a_permanent_contract(
    contract: Permanent | FixedTerm, shares: dict[str, Decimal]
) -> None:
    """10 EUR on the employer with its 10% solidarity; none on a fixed term."""
    assert _shares(contract) == shares
