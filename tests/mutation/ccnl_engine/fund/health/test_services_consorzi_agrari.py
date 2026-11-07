"""Consorzi agrari art. 37: FILCOOP SANITARIO, 186 EUR a year shared 2:1.

"Il contributo al Fondo è determinato nella misura annua di € 186,00 da
ripartire in ragione di due terzi a carico del Consorzio e di un terzo a
carico del lavoratore" (CCNL 2024-2027, p. 37): 124 and 62 EUR a year, a
twelfth a month, for the permanent workers.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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


def test_filcoop_sanitario_charges_a_twelfth_of_each_share() -> None:
    """10.33 EUR the employer, 5.17 the worker, 10% solidarity on the first."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="consorzi-agrari-assocap",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(30),
                contractual_funds=frozenset({"filcoop_sanitario"}),
            ),
        )
    )

    shares = {
        e.entry_id.removeprefix("filcoop_sanitario_").split("_")[-1]: e.amount
        for e in result.ledger_entries
        if e.entry_id.startswith("filcoop_sanitario_")
    }
    assert shares == {
        "er": Decimal("10.33"),
        "emp": Decimal("5.17"),
        "solidarity": Decimal("1.03"),
    }
