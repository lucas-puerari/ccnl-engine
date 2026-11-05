"""Multiservizi art. 66: the ONBSI shares, reduced below 20 weekly hours.

"l'ONBSI è finanziato mediante l'attribuzione di un contributo stabilito
nella misura di € 0,50 a carico del datore di lavoro e di € 0,50 a carico del
lavoratore mensili, per 12 mensilità [...] Per i lavoratori a part-time
inferiore a 20 ore settimanali gli importi di cui sopra sono ridotti a €
0,25" (ipotesi 8 giugno 2021, CNEL 139292, p. 29).
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
    WeeklyHours,
)

_HIRED = date(2026, 1, 1)


def _onbsi(hours: int) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="multiservizi-anip",
                level_code="3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=WeeklyHours(Decimal(hours)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), contractual_funds=frozenset({"onbsi", "asim"})
            ),
        )
    )
    return {
        e.entry_id.removeprefix("onbsi_").split("_")[-1]: e.amount
        for e in result.ledger_entries
        if e.entry_id.startswith("onbsi_")
    }


@pytest.mark.parametrize(("hours", "share"), [(40, "0.50"), (20, "0.50"), (19, "0.25")])
def test_the_onbsi_shares_halve_below_twenty_hours(hours: int, share: str) -> None:
    """0.50 + 0.50 a month, 0.25 + 0.25 below 20 weekly hours."""
    assert _onbsi(hours) == {"er": Decimal(share), "emp": Decimal(share)}
