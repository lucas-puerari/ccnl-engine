"""INPS rates of the funds of the Gestione Dipendenti Pubblici.

INPS, scheda 'I contributi dei dipendenti pubblici': "CTPS 33 24,2 8,8
CPDEL 32,65 23,8 8,85 [...] CPS 32,65 23,8 8,85".

January 2026, hired that month, the end-of-service regime not stated (no
contribution to the end-of-service fund), with the credit contribution of
0.35% (L. 662/1996 art. 1 c. 242):

- Funzioni Centrali (CTPS), Funzionari, 2227.99: employee 8.80% =
  196.06312 -> 196.06 + credit 7.797965 -> 7.80 = 203.86, employer 24.20%
  = 539.17358 -> 539.17;
- Funzioni Locali (CPDEL), Istruttori, 1928.23 + indennità di comparto
  32.06 (Tabella C, column 4) = 1960.29: employee 8.85% = 173.485665 ->
  173.49 + credit 6.861015 -> 6.86 = 180.35, employer 23.80% = 466.54902
  -> 466.55.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import NoPensionFund, Permanent
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

pytestmark = pytest.mark.legal_scenario


@pytest.mark.parametrize(
    ("slug", "level", "employee", "employer"),
    [
        ("funzioni-centrali-aran.json", "FUNZIONARI", "203.86", "539.17"),
        ("funzioni-locali-aran.json", "ISTRUTTORI", "180.35", "466.55"),
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
