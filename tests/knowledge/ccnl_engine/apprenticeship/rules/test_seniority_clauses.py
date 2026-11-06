"""The apprentice seniority clauses read in the CCNL texts.

Portieri artt. 126-128 c. 3 ("L'eventuale periodo di apprendistato non sarà
considerato utile agli effetti degli scatti"), Servizi postali (apprentice
pay of tabellare, contingenza and EDR only) and Lapidei (agreement of 15
March 2006: "esclusi gli scatti di anzianità") pay no increment; Sistemazioni
idraulico-forestali impiegati art. 7 and Cooperative agricole art. 24 give
the apprentice the treatment of the permanent staff, increments included.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_NONE = [
    "portieri-fabbricati-confedilizia",
    "servizi-postali-appalto-fise",
    "lapidei-industria",
]
_LEVEL = ["sistemazioni-idraulico-forestali-impiegati", "cooperative-consorzi-agricoli"]


@pytest.mark.parametrize("slug", _NONE)
def test_the_apprentice_accrues_no_increment(slug: str) -> None:
    """A zero apprentice amount, not the level amounts."""
    increments = load_ccnl(slug).parameters.seniority_increments
    assert increments is not None
    assert increments.apprentice_amount is not None
    assert increments.apprentice_amount.value_at(date(2026, 3, 1)) == 0
    assert not increments.apprentice_level_amount


@pytest.mark.parametrize("slug", _LEVEL)
def test_the_apprentice_accrues_the_level_increments(slug: str) -> None:
    """The amounts of the level the apprentice is classified at."""
    increments = load_ccnl(slug).parameters.seniority_increments
    assert increments is not None
    assert increments.apprentice_level_amount
    assert increments.apprentice_amount is None


@pytest.mark.parametrize("slug", _NONE + _LEVEL)
def test_no_apprentice_seniority_limitation_is_left(slug: str) -> None:
    """The clause is read: the provisional note is gone."""
    notes = load_ccnl(slug).coverage.notes
    assert not [
        n
        for n in notes
        if n.limitation is not None and n.limitation.variant == "apprentice_seniority"
    ]
