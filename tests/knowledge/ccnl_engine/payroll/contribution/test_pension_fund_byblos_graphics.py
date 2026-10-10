"""Byblos on the CCNL grafici editoriali, with the ERC rate.

Byblos, Scheda 'I destinatari e i contributi' (in force from 25/09/2026),
settore grafico-editoriale: worker at least 1%, employer 1.9% for a worker
"al quale non si applica l'ERC" and 1.4% for one "al quale si applica
l'ERC", "sulla retribuzione contrattuale annua" from 1.1.2024.

C1 in January 2026, hired that month: 1954.47.  Without ERC: employer
1954.47 x 1.9% = 37.13493 -> 37.13, solidarity 3.713 -> 3.71.  With ERC:
1954.47 x 1.4% = 27.36258 -> 27.36, solidarity 2.736 -> 2.74.  Employee
1% = 19.5447 -> 19.54 in both cases.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import EmploymentPeriod, PensionFundEnrolment, Permanent
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _january(erc_amount: Decimal | None) -> PeriodResult:
    employment = Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="C1",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("BYBLOS", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
        erc_amount=erc_amount,
    )
    return regular_period(employment=employment, current_year=employment_only())


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _inputs(result: PeriodResult) -> dict[str, object]:
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    return dict(decision.inputs)


@pytest.mark.parametrize(
    ("erc_amount", "employer", "solidarity"),
    [(Decimal(0), "37.13", "3.71"), (Decimal("412.50"), "27.36", "2.74")],
    ids=["without_erc", "erc_holder"],
)
def test_employer_rate_follows_the_erc(
    erc_amount: Decimal, employer: str, solidarity: str
) -> None:
    """1.9% without the ERC, 1.4% with it; the worker pays 1% either way."""
    result = _january(erc_amount)
    inputs = _inputs(result)
    assert inputs["base"] == Decimal("1954.47")
    assert _entry(result, "pension_fund_employer") == Decimal(employer)
    assert _entry(result, "pension_fund_employee") == Decimal("19.54")
    assert inputs["solidarity"] == Decimal(solidarity)
    assert "pension_fund_erc_unknown" not in {i.code for i in result.issues}


def test_unknown_erc_is_a_missing_fact() -> None:
    """Unstated ERC: the 1.9% rate, an incomplete issue, not payable."""
    result = _january(None)
    assert _entry(result, "pension_fund_employer") == Decimal("37.13")
    (issue,) = [i for i in result.issues if i.code == "pension_fund_erc_unknown"]
    assert issue.fact == "erc_amount"
    assert not result.is_payable


def test_no_erc_after_december_2020() -> None:
    """Hired in 2026: no ERC by definition, 1.9% without a missing fact."""
    employment = Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="C1",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(started_on=date(2026, 1, 1)),
        pension_fund=PensionFundEnrolment("BYBLOS", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment, current_year=employment_only())
    assert _entry(result, "pension_fund_employer") == Decimal("37.13")
    assert "pension_fund_erc_unknown" not in {i.code for i in result.issues}
