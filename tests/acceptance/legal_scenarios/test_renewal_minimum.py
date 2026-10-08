"""Renewal increments paid inside the CCNL minimo (L. 199/2025 art. 1 c. 7).

Source: L. 199/2025 art. 1 c. 7 (Gazzetta Ufficiale, serie generale, 21
January 2026): increments paid in 2026 under renewals signed from 1 January
2024 to 31 December 2026 are taxed at 5%, for private-sector employees with
2025 employment income not above 33,000 EUR, unless waived in writing.

Scenario: Metalmeccanico C3, private sector, resident in Alghero, June 2026.
The C3 minimo rises from 2,158.26 to 2,211.43 on 1 June 2026, and its
tables of 1 June 2024 and 2025 also fall within the signing window (the
bundle cites the tables of the renewal of 22 November 2025).  How much of
the minimo counts as a renewal increment is not settled by the engine: it
never posts the 5% on the minimo, and a worker who meets the requirements
is blocked instead of being paid at ordinary rates in silence.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import EmployerProfile, Employment, Headcount
from ccnl_engine.inputs import EmploymentSector, Permanent, PriorYearTaxFacts
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.acceptance.legal_scenarios._support import (
    history,
    regular_period,
    substitute_tax,
)
from tests.fixtures.residence import COMUNE_BELFIORE, REGIONE
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_RENEWAL = "rinnovo_substitute_tax"
_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=new_hire(),
    sector=EmploymentSector.PRIVATE,
    tfr_treasury_fund=False,
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


def test_eligible_worker_is_blocked_not_taxed_in_silence() -> None:
    """2025 income 20,000, private: the increment is not quantified."""
    result = _june(Decimal(20_000))

    assert substitute_tax(result) == Decimal(0)
    decision = _minimum_decision(result)
    assert decision.reason_code == "renewal_increment_in_minimum_unquantified"
    assert decision.status is CalculationStatus.PROVISIONAL
    assert (
        BlockerCode.CALCULATION_ISSUE,
        "rinnovo_minimum_increment_unquantified",
    ) in {(b.code, b.detail) for b in result.blockers}
    assert not result.is_payable


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
