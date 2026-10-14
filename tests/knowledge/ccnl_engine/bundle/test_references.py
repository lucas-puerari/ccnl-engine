"""Every reference between bundled resources points to something that exists.

Overlapping, uncovered and duplicate periods of a series are rejected when a
series loads (``ccnl_engine.types``, an ordered and contiguous sequence), so
:mod:`test_whole_bundle` covers them.  What a single file cannot check is a
name that points into another file or another part of the same file: a
level of an apprenticeship track, a CCNL in the sick-pay cover or in an
engine limitation, a sector or category of the cover.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.employment.category.models import WorkerCategory
from scripts.provenance.rules import KNOWLEDGE_DIR

_AGREEMENTS: dict[str, dict[str, Any]] = {
    path.stem: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json"))
}


def _load(relative: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (KNOWLEDGE_DIR / relative).read_text(encoding="utf-8")
    )
    return data


def test_level_codes_are_unique_in_each_agreement() -> None:
    """No CCNL lists the same level code twice."""
    duplicates = {
        slug: [code for code, n in Counter(codes).items() if n > 1]
        for slug, data in _AGREEMENTS.items()
        if len(codes := [level["code"] for level in data["levels"]]) != len(set(codes))
    }

    assert duplicates == {}


def test_apprenticeship_tracks_name_levels_of_their_agreement() -> None:
    """Destination and reference levels exist in the CCNL of the track."""
    dangling = [
        (slug, code)
        for slug, data in _AGREEMENTS.items()
        for track in data.get("apprenticeship") or []
        for code in [
            *track.get("destination_levels", []),
            *([track["reference_level"]] if track.get("reference_level") else []),
        ]
        if code not in {level["code"] for level in data["levels"]}
    ]

    assert dangling == []


def test_sick_pay_cover_names_known_agreements_sectors_and_categories() -> None:
    """Each rule of the INPS cover matches something the bundle has."""
    sectors = {sector.value for sector in TaxSector}
    categories = {category.value for category in WorkerCategory}
    for rule in _load("sickness/indemnity/rates.json")["coverage"]:
        assert set(rule.get("ccnls", [])) <= set(_AGREEMENTS)
        assert set(rule.get("sectors", [])) <= sectors
        assert set(rule.get("categories", [])) <= categories


def test_engine_limitations_name_bundled_agreements() -> None:
    """The rulesets of an engine limitation are bundled CCNLs."""
    for limitation in _load("limitation/engine.json")["limitations"]:
        assert set(limitation["rulesets"]) <= set(_AGREEMENTS), limitation["id"]


def test_every_agreement_sector_has_its_files() -> None:
    """The tax sector of each CCNL has a sector and an INPS file every year."""
    years = sorted(path.name for path in (KNOWLEDGE_DIR / "sector").iterdir())
    for data in _AGREEMENTS.values():
        sector = data["meta"]["tax_sector"]
        for year in years:
            assert (KNOWLEDGE_DIR / "sector" / year / f"{sector}.json").is_file()
            assert (KNOWLEDGE_DIR / "contribution" / year / f"{sector}.json").is_file()
