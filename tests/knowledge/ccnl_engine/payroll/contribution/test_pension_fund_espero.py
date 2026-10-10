"""Espero on the school CCNL, Perseo Sirio on the other public CCNLs.

Fondo Scuola Espero, Scheda 'I destinatari e i contributi' (in force from
30/07/2026): worker and employer 1% "dei seguenti elementi retributivi:
retribuzione tabellare, indennità integrativa speciale, tredicesima
mensilità e retribuzione professionale"; the TFR "non [è versato] al Fondo
ma [è accantonato] figurativamente presso l'INPS Gestione ex INPDAP".
Perseo Sirio: 1% + 1% of the retribuzione utile ai fini del TFR.

January 2026, hired that month:

- docente secondaria, 1866.79: 18.6679 -> 18.67 each, solidarity 1.867
  -> 1.87;
- sanita, professionisti, 2076.58: 20.7658 -> 20.77 each, solidarity
  2.0766 -> 2.08.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import PensionFundEnrolment, Permanent, PublicEndOfService
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _january(slug: str, level: str, fund: str) -> PeriodResult:
    employment = Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment(fund, Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
        public_end_of_service=PublicEndOfService.TFR_INPS,
    )
    return regular_period(employment=employment, current_year=employment_only())


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("slug", "level", "fund", "each", "solidarity"),
    [
        (
            "istruzione-ricerca-aran.json",
            "DOCENTE_SECONDARIA",
            "ESPERO",
            "18.67",
            "1.87",
        ),
        ("sanita-aran.json", "PROFESSIONISTI", "PERSEO_SIRIO", "20.77", "2.08"),
    ],
    ids=["espero", "perseo_sirio"],
)
def test_one_percent_each_with_the_tfr_notional(
    slug: str, level: str, fund: str, each: str, solidarity: str
) -> None:
    """1% + 1% of the TFR base, no TFR paid to the fund."""
    result = _january(slug, level, fund)
    assert _entry(result, "pension_fund_employer") == Decimal(each)
    assert _entry(result, "pension_fund_employee") == Decimal(each)
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["solidarity"] == Decimal(solidarity)
    assert decision.inputs["tfr_to_fund"] == "notional"
    assert _entry(result, "pension_fund_tfr") == 0


@pytest.mark.parametrize("fund", ["ESPERO", "PERSEO_SIRIO"])
def test_school_and_research_executives_name_their_fund(fund: str) -> None:
    """The dirigenza Istruzione e Ricerca holds both funds."""
    result = _january("dirigenza-istruzione-ricerca-aran.json", "SECONDA_FASCIA", fund)
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["fund_code"] == fund
