"""December TFR: revaluation of the fund and Fondo Tesoreria destination.

The October review found the December run of a worker hired before the
year final at 50 and at 60 employees, with the same ``tfr_accrual`` and no
gap: no revaluation (art. 2120 c. 4 c.c.), no substitute tax (D.Lgs.
47/2000 art. 11 cc. 3-4) and no Fondo Tesoreria (L. 296/2006 art. 1 c.
756).  The run must say what it does not know and route the TFR where the
caller says it goes.  ISTAT publishes the December 2026 FOI index in
January 2027, so a fund to revalue keeps the December 2026 run blocked.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import EmployerProfile, Employment, Headcount, PeriodResult
from ccnl_engine.inputs import EmploymentPeriod, TfrFundBalance
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_METALMECCANICO = "metalmeccanico-federmeccanica.json"


def _december(headcount: int, **facts: object) -> PeriodResult:
    employment = Employment(
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        **facts,  # type: ignore[arg-type]
    )
    return regular_period(
        month=12,
        employment=employment,
        employer=EmployerProfile(headcount=Headcount(headcount)),
    )


def _missing_facts(result: PeriodResult) -> set[str]:
    return {b.detail for b in result.blockers if b.code is BlockerCode.MISSING_FACT}


def _revaluation(result: PeriodResult) -> tuple[str, CalculationStatus]:
    (decision,) = (d for d in result.decisions if d.capability == "tfr_revaluation")
    return decision.reason_code, decision.status


@pytest.mark.parametrize("headcount", [50, 60])
def test_december_without_tfr_facts_is_not_payable(headcount: int) -> None:
    """Neither the fund nor its destination is a default: two blockers."""
    result = _december(headcount)
    assert {"tfr_fund", "tfr_treasury_fund"} <= _missing_facts(result)
    assert _revaluation(result) == (
        "required_fact_missing",
        CalculationStatus.INCOMPLETE,
    )
    assert not result.is_payable


def test_fund_to_revalue_waits_for_the_december_index() -> None:
    """With the fund stated, the unpublished index keeps the run blocked."""
    result = _december(
        60,
        tfr_fund=TfrFundBalance(2025, Decimal("15000.00")),
        tfr_treasury_fund=True,
    )
    assert {"tfr_fund", "tfr_treasury_fund"}.isdisjoint(_missing_facts(result))
    assert _revaluation(result) == (
        "price_index_not_published",
        CalculationStatus.INCOMPLETE,
    )
    assert not result.is_payable


def test_fondo_tesoreria_changes_the_account_not_the_cost() -> None:
    """Same quota and employer cost; the posting moves to the Fondo account."""
    fund = TfrFundBalance(2025, Decimal("0.00"))
    company = _december(60, tfr_fund=fund, tfr_treasury_fund=False)
    treasury = _december(60, tfr_fund=fund, tfr_treasury_fund=True)

    def tfr_postings(result: PeriodResult) -> dict[str, Decimal]:
        return {
            e.account.value: e.amount
            for e in result.ledger_entries
            if e.account.value in {"tfr_accrual", "tfr_treasury_fund"}
        }

    (accrued,) = tfr_postings(company).values()
    assert tfr_postings(company) == {"tfr_accrual": accrued}
    assert tfr_postings(treasury) == {"tfr_treasury_fund": accrued}
    assert treasury.period_employer_cost == company.period_employer_cost
    assert _revaluation(treasury) == ("no_opening_fund", CalculationStatus.FINAL)
