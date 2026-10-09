"""INPS rates of the funds of the Gestione Dipendenti Pubblici.

INPS, scheda 'I contributi dei dipendenti pubblici': "CTPS 33 24,2 8,8
CPDEL 32,65 23,8 8,85 [...] CPS 32,65 23,8 8,85".

January 2026, hired that month, no other contribution of the run:

- Funzioni Centrali (CTPS), Funzionari, 2227.99: employee 8.80% =
  196.06312 -> 196.06, employer 24.20% = 539.17358 -> 539.17;
- Funzioni Locali (CPDEL), Istruttori, 1928.23: employee 8.85% =
  170.648355 -> 170.65, employer 23.80% = 458.91874 -> 458.92.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import NoPensionFund, Permanent
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

pytestmark = pytest.mark.legal_scenario


@pytest.mark.parametrize(
    ("slug", "level", "employee", "employer"),
    [
        ("funzioni-centrali-aran.json", "FUNZIONARI", "196.06", "539.17"),
        ("funzioni-locali-aran.json", "ISTRUTTORI", "170.65", "458.92"),
    ],
    ids=["ctps", "cpdel"],
)
def test_rates_of_the_fund_of_the_ccnl(
    slug: str, level: str, employee: str, employer: str
) -> None:
    """CTPS for the State, CPDEL for the enti locali."""
    employment = Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment, current_year=employment_only())
    breakdown = result.contribution_breakdown
    assert breakdown.employee == Decimal(employee)
    assert breakdown.employer == Decimal(employer)
