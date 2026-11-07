"""The sub-sector tables of the two tessile CCNL, with their own levels.

Tessile PMI art. 46 (renewal 2024-2027, p. 22, and the verbale of 21
February 2025, pp. 24-25): "SETTORE GIOCATTOLI [...] 4s [...] 2.042,84",
"SETTORE OCCHIALI [...] 4s [...] 2.066,31", "PELLI E CUOIO [...] 6 [...]
2.394,19" from 1/01/2026.  Tessile-moda artigianato, verbale integrativo
of 22 July 2024, pp. 5-6, from 1 October 2025: chimica "5s [...]
1.934,62", "4 [...] 1.747,55"; ceramica "A [...] 1.953,67", "G [...]
1.426,29".
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import EmployerProfile, Headcount, InvalidInputError
from tests.knowledge.ccnl_engine.support import regular_period

_PMI = "tessile-pmi-uniontessile"
_ART = "tessile-moda-artigianato-confartigianato"


def _base(ccnl_id: str, level_code: str, subsector: str | None) -> Decimal:
    result = regular_period(
        ccnl_id=ccnl_id,
        level_code=level_code,
        month=6,
        employer=EmployerProfile(headcount=Headcount(8), subsector=subsector),
    )
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


@pytest.mark.parametrize(
    ("ccnl_id", "level_code", "subsector", "base"),
    [
        (_PMI, "4s", "giocattoli", "2042.84"),
        (_PMI, "4s", "occhiali", "2066.31"),
        (_PMI, "4s", "pelli_cuoio", "2031.96"),
        (_PMI, "6", "pelli_cuoio", "2394.19"),
        (_PMI, "7", "giocattoli", "2460.07"),
        (_PMI, "6", None, "2212.66"),
        (_ART, "5s", "chimica", "1934.62"),
        (_ART, "7", "chimica", "2192.96"),
        (_ART, "4", "chimica", "1747.55"),
        (_ART, "4", None, "1617.92"),
        (_ART, "A", "ceramica", "1953.67"),
        (_ART, "G", "ceramica", "1426.29"),
    ],
)
def test_the_table_of_the_subsector(
    ccnl_id: str, level_code: str, subsector: str | None, base: str
) -> None:
    """June 2026: the minimo of the level in the table of the sub-sector."""
    assert _base(ccnl_id, level_code, subsector) == Decimal(base)


@pytest.mark.parametrize(
    ("ccnl_id", "level_code", "subsector", "field"),
    [
        (_PMI, "4s", None, "EmployerProfile.subsector"),
        (_PMI, "4s", "calzature", "Employment.level_code"),
        (_ART, "5s", "ceramica", "Employment.level_code"),
        (_ART, "B", None, "EmployerProfile.subsector"),
    ],
)
def test_a_subsector_level_needs_its_subsector(
    ccnl_id: str, level_code: str, subsector: str | None, field: str
) -> None:
    """A level of other sub-sectors, or with none stated, is refused."""
    with pytest.raises(InvalidInputError) as exc:
        _base(ccnl_id, level_code, subsector)
    assert exc.value.field == field
