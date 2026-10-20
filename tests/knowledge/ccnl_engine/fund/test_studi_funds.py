"""Hand oracle: the funds of the Studi professionali (Confprofessioni).

4th level impiegato, June 2026, INPS base 1,595 EUR.

- Fondo di solidarietà bilaterale per le attività professionali (D.I. 21 May
  2024 art. 6): 0.50%, 0.80% and 1% by headcount, two thirds employer, in
  place of the FIS and the CIGS of the terziario rates.  Above 15 employees
  the worker pays 9.19% IVS plus 0.33333% (9.52%), the employer 29.65%
  instead of 30.11%.
- CADIPROF (Art. 13): 20 EUR a month of the employer, a health fund (2 EUR
  INPS solidarity); EBIPRO: 7 EUR of the employer and 2 of the worker; both
  in full for a part-timer.  An employer outside the bilateral system owes
  one element of 43 EUR for 14 months, not reproportioned, in the TFR base.
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
    PeriodResult,
)
from ccnl_engine.inputs import (
    Apprentice,
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2026, 1, 1)
_BOTH = frozenset({"cadiprof", "ebipro"})


def _run(
    funds: frozenset[str] = _BOTH,
    *,
    headcount: int = 60,
    contract: Apprentice | None = None,
    hours: int | None = None,
    fourteenth: bool = False,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.fourteenth(2026, 6)
            if fourteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="studi-professionali-confprofessioni",
                level_code="4",
                contract_type=contract or Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
                full_time_weekly_hours=None
                if hours is None
                else WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(headcount), contractual_funds=funds
            ),
        )
    )


def _rates(result: PeriodResult) -> dict[str, Decimal]:
    return {c.name: c.rate for c in result.contribution_breakdown.components}


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def _elements(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if "_element_" in i.item_id]


@pytest.mark.parametrize(
    ("headcount", "employee", "employer"),
    [
        (5, Decimal("0.0016667"), Decimal("0.0550333")),
        (15, Decimal("0.0026667"), Decimal("0.0570333")),
        (60, Decimal("0.0033333"), Decimal("0.0583667")),
    ],
)
def test_the_fund_replaces_the_fis_and_the_cigs(
    headcount: int, employee: Decimal, employer: Decimal
) -> None:
    """Up to 15 employees the terziario thirds; above, the 1% of the fund."""
    rates = _rates(_run(headcount=headcount))

    assert rates["ivs_employee"] == Decimal("0.0919")
    assert rates["non_ivs_employee"] == employee
    assert rates["ivs_employer"] + rates["non_ivs_employer"] == (
        Decimal("0.2381") + employer
    )


def test_an_apprentice_owes_the_fund_in_place_of_the_fis_and_the_cigs() -> None:
    """Above 15: NASpI 1.61% plus 0.66667% of the employer, 0.33333% of the worker."""
    rates = _rates(
        _run(contract=Apprentice(months_elapsed=6, track="professionalizzante_36"))
    )

    assert rates["non_ivs_employee"] == Decimal("0.0033333")
    assert rates["non_ivs_employer"] == Decimal("0.0161") + Decimal("0.0066667")


def test_an_employer_in_the_bilateral_system_pays_both_funds() -> None:
    """CADIPROF 20 + 2 solidarity, EBIPRO 7 + 2 of the worker; no element."""
    result = _run()

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("27.00")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("2.00")
    solidarity = [
        e.amount for e in result.ledger_entries if e.entry_id.endswith("_solidarity")
    ]
    assert solidarity == [Decimal("2.00")]
    assert _elements(result) == []


def test_a_part_timer_owes_the_shares_in_full() -> None:
    """20 of 40 hours: the 29 EUR stay whole."""
    result = _run(hours=20)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("27.00")


@pytest.mark.parametrize("funds", [frozenset(), frozenset({"ebipro"})])
def test_an_employer_outside_the_system_owes_one_element(
    funds: frozenset[str],
) -> None:
    """43 EUR once, on the 14th too and whole for a part-timer."""
    assert _elements(_run(funds)) == [Decimal("43.00")]
    assert _elements(_run(funds, fourteenth=True)) == [Decimal("43.00")]
    assert _elements(_run(funds, hours=20)) == [Decimal("43.00")]


def test_ebipro_needs_the_employer_to_state_it() -> None:
    """EBIPRO has the element of CADIPROF: unstated, neither is posted."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="studi-professionali-confprofessioni",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(60)),
        )
    )

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal(0)
    assert {i.code for i in result.issues} >= {"contractual_funds_unknown"}
