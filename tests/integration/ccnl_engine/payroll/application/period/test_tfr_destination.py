"""Fondo Tesoreria destination of the TFR, through the period calculation.

L. 296/2006 art. 1 c. 756 (Normattiva, text in force from 12-8-2026) has
the employers it names pay the TFR not destined to a pension fund to the
Fondo of c. 755, net of the L. 297/1982 contribution; DM 30 gennaio 2007
art. 1 c. 5 excludes domestic employers and INPS circ. 70/2007 par. 2
lett. a the public administrations of D.Lgs. 165/2001.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import ContributableHours, WeeklyHours
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.period import PeriodResult

_DOMESTIC: dict[str, object] = {
    "ccnl_slug": "lavoro-domestico-convivente.json",
    "level_code": "A",
    "weekly_hours": WeeklyHours(40),
    "contributable_hours": ContributableHours(Decimal(173)),
}
_PUBLIC: dict[str, object] = {
    "ccnl_slug": "dirigenza-funzioni-centrali-aran.json",
    "level_code": "SECONDA_FASCIA",
}
_METALMECCANICO: dict[str, object] = {
    "ccnl_slug": "metalmeccanico-federmeccanica.json",
    "level_code": "C3",
}


def _run(contract: dict[str, object], **kwargs: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employer=EmployerProfile(headcount=Headcount(60)),
            seniority=new_hire(),
            **contract,  # type: ignore[arg-type]
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _tfr(result: PeriodResult) -> CalculationDecision:
    (decision,) = (d for d in result.decisions if d.capability == "tfr")
    return decision


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_treasury_fund_takes_the_quota_net_of_the_deduction() -> None:
    """The same amount as in the company, posted to the Fondo account."""
    company = _run(_METALMECCANICO, tfr_treasury_fund=False)
    treasury = _run(_METALMECCANICO, tfr_treasury_fund=True)
    decision = _tfr(treasury)
    assert decision.inputs["treasury_fund"] == "true"
    assert decision.inputs["account"] == AccountKind.TFR_TREASURY_FUND.value
    assert decision.amount == _tfr(company).amount
    posted = [e for e in treasury.ledger_entries if e.account.value.startswith("tfr")]
    assert [(e.account, e.amount) for e in posted] == [
        (AccountKind.TFR_TREASURY_FUND, decision.amount)
    ]
    assert treasury.period_employer_cost == company.period_employer_cost


def test_unknown_destination_posts_to_the_company_with_a_missing_fact() -> None:
    """Not stated: the TFR stays in the company account, with a blocker."""
    result = _run(_METALMECCANICO)
    assert _tfr(result).inputs["treasury_fund"] == "unknown"
    assert _tfr(result).inputs["account"] == AccountKind.TFR_ACCRUAL.value
    assert "tfr_treasury_fund_unknown" in _codes(result)
    assert ("missing_fact", "tfr_treasury_fund") in {
        (b.code.value, b.detail) for b in result.blockers
    }


@pytest.mark.parametrize("contract", [_DOMESTIC, _PUBLIC])
def test_excluded_sector_needs_no_fact(contract: dict[str, object]) -> None:
    """Domestic work and public administrations never pay the Fondo."""
    result = _run(contract)
    assert _tfr(result).inputs["treasury_fund"] == "false"
    assert "tfr_treasury_fund_unknown" not in _codes(result)


@pytest.mark.parametrize("contract", [_DOMESTIC, _PUBLIC])
def test_excluded_sector_rejects_the_fondo(contract: dict[str, object]) -> None:
    """Routing the TFR of an excluded sector to the Fondo is an input error."""
    with pytest.raises(InvalidInputError, match="Fondo Tesoreria") as raised:
        _run(contract, tfr_treasury_fund=True)
    assert raised.value.field == "Employment.tfr_treasury_fund"
