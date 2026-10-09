"""Perseo Sirio on the CCNL Funzioni Centrali, with the TFR accrued notionally.

Perseo Sirio, Scheda 'I destinatari e i contributi' (in force from
27/03/2026), dipendenti pubblici: worker 1% and employer 1% "della
retribuzione utile ai fini del calcolo del TFR"; "Le quote di TFR dei
dipendenti pubblici non sono versate al fondo ma sono accantonate
figurativamente presso l'INPS Gestione Dipendenti Pubblici".

Funzionari in January 2026: 2227.99.  Employer and worker 1% = 22.2799 ->
22.28; solidarity 10% of 22.28 = 2.228 -> 2.23.  The tredicesima of 2026
pays 2227.99 and bears the same 22.28.  The TFR conferred is not paid to
the fund: nothing on ``pension_fund_tfr``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment
from ccnl_engine.inputs import PensionFundEnrolment, Permanent, PublicEndOfService
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_EMPLOYMENT = Employment(
    ccnl_slug="funzioni-centrali-aran.json",
    level_code="FUNZIONARI",
    seniority=new_hire(),
    pension_fund=PensionFundEnrolment(
        "PERSEO_SIRIO", Decimal("0.01"), tfr_to_fund=True
    ),
    contract_type=Permanent(),
    public_end_of_service=PublicEndOfService.TFR_INPS,
)


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


def test_one_percent_each_with_the_tfr_notional() -> None:
    """22.28 employer and worker, 2.23 solidarity, the TFR accrued at INPS."""
    result = regular_period(employment=_EMPLOYMENT, current_year=employment_only())
    inputs = _inputs(result)
    assert inputs["base"] == Decimal("2227.99")
    assert _entry(result, "pension_fund_employer") == Decimal("22.28")
    assert _entry(result, "pension_fund_employee") == Decimal("22.28")
    assert inputs["solidarity"] == Decimal("2.23")
    assert inputs["tfr_to_fund"] == "notional"
    assert _entry(result, "pension_fund_tfr") == 0
    assert _entry(result, "tfr_accrual") == 0
    (tfr,) = [d for d in result.decisions if d.capability == "tfr"]
    assert tfr.inputs["account"] == "inps_notional"


def test_tredicesima_bears_the_contribution() -> None:
    """The retribuzione utile ai fini del TFR holds the tredicesima."""
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    (thirteenth,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "thirteenth"
    ]
    assert _entry(thirteenth, "pension_fund_employer") == Decimal("22.28")
    assert _entry(thirteenth, "pension_fund_tfr") == 0
