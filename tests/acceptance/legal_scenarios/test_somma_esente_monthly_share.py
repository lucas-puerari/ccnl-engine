"""The somma esente of a run is the percentage applied to the income it pays.

AdE circ. 4/E/2025 par. 1.2: the withholding agent "individua la
percentuale [...] tenendo conto del reddito annuale teorico di lavoro
dipendente [...] e riconosce la somma spettante applicando tale percentuale
al reddito effettivamente corrisposto mensilmente"; the conguaglio settles
the year (L. 207/2024 art. 1 c. 7).

Commercio level 4 hired on 1 July 2026 by an employer of 50: 1783.75 a
month, employee IVS 9.19% = 163.93 plus FIS and CIGS 0.57% = 10.17,
taxable 1609.65.  The income of the year, annualised, is above 15,000 EUR:
4.8% (c. 4 lett. c).  July pays 4.8% x 1609.65 = 77.2632 -> 77.26, not the
annual amount divided by the seven payments left.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment, PayrollRun, PeriodFacts, PeriodInput
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE
from tests.fixtures.opening_state import fresh_tax_year
from tests.fixtures.prior_year import RENEWAL_WAIVED
from tests.fixtures.seniority import new_hire
from tests.fixtures.tfr import no_tfr_fund

pytestmark = pytest.mark.legal_scenario

_HIRED = date(2026, 7, 1)


def test_july_pays_the_percentage_of_its_income() -> None:
    """77.26 on the 1609.65 of July."""
    result = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 7),
            payment_date=date(2026, 7, 27),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                employment_period=EmploymentPeriod(started_on=_HIRED),
                seniority=new_hire(2026),
                tfr_fund=no_tfr_fund(2026),
                tfr_treasury_fund=False,
                contract_type=Permanent(),
                pension_fund=NoPensionFund(),
            ),
            employer=EMPLOYER,
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="F205",
                family_composition=FamilyComposition(),
            ),
            opening_state=fresh_tax_year(2026),
            prior_year=RENEWAL_WAIVED,
            current_year=CurrentYearTaxFacts.employment_only(2026, _HIRED),
        )
    )
    assert result.contribution_breakdown.employee == Decimal("174.10")
    assert result.closing_state.cash.somma_esente.recognized == Decimal("77.26")
