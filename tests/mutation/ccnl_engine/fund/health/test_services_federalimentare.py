"""Hand oracle: the bilateralità of the Industria alimentare (art. 74 quinquies).

FLAI text of the CCNL 2023-2027 (sha256 11792ad3…, PDF p. 158): EUR 2 a
month plus EUR 0.50 from 1 January 2025 for each permanent worker; the
prima dichiarazione comune sets EUR 1.50 in place of the 2 for a company
with better union-leave terms, so 2.00 from 2025.  June 2026, level 5,
FASA 16, Cassa maternità 4.50, Cassa rischio vita 30 / 12 = 2.50.
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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2024, 1, 1)
_OTHERS = frozenset({"fasa", "cassa_maternita", "rischio_vita"})


def _employer_funds(funds: frozenset[str], year: int) -> list[Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, 6),
            payment_date=date(year, 6, 27),
            employment=Employment(
                ccnl_id="alimentari-federalimentare",
                level_code="5",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), contractual_funds=funds, subsector="carni"
            ),
        )
    )
    return [
        e.amount
        for e in result.ledger_entries
        if e.account is AccountKind.BILATERAL_FUND_EMPLOYER
    ]


@pytest.mark.parametrize(
    ("bilateral", "amount"),
    [
        ("bilateralita", Decimal("2.50")),
        ("bilateralita_aspettativa_sindacale", Decimal("2.00")),
    ],
)
def test_the_bilateralita_of_2026(bilateral: str, amount: Decimal) -> None:
    """2 + 0.50, or 1.50 + 0.50 with better union-leave terms."""
    funds = _OTHERS | {bilateral}
    assert _employer_funds(funds, 2026) == [
        Decimal("16.00"),
        Decimal("4.50"),
        Decimal("2.50"),
        amount,
    ]


def test_the_reduced_bilateralita_of_2024() -> None:
    """Before the 0.50 of 2025: EUR 1.50."""
    (fund,) = (
        f
        for f in load_ccnl("alimentari-federalimentare").parameters.health_funds
        if f.code == "bilateralita_aspettativa_sindacale"
    )
    assert fund.employer.monthly is not None
    assert fund.employer.monthly.value_at(date(2024, 12, 31)) == Decimal("1.50")
    assert fund.group == "bilateralita"


def test_naming_no_way_pays_no_bilateralita() -> None:
    """The employer names one way of the group; naming none pays neither."""
    assert len(_employer_funds(_OTHERS, 2026)) == 3
