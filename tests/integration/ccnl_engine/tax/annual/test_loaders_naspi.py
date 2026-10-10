"""The NASpI surcharge of each bundled 2026 sector (L. 92/2012 art. 2).

C. 28: 1.4% and 0.5 points per renewal, no renewal increase for domestic
work; c. 3: none for the operai agricoli; c. 29 lett. d: none for the
public administrations.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.tax.annual.loaders import load_year_rules

_YEAR = 2026
_PRIVATE = [
    s
    for s in TaxSector
    if s not in {TaxSector.PUBBLICA_AMMINISTRAZIONE, TaxSector.LAVORO_DOMESTICO}
]


@pytest.mark.parametrize("sector", _PRIVATE)
def test_private_sectors_charge_the_statutory_surcharge(sector: TaxSector) -> None:
    """1.4% plus 0.5 points per renewal."""
    rules = load_year_rules(_YEAR, sector, 50)

    assert rules.fixed_term_additional_rate == Decimal("0.014")
    assert rules.fixed_term_renewal_increment == Decimal("0.005")


def test_only_agriculture_exempts_its_operai() -> None:
    """C. 3 names the operai agricoli, not the impiegati."""
    exempt = {
        s: load_year_rules(_YEAR, s, 50).fixed_term_exempt_categories for s in TaxSector
    }

    assert exempt.pop(TaxSector.AGRICOLTURA) == frozenset({WorkerCategory.OPERAIO})
    assert set(exempt.values()) == {frozenset()}


@pytest.mark.parametrize(
    ("sector", "rate"),
    [
        (TaxSector.PUBBLICA_AMMINISTRAZIONE, Decimal(0)),
        (TaxSector.LAVORO_DOMESTICO, Decimal("0.014")),
    ],
)
def test_no_renewal_increase_outside_private_employers(
    sector: TaxSector, rate: Decimal
) -> None:
    """Public administrations pay nothing; domestic work pays no increase."""
    rules = load_year_rules(_YEAR, sector, 50)

    assert rules.fixed_term_additional_rate == rate
    assert rules.fixed_term_renewal_increment == Decimal(0)
