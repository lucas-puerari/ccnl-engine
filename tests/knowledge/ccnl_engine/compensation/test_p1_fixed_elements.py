"""Scatti and fixed elements of the first-round CCNLs read from their texts.

- Metalmeccanico artigianato: from 1 January 2025 apprentices accrue scatti
  of 10 euro (Art. 27 as renewed on 19 November 2024, signed scan p. 6,
  sha256 6f8424cb05c74d81e1a9e58f2b6c972f6f3d61a9639ded36b4c316e13a4e00e1).
- Logistica: the EDR of 18 May 2021 (p. 82) and of Art. 60 c. 8 (p. 85) of
  the testo unico (sha256
  99d743d0924958c9cea8e80ec97377763090ad2b3b84d1a4bb8aa5900f0d6e24).
- Edilizia ANCE: the ex contingenza and EDR of the ANCE table of 1 February
  2025 (sha256
  b681a3f867cd31d4cef09e5234d85a2b6f183a72c66054ed6ff8bd326d88f715), whose
  hourly row is the monthly amount over the divisor 173.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_DAY = date(2026, 6, 1)


def _allowance(slug: str, level: str, code: str) -> Decimal:
    level_rules = load_ccnl(slug).level_by_code(level)
    (element,) = [f for f in level_rules.fixed_allowances if f.code == code]
    value: Decimal = element.monthly.value_at(_DAY)
    return value


def test_artisan_apprentices_accrue_ten_euro_from_2025() -> None:
    """No apprentice scatto before 2025, 10 euro from 1 January 2025."""
    seniority = load_ccnl("metalmeccanico-artigianato").parameters
    amount = seniority.seniority_increments.apprentice_amount

    assert amount is not None
    assert amount.value_at(date(2024, 12, 31)) == Decimal("0.00")
    assert amount.value_at(date(2025, 1, 1)) == Decimal("10.00")


@pytest.mark.parametrize(
    ("level", "edr_2021", "edr_2011"),
    [("Q", "12.80", "12.89"), ("3S", "10.00", "10.00"), ("6", "8.26", "8.26")],
)
def test_logistica_edr_tables(level: str, edr_2021: str, edr_2011: str) -> None:
    """Both EDR tables of the testo unico, personale non viaggiante."""
    slug = "logistica-trasporto-confetra"

    assert _allowance(slug, level, "EDR_2021") == Decimal(edr_2021)
    assert _allowance(slug, level, "EDR_2011") == Decimal(edr_2011)


@pytest.mark.parametrize(
    ("level", "monthly", "hourly"),
    [
        ("1", "512.87", "2.96"),
        ("2", "516.43", "2.99"),
        ("3", "519.16", "3.00"),
        ("4", "521.25", "3.01"),
    ],
)
def test_edilizia_contingenza_matches_the_hourly_row(
    level: str, monthly: str, hourly: str
) -> None:
    """The monthly ex contingenza over 173 gives the printed hourly amount."""
    value = _allowance("edilizia-ance", level, "CONTINGENZA")

    assert value == Decimal(monthly)
    assert (value / 173).quantize(Decimal("0.01"), ROUND_HALF_UP) == Decimal(hourly)
