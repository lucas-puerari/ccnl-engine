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


def _provisional(path: Path) -> bool:
    ruleset = _ruleset(path)
    assert ruleset is not None
    provisional: bool = bool(ruleset.get("provisional"))
    estimated: bool = ruleset["source_type"] == "estimated"
    assert estimated == provisional, path.name
    return provisional


def _dataset(path: Path) -> str:
    return path.relative_to(KNOWLEDGE_DIR).parts[0]


#: Datasets whose provisional state the tax ruleset of the year stands for.
_TAX_COMPANIONS = {"family", "surtax", "tax_credit", "variable_pay"}


@pytest.mark.parametrize("year", sorted({_year_of(p) for p in _YEAR_FILES}))
def test_the_tax_ruleset_stands_for_its_companions(year: str) -> None:
    """A provisional companion file is never left without its tax ruleset.

    A family, surtax, somma esente or variable pay file blocks no run by
    itself: the provisional tax ruleset of the year does.  The sector files
    of a year are provisional together, and so are its INPS files; the INPS
    circulars come out weeks after the budget law, so the INPS files may
    stay provisional once the sector files are not.
    """
    files = [p for p in _YEAR_FILES if _year_of(p) == year]
    sector = {_provisional(p) for p in files if _dataset(p) == "sector"}
    inps = {_provisional(p) for p in files if _dataset(p) == "contribution"}
    companions = [p for p in files if _dataset(p) in _TAX_COMPANIONS]

    assert len(sector) == 1
    assert len(inps) == 1
    if any(_provisional(p) for p in companions):
        assert sector == {True}


def test_the_published_year_is_not_provisional() -> None:
    """No file of a year whose sources are published is provisional."""
    for path in _YEAR_FILES:
        if _year_of(path) not in _PROVISIONAL_YEARS:
            assert not _provisional(path), path.name


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


def _assumed_tranches() -> list[tuple[str, str, int, int]]:
    """Return the first assumed tranche of a provisional year of each CCNL.

    Returns:
        ``(slug, level, year, month)`` of the first level whose base salary
        takes an ``assumed`` value in a provisional year.
    """
    found: dict[str, tuple[str, str, int, int]] = {}
    for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json")):
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        for level in data.get("levels", []):
            for period in level.get("base_salary", {}).get("periods", []):
                start = str(period.get("valid_from", ""))
                status = period.get("provenance", {}).get("status")
                if start[:4] in _PROVISIONAL_YEARS and status == "assumed":
                    found.setdefault(
                        path.name,
                        (path.name, level["code"], int(start[:4]), int(start[5:7])),
                    )
    return sorted(found.values())


@pytest.mark.parametrize(("slug", "level", "year", "month"), _assumed_tranches())
def test_an_assumed_tranche_of_the_provisional_year_is_a_visible_blocker(
    slug: str, level: str, year: int, month: int
) -> None:
    """A pay tranche no signed text backs yet blocks the run that pays it."""
    result = regular_period(ccnl_slug=slug, level_code=level, year=year, month=month)
    weak = {
        (b.feature, b.detail)
        for b in result.blockers
        if b.code is BlockerCode.RULE_SOURCE_WEAK
    }

    assert ("base_salary", "assumed") in weak
    assert not result.is_payable


def test_the_provisional_year_has_assumed_tranches_to_check() -> None:
    """The scan above is not vacuous: some CCNLs still assume a 2027 tranche."""
    assert _assumed_tranches()
