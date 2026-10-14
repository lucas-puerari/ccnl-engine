"""INPS sickness cover of the bundled rates by CCNL, sector and category.

INPS, Indennità di malattia per lavoratori dipendenti (updated 21.9.2026,
re-read on 14.10.2026): the indemnity "spetta [...] a: operai del settore
industria; operai e impiegati del settore terziario e servizi; lavoratori
dell'agricoltura; apprendisti; [...] lavoratori dello spettacolo" and "Non
spetta a (elenco non esaustivo): collaboratori familiari (colf e badanti);
impiegati dell'industria; quadri (industria e artigianato); dirigenti;
portieri".  A worker the page does not place is not known to be covered:
the engine pays the day as uncovered with a provisional issue.
"""

from __future__ import annotations

import pytest

from ccnl_engine.sickness.indemnity.loaders import load_sick_pay_rates


@pytest.mark.parametrize(
    ("sector", "category", "ccnl", "covered"),
    [
        ("terziario", "operaio", "portieri-fabbricati-confedilizia", False),
        ("terziario", "operaio", "commercio-confcommercio", True),
        ("agricoltura", "operaio", "operai-agricoli-florovivaisti", True),
        ("edilizia", "operaio", "edilizia-ance", True),
        ("edilizia", "impiegato", "edilizia-ance-impiegati", False),
        ("edilizia", "quadro", "edilizia-ance-impiegati", False),
        ("industria", "operaio", "metalmeccanico-federmeccanica", True),
        ("industria", "impiegato", "metalmeccanico-federmeccanica", False),
        ("industria", "quadro", "metalmeccanico-federmeccanica", False),
        ("industria", "dirigente", "metalmeccanico-federmeccanica", False),
        ("terziario", "impiegato", "commercio-confcommercio", True),
        ("terziario", "dirigente", "commercio-confcommercio", False),
        ("artigianato", "quadro", "metalmeccanico-artigianato", False),
        ("industria", "impiegato", "cinema-audiovisivi-industria", True),
        ("lavoro-domestico", "operaio", "lavoro-domestico-non-convivente", False),
        ("pubblica-amministrazione", "impiegato", "funzioni-centrali-aran", False),
    ],
)
def test_cover(sector: str, category: str, ccnl: str, covered: bool) -> None:
    """Portieri and building impiegati or quadri are out, operai in."""
    assert load_sick_pay_rates().covers(sector, category, "permanent", ccnl) is covered


@pytest.mark.parametrize("contract_type", ["permanent", "apprentice"])
def test_apprentices_follow_the_rule_of_their_sector(contract_type: str) -> None:
    """An apprentice operaio of industry is covered like the operai."""
    rates = load_sick_pay_rates()

    assert rates.covers("industria", "operaio", contract_type, "concia-unic") is True


@pytest.mark.parametrize(
    ("sector", "category"),
    [("credito", "impiegato"), ("agricoltura", "impiegato")],
)
def test_a_worker_the_page_does_not_place_is_unknown(
    sector: str, category: str
) -> None:
    """No rule matches: the cover is not known, not assumed either way."""
    rates = load_sick_pay_rates()

    assert rates.covers(sector, category, "permanent", "x") is None
