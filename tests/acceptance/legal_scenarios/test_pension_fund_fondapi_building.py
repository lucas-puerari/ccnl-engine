"""Fondapi on the CCNL PMI edili Confapi Aniem.

Fondapi, Scheda 'I destinatari e i contributi', CCNL PMI EDILI ED AFFINI:
worker minimum 1.10% and employer 1.10% of the "Retribuzione TFR", plus a
"Contributo mensile di euro 8 (riparametrati su base 100) per tutti i
lavoratori", "aumentato di euro 2,00 a parametro 100 (operaio comune) a
partire dal 1° ottobre 2019": 10 EUR at parametro 100.

The minima of the table of 1 April 2025 follow the parametri 100, 117, 130,
140, 150, 180, 200 of levels 1 to 7 (1087.99 x 1.30 = 1414.387 for level
3): 10.00, 11.70, 13.00, 14.00, 15.00, 18.00, 20.00 EUR a month.

Level 3 in January 2026: 1414.38 minimum + 520.00 contingenza + 10.33 EDR =
1944.71.  Not enrolled: 13.00 employer, solidarity 1.30.  Enrolled at
1.10%: employer 1944.71 x 1.10% = 21.39181 -> 21.39, plus 13.00 = 34.39;
employee 21.39; solidarity 3.439 -> 3.44.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    PensionFundEnrolment,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_EDILI = "edilizia-pmi-confapi-aniem.json"
_PARTIAL = "edilizia-pmi-confapi-aniem/contractual_fund_partial"


def _january(
    pension: PensionFundEnrolment | NoPensionFund | None,
    level: str = "3",
    period: EmploymentPeriod | None = None,
) -> PeriodResult:
    employment = Employment(
        ccnl_slug=_EDILI,
        level_code=level,
        seniority=new_hire(),
        pension_fund=pension,
        contract_type=Permanent(),
        employment_period=period,
    )
    return regular_period(employment=employment, current_year=employment_only())


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _decision_inputs(result: PeriodResult) -> dict[str, object]:
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    return {"reason": decision.reason_code, **decision.inputs}


@pytest.mark.parametrize(
    ("level", "expected"),
    [("1", "10.00"), ("2", "11.70"), ("3", "13.00"), ("7", "20.00")],
)
def test_owed_without_enrolment(level: str, expected: str) -> None:
    """A worker not enrolled is owed 10 EUR riparametrati on the level."""
    result = _january(NoPensionFund(), level)
    assert _decision_inputs(result)["reason"] == "contractual_only"
    assert _entry(result, "pension_fund_employer") == Decimal(expected)
    assert _PARTIAL not in {
        limitation.id for limitation in result.assurance.limitations
    }


def test_added_to_the_ordinary_contributions() -> None:
    """Enrolled at 1.10%: 21.39 + 13.00 = 34.39 employer, 21.39 employee."""
    result = _january(
        PensionFundEnrolment("FONDAPI", Decimal("0.011"), tfr_to_fund=True)
    )
    inputs = _decision_inputs(result)
    assert inputs["contractual"] == Decimal("13.00")
    assert _entry(result, "pension_fund_employer") == Decimal("34.39")
    assert _entry(result, "pension_fund_employee") == Decimal("21.39")
    assert inputs["solidarity"] == Decimal("3.44")


def test_solidarity_on_the_contractual_part() -> None:
    """Not enrolled: the 13.00 bears 10% solidarity, 1.30."""
    result = _january(NoPensionFund())
    assert _decision_inputs(result)["solidarity"] == Decimal("1.30")


def test_partial_month_is_an_open_limitation() -> None:
    """A hire on 15 January: the Scheda gives no rule, full amount."""
    result = _january(
        NoPensionFund(), period=EmploymentPeriod(started_on=date(2026, 1, 15))
    )
    assert _entry(result, "pension_fund_employer") == Decimal("13.00")
    assert _PARTIAL in {limitation.id for limitation in result.assurance.limitations}
    assert not result.is_payable
