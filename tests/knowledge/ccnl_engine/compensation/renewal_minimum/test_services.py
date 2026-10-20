"""Renewal increments paid inside the CCNL minimo (L. 199/2025 art. 1 c. 7).

Source: L. 199/2025 art. 1 c. 7 (Gazzetta Ufficiale, serie generale, 21
January 2026): increments paid in 2026 under renewals signed from 1 January
2024 to 31 December 2026 are taxed at 5%, for private-sector employees with
2025 employment income not above 33,000 EUR, unless waived in writing.

Scenario: Metalmeccanico C3, private sector, resident in Alghero, June 2026.
The C3 minimo rises from 2,158.26 to 2,211.43 on 1 June 2026 with the first
tranche of the renewal signed on 22 November 2025; its tables of 1 June 2024
and 2025 are IPCA adjustments of the earlier CCNL, not renewals.  Agenzia
delle Entrate circ. 2/E of 24 February 2026 (par. 1) measures the increment
on the table before the renewal: 2,211.43 - 2,158.26 = 53.17 EUR, taxed at
5% = 2.66 EUR for a worker who meets the requirements.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import EmployerProfile, Employment, Headcount
from ccnl_engine.inputs import (
    EmploymentSector,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
)
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.integration.ccnl_engine.surtax.residence.builders import (
    COMUNE_BELFIORE,
    REGIONE,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import (
    history,
    regular_period,
    substitute_tax,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_RENEWAL = "rinnovo_substitute_tax"
_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_id="metalmeccanico-federmeccanica",
    level_code="C3",
    seniority=new_hire(),
    sector=EmploymentSector.PRIVATE,
    tfr_treasury_fund=False,
    pension_fund=NoPensionFund(),
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _june(income: Decimal | None) -> PeriodResult:
    prior_year = PriorYearTaxFacts(employment_income=income)
    return regular_period(
        month=6,
        employment=_EMPLOYMENT,
        employer=_EMPLOYER,
        opening_state=history(_EMPLOYMENT, 6, prior_year=prior_year),
        prior_year=prior_year,
        regione=REGIONE,
        comune_belfiore=COMUNE_BELFIORE,
    )


def _minimum_decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == _RENEWAL and d.inputs.get("paid_in") == "minimum"
    )
    return decision


def test_eligible_worker_pays_5_percent_on_the_increment() -> None:
    """2025 income 20,000, private: 53.17 EUR taxed at 5% = 2.66 EUR."""
    result = _june(Decimal(20_000))

    assert substitute_tax(result) == Decimal("2.66")
    decision = _minimum_decision(result)
    assert decision.reason_code == "renewal_increment_in_minimum_taxed"
    assert decision.status is CalculationStatus.FINAL
    assert decision.inputs["increment"] == Decimal("53.17")
    assert decision.inputs["pre_renewal_minimum"] == Decimal("2158.26")
    assert "rinnovo_minimum_increment_unquantified" not in {
        b.detail for b in result.blockers
    }


def test_unknown_prior_income_names_the_income() -> None:
    """Without the 2025 income the blocker is that fact, not a generic one."""
    result = _june(None)

    assert _minimum_decision(result).reason_code == "prior_income_unknown"
    assert (BlockerCode.MISSING_FACT, "employment_income") in {
        (b.code, b.detail) for b in result.blockers
    }


def test_income_above_the_ceiling_is_final() -> None:
    """2025 income 40,000 > 33,000: the minimo is ordinary income, final."""
    result = _june(Decimal(40_000))

    decision = _minimum_decision(result)
    assert decision.reason_code == "prior_income_above_ceiling"
    assert decision.status is CalculationStatus.FINAL
    assert _RENEWAL not in {b.feature for b in result.blockers}
