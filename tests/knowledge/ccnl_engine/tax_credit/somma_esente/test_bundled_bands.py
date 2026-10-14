"""The bundled somma esente against the text of L. 207/2024 art. 1 cc. 4-5.

The unit tests of :func:`~ccnl_engine.tax_credit.rules.somma_esente` run on
a copy of the bands; these run on the files the engine ships, at each limit
of c. 4 and one cent above it, so a typo in the data cannot pass.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.tax_credit.rules import somma_esente
from ccnl_engine.tax_credit.somma_esente.loaders import load_somma_esente_rules

_YEARS = (2026, 2027)

#: Employment income of a full year, the percentage of c. 4 it takes.
_CASES = (
    ("8500.00", "0.071"),
    ("8500.01", "0.053"),
    ("15000.00", "0.053"),
    ("15000.01", "0.048"),
    ("20000.00", "0.048"),
)


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize(("income", "rate"), _CASES)
def test_each_limit_takes_the_percentage_of_the_text(
    year: int, income: str, rate: str
) -> None:
    """Lett. a) up to 8,500, b) up to 15,000, c) above, while R <= 20,000."""
    amount = somma_esente(Decimal(income), load_somma_esente_rules(year))

    assert amount == Decimal(income) * Decimal(rate)


@pytest.mark.parametrize("year", _YEARS)
def test_nothing_is_due_above_20000_of_reddito_complessivo(year: int) -> None:
    """C. 4: only a reddito complessivo not above 20,000 takes the somma."""
    rules = load_somma_esente_rules(year)

    assert somma_esente(Decimal("20000.01"), rules) == 0
    assert somma_esente(Decimal(15000), rules, external_income=Decimal("5000.01")) == 0


@pytest.mark.parametrize("year", _YEARS)
def test_the_percentage_follows_the_annualised_income(year: int) -> None:
    """C. 5: 6,000 earned in half a year is 12,000 a year, so 5.3% of 6,000."""
    rules = load_somma_esente_rules(year)

    amount = somma_esente(Decimal(6000), rules, eligible_work_days=183)

    assert amount == Decimal(6000) * Decimal("0.053")
