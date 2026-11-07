"""Hand oracle: mètaSalute and the flexible benefits of Federmeccanica.

- mètaSalute (CCNL 5 February 2021, art. 16, p. 184): 156 EUR a year in 12
  monthly shares of 13 EUR from the employer; with the 10% INPS solidarity
  171.60 a year (Ministry of Labour cost table, DD 82/2026).
- Flexible benefits (ipotesi 22 November 2025, p. 3): 250 EUR a year made
  available by February in 2026 and by 1 June from 2027, an employer cost
  outside the pay, not reproportioned for part time (CCNL 2021, p. 185).
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

_HIRED = date(2026, 1, 1)
_FUNDS = frozenset({"metasalute", "flexible_benefits"})


def _run(month: int, funds: frozenset[str] = _FUNDS) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(60), contractual_funds=funds),
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def test_february_2026_makes_the_flexible_benefits_available() -> None:
    """13 EUR to mètaSalute, 1.30 solidarity, and the 250 EUR of welfare."""
    result = _run(2)
    solidarity = [
        e.amount for e in result.ledger_entries if e.entry_id.endswith("_solidarity")
    ]

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("13.00")
    assert _posted(result, AccountKind.NON_CASH_BENEFITS) == Decimal("250.00")
    assert solidarity == [Decimal("1.30")]


def test_the_ccnl_owes_them_whatever_the_employer_states() -> None:
    """No alternative element: posted even when the employer names neither."""
    stated, unstated = _run(2), _run(2, frozenset())

    assert unstated.period_employer_cost == stated.period_employer_cost
    assert unstated.period_net == stated.period_net


def test_another_month_pays_metasalute_only() -> None:
    """June 2026: 13 EUR and 1.30, no welfare."""
    result = _run(6)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("13.00")
    assert _posted(result, AccountKind.NON_CASH_BENEFITS) == 0
