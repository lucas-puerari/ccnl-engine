"""The tabellare of CCNL Funzioni Centrali 2025-2027 from the ARAN text.

CCNL of 6 August 2026, Tabella 3 "Nuova retribuzione tabellare annua",
"Valori in Euro per 12 mensilità a cui aggiungere la 13^ mensilità" (ARAN,
sha256 1a8142a37a08f1ed6558b4cd0b05f35fb9638ac14ef2a8ccc98c3b494824033e),
read again on 14 October 2026: the monthly tabellare of each area is the
annual amount over 12, from 1 January 2025, 2026 and 2027.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("funzioni-centrali-aran.json")
_YEARS = (2025, 2026, 2027)
#: Area, annual tabellare from 1 January 2025, 2026 and 2027, as printed.
_TABLE = (
    ("ELEVATE_PROFESSIONALITA", ("35571.69", "36508.89", "37286.49")),
    ("FUNZIONARI", ("26049.53", "26735.93", "27304.73")),
    ("ASSISTENTI", ("21449.57", "22014.77", "22482.77")),
    ("OPERATORI", ("20384.04", "20921.64", "21366.84")),
)


@pytest.mark.parametrize(("area", "annual"), _TABLE)
def test_monthly_tabellare_is_the_annual_over_twelve(
    area: str, annual: tuple[str, ...]
) -> None:
    """From 1 January of each year, and the year before on 31 December."""
    salary = _CCNL.level_by_code(area).base_salary
    monthly = [
        (Decimal(a) / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        for a in annual
    ]

    for year, amount in zip(_YEARS, monthly, strict=True):
        assert salary.value_at(date(year, 1, 1)) == amount
    for year, previous in zip(_YEARS[1:], monthly, strict=False):
        assert salary.value_at(date(year - 1, 12, 31)) == previous
