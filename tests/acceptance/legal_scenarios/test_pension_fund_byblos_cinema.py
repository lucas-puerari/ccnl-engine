"""Byblos on the CCNL Esercizi cinematografici, on twelve monthly payments.

Art. 43: "una contribuzione percentuale mensile per 12 mensilità annue a
carico delle aziende ed una contribuzione percentuale mensile per 12
mensilità annue a carico del lavoratore dell'1% della retribuzione
contrattuale".

Level 3 in January 2026, seniority since 1 January 2022: 1383.48 minimum +
two scatti of 16.34 = 1416.16.  Employer and employee 1% = 14.1616 ->
14.16; solidarity 10% of 14.16 = 1.416 -> 1.42.  The tredicesima and the
quattordicesima owe none.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment
from ccnl_engine.inputs import (
    PensionFundEnrolment,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period
from tests.fixtures.current_year import employment_only

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_EMPLOYMENT = Employment(
    ccnl_slug="esercizi-cinematografici-anec.json",
    level_code="3",
    seniority=SeniorityFact.since(date(2022, 1, 1), SenioritySource.EMPLOYER_RECORDS),
    pension_fund=PensionFundEnrolment("BYBLOS", Decimal("0.01"), tfr_to_fund=True),
    contract_type=Permanent(),
)


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def test_monthly_payment_on_the_minimum_and_the_scatti() -> None:
    """1416.16 x 1% = 14.16 employer and employee, 1.42 solidarity."""
    result = regular_period(employment=_EMPLOYMENT, current_year=employment_only())
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["base"] == Decimal("1416.16")
    assert _entry(result, "pension_fund_employer") == Decimal("14.16")
    assert _entry(result, "pension_fund_employee") == Decimal("14.16")
    assert decision.inputs["solidarity"] == Decimal("1.42")


def test_extra_months_owe_none() -> None:
    """12 mensilità: the extra-month runs have a zero base."""
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    extra = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind in {"thirteenth", "fourteenth"}
    ]
    assert len(extra) == 2
    for result in extra:
        (decision,) = [
            d for d in result.decisions if d.capability == "pension_fund_contribution"
        ]
        assert decision.reason_code == "enrolled"
        assert decision.inputs["base"] == 0
        assert _entry(result, "pension_fund_employer") == 0
        assert _entry(result, "pension_fund_employee") == 0
