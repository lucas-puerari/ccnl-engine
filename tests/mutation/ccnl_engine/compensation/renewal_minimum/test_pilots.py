"""Hand oracle: the renewal increment inside the minimo of six pilot CCNLs.

A full-time permanent worker of the middle level, March 2026, private
sector, 2025 employment income 25,000 EUR.  The increment is the minimo of
March 2026 less the minimo before the first renewal signed from 1 January
2024 (L. 199/2025 art. 1 c. 7; AdE circ. 2/E/2026 par. 1), taxed at 5%:

- chimica D1: 2,360.26 - 2,259.26 (2,239.26 + 20 of the 2022 renewal paid
  with the July 2025 tranche, 2025 text p. 46) = 101.00, tax 5.05;
- FIPE 3: 1,757.14 - 1,659.07 (1,130.81 + 528.26) = 98.07, tax 4.90;
- studi 3S: 1,722.01 - 1,525.23 = 196.78, tax 9.84;
- commercio 4: 1,257.46 - 1,122.46 = 135.00, tax 6.75;
- terziario IV: 1,781.68 - 1,646.68 = 135.00, tax 6.75;
- confapi 5: 2,195.87 - 2,173.76 = 22.11, tax 1.11.

Turismo (year) and Federmeccanica (June) have oracles of their own.
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
from tests.integration.ccnl_engine.surtax.residence.builders import (
    COMUNE_BELFIORE,
    REGIONE,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import history, regular_period

if TYPE_CHECKING:
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_PRIOR = PriorYearTaxFacts(employment_income=Decimal(25_000))


def _decision(ccnl_id: str, level: str) -> CalculationDecision:
    employment = Employment(
        contract_type=Permanent(),
        ccnl_id=ccnl_id,
        level_code=level,
        seniority=new_hire(),
        sector=EmploymentSector.PRIVATE,
        tfr_treasury_fund=False,
        pension_fund=NoPensionFund(),
        roles=frozenset(),
    )
    result = regular_period(
        month=3,
        employment=employment,
        employer=EmployerProfile(headcount=Headcount(50), provincial_pay_element=False),
        opening_state=history(employment, 3, prior_year=_PRIOR),
        prior_year=_PRIOR,
        regione=REGIONE,
        comune_belfiore=COMUNE_BELFIORE,
    )
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "rinnovo_substitute_tax"
        and d.inputs.get("paid_in") == "minimum"
    )
    return decision


@pytest.mark.parametrize(
    ("ccnl_id", "level", "before", "increment", "tax"),
    [
        ("chimica-farmaceutica-federchimica", "D1", "2259.26", "101.00", "5.05"),
        ("pubblici-esercizi-fipe-angem", "3", "1659.07", "98.07", "4.90"),
        ("studi-professionali-confprofessioni", "3S", "1525.23", "196.78", "9.84"),
        ("commercio-confcommercio", "4", "1122.46", "135.00", "6.75"),
        ("terziario-confesercenti", "IV", "1646.68", "135.00", "6.75"),
        ("metalmeccanico-confapi", "5", "2173.76", "22.11", "1.11"),
    ],
)
def test_the_increment_and_its_tax(
    ccnl_id: str, level: str, before: str, increment: str, tax: str
) -> None:
    """Minimo of March 2026 less the minimo before the renewal, at 5%."""
    decision = _decision(ccnl_id, level)

    assert decision.reason_code == "renewal_increment_in_minimum_taxed"
    assert decision.inputs["pre_renewal_minimum"] == Decimal(before)
    assert decision.inputs["increment"] == Decimal(increment)
    assert decision.amount == Decimal(tax)


def test_a_chimica_category_without_its_2022_tranche_is_unmeasured() -> None:
    """The 2025 text gives the 2022 tranche of D1 only: E1 stays unmeasured."""
    decision = _decision("chimica-farmaceutica-federchimica", "E1")

    assert decision.reason_code == "renewal_increment_in_minimum_unquantified"
