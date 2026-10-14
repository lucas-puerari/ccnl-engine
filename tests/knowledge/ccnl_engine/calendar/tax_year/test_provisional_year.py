"""A provisional tax year is computed but never payable.

The 2027 sector, INPS, family, somma esente, surtax and variable pay files
carry the 2026 values until the sources of 2027 are published.  The engine
blocks a run on them through two limitations only, one for the tax ruleset
and one for the INPS ruleset of the run
(:func:`~ccnl_engine.assurance.ruleset.services.provisional_paths`): the
other rulesets of a year are assumed provisional together with its tax
ruleset.  These tests hold the data to that assumption and check that a run
of every tax sector is blocked.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.results import BlockerCode
from scripts.provenance.rules import KNOWLEDGE_DIR
from tests.knowledge.ccnl_engine.support import regular_period

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.legal_scenario

#: Year files that carry a ruleset: every one but the capability registries.
_YEAR_FILES = sorted(
    path
    for path in {
        *KNOWLEDGE_DIR.glob("*/20[0-9][0-9]/*.json"),
        *KNOWLEDGE_DIR.glob("**/20[0-9][0-9].json"),
    }
    if "ruleset" in json.loads(path.read_text(encoding="utf-8"))
)
#: Years whose sources are not published yet.
_PROVISIONAL_YEARS = {"2027"}
#: One CCNL and level of each tax sector.
_SECTOR_RUNS = (
    ("operai-agricoli-florovivaisti.json", "Area2"),
    ("metalmeccanico-artigianato.json", "2bis"),
    ("bancari-abi.json", "3A4"),
    ("edilizia-ance-impiegati.json", "4"),
    ("metalmeccanico-federmeccanica.json", "C3"),
    ("funzioni-centrali-aran.json", "FUNZIONARI"),
    ("commercio-confcommercio.json", "4"),
)
_TAX = (BlockerCode.OPEN_LIMITATION, "provisional_ruleset")
_INPS = (BlockerCode.OPEN_LIMITATION, "provisional_inps_ruleset")


def _year_of(path: Path) -> str:
    return path.stem if path.stem.isdigit() else path.parent.name


def _ruleset(path: Path) -> dict[str, Any] | None:
    ruleset: dict[str, Any] | None = json.loads(path.read_text(encoding="utf-8")).get(
        "ruleset"
    )
    return ruleset


@pytest.mark.parametrize(
    "path", _YEAR_FILES, ids=lambda p: str(p.relative_to(KNOWLEDGE_DIR))
)
def test_a_year_is_provisional_in_every_file_or_in_none(path: Path) -> None:
    """Every ruleset of a provisional year says so, and no other one does."""
    ruleset = _ruleset(path)
    assert ruleset is not None
    provisional = _year_of(path) in _PROVISIONAL_YEARS

    assert bool(ruleset.get("provisional")) is provisional
    assert (ruleset["source_type"] == "estimated") is provisional


@pytest.mark.parametrize(("ccnl", "level"), _SECTOR_RUNS)
def test_a_run_of_every_sector_on_the_provisional_year_is_blocked(
    ccnl: str, level: str
) -> None:
    """January 2027 reads the provisional tax and INPS rules of its sector."""
    result = regular_period(ccnl_slug=ccnl, level_code=level, year=2027, month=1)
    blockers = {(b.code, b.detail) for b in result.blockers}

    assert {_TAX, _INPS} <= blockers
    assert not result.is_payable


def test_a_run_of_the_published_year_is_not_blocked_as_provisional() -> None:
    """January 2026 reads no provisional ruleset."""
    result = regular_period(year=2026, month=1)
    blockers = {(b.code, b.detail) for b in result.blockers}

    assert not {_TAX, _INPS} & blockers
