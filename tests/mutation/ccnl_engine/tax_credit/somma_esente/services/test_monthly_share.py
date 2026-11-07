"""The somma esente of a run is the percentage applied to the income it pays.

AdE circ. 4/E/2025 par. 1.2: the withholding agent "individua la
percentuale [...] tenendo conto del reddito annuale teorico di lavoro
dipendente [...] e riconosce la somma spettante applicando tale percentuale
al reddito effettivamente corrisposto mensilmente"; the conguaglio settles
the year (L. 207/2024 art. 1 c. 7).

Commercio level 4 hired on 1 July 2026 by an employer of 50: 1783.75 a
month, contributed on 1784 (whole euro, INPS circ. 208/2001), employee IVS
9.19% = 163.95 plus FIS and CIGS 0.56667% = 10.11, taxable 1609.69.  The
income of the year, annualised, is above 15,000 EUR: 4.8% (c. 4 lett. c).
July pays 4.8% x 1609.69 = 77.2651 -> 77.27, not the annual amount divided
by the seven payments left.
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
from tests.integration.ccnl_engine.irpef.declaration.builders import (
    RENEWAL_WAIVED,
)
from tests.knowledge.ccnl_engine.balance.builders import (
    fresh_tax_year,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.severance.builders import no_tfr_fund
from tests.knowledge.ccnl_engine.support import EMPLOYER, ENGINE

pytestmark = pytest.mark.legal_scenario

_HIRED = date(2026, 7, 1)


def test_july_pays_the_percentage_of_its_income() -> None:
    """77.27 on the 1609.69 of July."""
    result = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 7),
            payment_date=date(2026, 7, 27),
            employment=Employment(
                ccnl_id="commercio-confcommercio",
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
    assert result.contribution_breakdown.employee == Decimal("174.06")
    assert result.closing_state.cash.somma_esente.recognized == Decimal("77.27")
