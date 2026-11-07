"""The 2026 minimi of the domestic CCNL and their annual update.

Tabella minimi retributivi 2026, "valori decorrenti dal 01/01/2026",
Tabella C, lavoratori non conviventi, valori orari (DOMINA, sha256
bf881702d838dc9c721f07140f17ee6f7cc8b7eb920b4e7647bfa2176ee3d387), read on
14 October 2026: the monthly amount of each level is the hourly minimo
times 40 hours times 52 weeks over 12.  The Commissione nazionale resets the
minimi every 1 January (Art. 38): a 2027 run is blocked until the 2027
table is added.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.limitation.models import LimitationFacts

_CCNL = load_ccnl("lavoro-domestico-non-convivente")
_HOURLY = (
    ("A", "6.51"),
    ("AS", "6.76"),
    ("B", "7.01"),
    ("BS", "7.45"),
    ("C", "7.86"),
    ("CS", "8.30"),
    ("D", "9.57"),
    ("DS", "9.97"),
)


@pytest.mark.parametrize(("level", "hourly"), _HOURLY)
def test_monthly_minimo_is_the_hourly_minimo_of_the_table(
    level: str, hourly: str
) -> None:
    """Hourly minimo x 40 x 52 / 12, to the cent."""
    monthly = (Decimal(hourly) * 40 * 52 / 12).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    assert _CCNL.level_by_code(level).base_salary.value_at(date(2026, 1, 1)) == (
        monthly
    )


@pytest.mark.parametrize(
    "slug",
    [
        "lavoro-domestico-non-convivente",
        "lavoro-domestico-convivente",
        "lavoro-domestico-convivente-orario-ridotto",
    ],
)
def test_the_2026_table_does_not_pass_for_2027(slug: str) -> None:
    """The annual update is an open limitation of every 2027 run."""
    ccnl = load_ccnl(slug)
    (limitation,) = [
        lim for lim in ccnl.limitations if lim.variant == "annual_minimi_not_updated"
    ]

    def facts(day: date) -> LimitationFacts:
        return LimitationFacts(
            ccnl_id=ccnl.meta.ccnl_id,
            as_of=day,
            contract_type="permanent",
            level_code=ccnl.levels[0].code,
            worker_category=None,
            run_kind="regular",
            seniority_months=None,
            applicable=frozenset({"base_salary"}),
        )

    assert limitation.blocks
    assert limitation.applies_to(facts(date(2027, 1, 1)))
    assert not limitation.applies_to(facts(date(2026, 12, 31)))
