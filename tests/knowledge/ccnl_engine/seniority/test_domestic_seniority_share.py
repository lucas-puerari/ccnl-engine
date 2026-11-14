"""Domestic seniority increments stay 4% of the minimum they rest on.

CCNL lavoro domestico of 28 October 2025, Art. 37 c. 1 (Assindatcolf PDF,
sha256 122ca6a72196a835976abac7fb988dc1502973941d52891a546512347fdc9dcf,
p. 44): "per ogni biennio di servizio presso lo stesso datore di lavoro, un
aumento del 4% sulla retribuzione minima contrattuale", which Art. 34 c. 2
a) makes "comprensiva per i livelli D) e D super) di uno specifico elemento
denominato indennità di funzione".  The data stores the amounts; every new
minimum must bring its increments, or this fails.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_SHARE = Decimal("0.04")
_CENT = Decimal("0.01")
_FUNCTION = "INDENNITA_FUNZIONE"


@pytest.mark.parametrize(
    "slug",
    [
        "lavoro-domestico-convivente",
        "lavoro-domestico-convivente-orario-ridotto",
        "lavoro-domestico-non-convivente",
    ],
)
def test_increment_is_four_percent_of_every_minimum(slug: str) -> None:
    """On the first day of each minimum, the increment is 4% of it."""
    ccnl = load_ccnl(slug)
    amounts = ccnl.parameters.seniority_increments.amount_by_level
    checked = 0
    for level in ccnl.levels:
        series = amounts.get(level.code)
        if series is None:
            continue
        for period in level.base_salary.periods:
            if period.value is None:
                continue
            day = period.valid_from
            function = sum(
                (
                    a.monthly.value_at(day)
                    for a in level.fixed_allowances
                    if a.code == _FUNCTION
                ),
                Decimal(0),
            )
            minimum = period.value + function
            expected = (minimum * _SHARE).quantize(_CENT, ROUND_HALF_UP)
            assert series.value_at(day) == expected, level.code
            checked += 1
    assert checked > 0
