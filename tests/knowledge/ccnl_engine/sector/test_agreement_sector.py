"""Check the tax sector each bundled CCNL declares.

The tax sector picks both the sector file and the INPS contribution table
of a run, so every declared sector must load for every bundled year.  An
artisan CCNL takes the artisan table, and a CCNL whose operai owe a CIGO
the tables do not carry (D.Lgs. 148/2015 art. 13 c. 1 lett. c-d) declares
that gap as an open limitation instead of passing for payable.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.sector.loaders import load_year_rules
from scripts.provenance.rules import KNOWLEDGE_DIR

_AGREEMENTS = sorted((KNOWLEDGE_DIR / "agreement").glob("*.json"))
_YEARS = (2026, 2027)
#: CCNLs of the building and stone-working firms whose CIGO no table holds.
_CIGO_BY_ACTIVITY = {
    "edilizia-artigianato-cna",
    "lapidei-industria",
    "legno-lapidei-artigianato-confartigianato",
    "materiali-costruzione-lapidei-confapi",
}


def _meta(slug: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (KNOWLEDGE_DIR / "agreement" / f"{slug}.json").read_text(encoding="utf-8")
    )
    return data


def _sectors() -> dict[str, str]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))["meta"]["tax_sector"]
        for path in _AGREEMENTS
    }


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("sector", sorted(set(_sectors().values())))
def test_every_declared_sector_loads(year: int, sector: str) -> None:
    """The sector and INPS files of each declared sector load for each year."""
    rules = load_year_rules(year, TaxSector(sector), 10)

    assert rules.ruleset is not None
    assert rules.inps_ruleset is not None


def test_artisan_agreements_take_the_artisan_table() -> None:
    """A CCNL of artisan firms reads contribution/<year>/artigianato.json."""
    wrong = {
        slug: sector
        for slug, sector in _sectors().items()
        if "artigianato" in slug and sector != "artigianato"
    }

    assert wrong == {}


def test_cigo_by_activity_is_a_declared_limitation() -> None:
    """The edile and lapidei CIGO gap blocks the runs it concerns."""
    declared = {
        path.stem
        for path in _AGREEMENTS
        for note in _meta(path.stem)["coverage"]["notes"]
        if (note.get("limitation") or {}).get("variant") == "cigo_rate_by_activity"
    }

    assert declared == _CIGO_BY_ACTIVITY
