"""Written deferral of the year-end shortfall and foreign tax credit.

Art. 23 c. 3 DPR 600/1973 (in force for 2026):

- on the worker's written request the IRPEF the conguaglio cannot withhold
  is withheld "sulle retribuzioni dei periodi di paga successivi al secondo
  dello stesso periodo di imposta", with interest "in ragione dello 0,50
  per cento mensile", remitted as the tax (code 1066, ris. AdE 6/E/2021);
- the foreign taxes paid on employment income produced abroad "sono
  ammesse in detrazione fino a concorrenza dell'imposta relativa ai predetti
  redditi prodotti all'estero" (art. 165 TUIR).

Scenario: Metalmeccanico C3, 2026.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    Employment,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.events import FringeEvent
from ccnl_engine.inputs import (
    DeferredShortfall,
    ForeignTaxPaid,
    OpeningBalances,
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE

pytestmark = pytest.mark.legal_scenario

_EMPLOYMENT = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
)


def _year(
    prior_year: PriorYearTaxFacts,
    periods: dict[int, PeriodFacts] | None = None,
    opening: OpeningBalances | None = None,
) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=EMPLOYER,
            prior_year=prior_year,
            periods=periods or {},
            opening_state=None
            if opening is None
            else PayrollEngine.import_opening_balances(opening),
        )
    )


def test_request_defers_the_shortfall_to_the_next_year() -> None:
    """A 20,000 EUR December fringe benefit leaves IRPEF the pay cannot cover.

    With the written request it is carried into 2027 instead of being
    communicated to the worker.
    """
    fringe = PeriodFacts(events=(FringeEvent(date(2026, 12, 5), Decimal(20000)),))
    request = ShortfallDeferralRequest(signed_on=date(2026, 12, 10))
    year = _year(PriorYearTaxFacts(shortfall_deferral=request), {12: fringe})
    opening_2027 = ENGINE.close_tax_year(year.period_results[-1].closing_state)
    (deferred,) = opening_2027.cash.obligations.deferred_shortfall
    assert deferred.tax_year == 2026
    assert deferred.irpef > Decimal(0)
    assert not [i for i in year.issues if i.code.endswith("shortfall_unrecovered")]


def test_march_withholds_a_deferral_with_interest_under_1066() -> None:
    """300.00 EUR deferred by the December 2025 conguaglio.

    March 2026 is the first pay period after the second: 3 months of
    interest at 0.50 per cent, 300.00 x 0.015 = 4.50 EUR.
    """
    deferred = DeferredShortfall(
        tax_year=2025,
        signed_on=date(2025, 12, 10),
        deferred_from=date(2025, 12, 1),
        irpef=Decimal("300.00"),
    )
    year = _year(
        PriorYearTaxFacts(),
        opening=OpeningBalances(
            tax_year=2026,
            deferred_shortfall=deferred,
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        ),
    )
    runs = year.period_results
    codes = [
        {ln.remittance_code: ln.amount for ln in r.remittance_summary()}
        for r in runs[:3]
    ]
    assert "1066" not in codes[0]
    assert "1066" not in codes[1]
    assert codes[2]["1066"] == Decimal("304.50")


def test_foreign_tax_lowers_the_irpef_of_the_year() -> None:
    """500 EUR paid in France on 10,000 EUR earned there is credited in full.

    The Italian tax on that income is about 23 per cent of it, well above
    500 EUR, so the whole foreign tax is deducted at the conguaglio.
    """
    plain = _year(PriorYearTaxFacts())
    abroad = _year(
        PriorYearTaxFacts(
            foreign_taxes=(ForeignTaxPaid("FR", Decimal(10000), Decimal(500)),)
        )
    )
    withheld = plain.period_results[-1].closing_state.cash.tax.irpef
    credited = abroad.period_results[-1].closing_state.cash.tax.irpef
    assert withheld - credited == Decimal(500)
