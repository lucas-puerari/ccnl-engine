"""Thermal establishment funds, level 6, June 2026 ordinary month.

Base 852.62 + contingenza 510.89 = 1363.51; each observatory share
is 0.10% = 1.36 after cent rounding. FONTUR annual 120/24 accrues
10 employer and 2 worker per ordinary month: total 11.36 employer and
3.36 worker (before: 0/0). The one-time enrolment fee is not accrued.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind


def _run(funds: frozenset[str], *, fourteenth: bool = False) -> PeriodResult:
    hired = date(2025, 1, 1)
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.fourteenth(2026, 6)
            if fourteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="aziende-termali-federterme",
                level_code="6",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10), contractual_funds=funds),
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (entry.amount for entry in result.ledger_entries if entry.account is account),
        Decimal(0),
    )


def test_ordinary_month_accrues_both_employer_and_worker_shares() -> None:
    """1363.51 times .001 = 1.36 each; FONTUR 120/12 = 10, 24/12 = 2."""
    result = _run(frozenset({"fontur_terme"}))
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("11.36")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("3.36")


def test_unpaid_health_fund_owes_the_wage_element() -> None:
    """Unpaid FONTUR owes 16 gross; the observatory still costs 1.36 each."""
    result = _run(frozenset())
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("1.36")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("1.36")
    assert any(
        item.item_id.startswith("fontur_terme_element_") and item.amount == Decimal(16)
        for item in result.pay_items
    )


def test_unpaid_health_fund_element_also_applies_to_fourteenth() -> None:
    """The EUR 16 wage element is owed for 14 instalments, not fund shares."""
    result = _run(frozenset(), fourteenth=True)
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == 0
    assert any(
        item.item_id.startswith("fontur_terme_element_") and item.amount == Decimal(16)
        for item in result.pay_items
    )
