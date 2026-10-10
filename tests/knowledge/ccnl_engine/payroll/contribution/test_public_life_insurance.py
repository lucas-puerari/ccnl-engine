"""Assicurazione Sociale Vita (ex ENPDEP) of a public employee.

INPS circ. 104/2014: "Sono [...] iscritti all'assicurazione tutti i
dipendenti da enti dotati di personalità giuridica di diritto pubblico, ad
eccezione delle Amministrazioni dello Stato, delle Province, dei Comuni";
"Il contributo è pari allo 0,12% della base imponibile e grava in misura
pari allo 0,027% sul lavoratore ed allo 0,093% sul datore di lavoro", on
the pension base.

Funzioni Centrali (an ente pubblico non economico or a ministry),
Funzionari, January 2026, 2227.99: worker 0.027% = 0.60155 -> 0.60,
employer 0.093% = 2.07203 -> 2.07.  The school of the State owes none.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import NoPensionFund, Permanent, PublicEndOfService
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import EMPLOYER, regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _january(
    insured: bool | None,
    slug: str = "funzioni-centrali-aran.json",
    level: str = "FUNZIONARI",
) -> PeriodResult:
    employment = Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        public_end_of_service=PublicEndOfService.TFR_EMPLOYER,
    )
    return regular_period(
        employment=employment,
        employer=replace(EMPLOYER, public_life_insurance=insured),
        current_year=employment_only(),
    )


def _components(result: PeriodResult) -> dict[str, Decimal]:
    return {c.name: c.amount for c in result.contribution_breakdown.components}


def test_ente_pubblico_owes_it() -> None:
    """0.60 of the worker and 2.07 of the employer."""
    components = _components(_january(insured=True))
    assert components["life_insurance_employee"] == Decimal("0.60")
    assert components["life_insurance_employer"] == Decimal("2.07")


def test_ministry_owes_none() -> None:
    """The State is left out."""
    result = _january(insured=False)
    assert "life_insurance_employee" not in _components(result)
    assert "public_life_insurance_unknown" not in {i.code for i in result.issues}


def test_unstated_on_a_mixed_ccnl_is_a_missing_fact() -> None:
    """Funzioni Centrali hosts ministries and enti pubblici alike."""
    result = _january(insured=None)
    (issue,) = [i for i in result.issues if i.code == "public_life_insurance_unknown"]
    assert issue.fact == "public_life_insurance"
    assert not result.is_payable


def test_state_school_needs_no_statement() -> None:
    """The CCNL of the State school fixes it: none owed, no issue."""
    result = _january(None, "istruzione-ricerca-aran.json", "DOCENTE_SECONDARIA")
    assert "life_insurance_employee" not in _components(result)
    assert "public_life_insurance_unknown" not in {i.code for i in result.issues}
