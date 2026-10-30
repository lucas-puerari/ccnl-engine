"""The rule inventory scans every dataset whose records the engine reads."""

from __future__ import annotations

import json

from scripts.provenance.rules import FISCAL_DATASETS, KNOWLEDGE_DIR, inventory

#: Datasets of the bundle that hold no payable rule: the agreements are
#: scanned apart; the others are indexes, registries and the census.
_NOT_RULES = {"agreement", "capability", "census", "limitation", "pay_item"}


def _has_provenance(data: object) -> bool:
    if isinstance(data, dict):
        return "provenance" in data or any(_has_provenance(v) for v in data.values())
    if isinstance(data, list):
        return any(_has_provenance(v) for v in data)
    return False


def test_every_dataset_with_provenance_is_scanned() -> None:
    """A dataset of sourced records the inventory skips would hide its rules."""
    with_records = {
        path.relative_to(KNOWLEDGE_DIR).parts[0]
        for path in KNOWLEDGE_DIR.rglob("*.json")
        if path.parent != KNOWLEDGE_DIR
        and _has_provenance(json.loads(path.read_text(encoding="utf-8")))
    }

    assert with_records - _NOT_RULES <= set(FISCAL_DATASETS)


def test_the_insured_absences_are_in_the_inventory() -> None:
    """Maternity, paternity, parental leave, permits, extraordinary leave, injury."""
    paths = {
        rule.path for rule in inventory() if rule.file == "absence/insured/rates.json"
    }

    assert paths == {
        "maternity",
        "paternity",
        "parental",
        "disability_permit",
        "extraordinary_leave",
        "injury",
    }
