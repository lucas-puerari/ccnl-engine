"""Seed the census from the open limitations and the weak rules."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.census.models import Census
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.limitation.loaders import load_engine_limitations
from scripts.census import generate
from scripts.provenance.evidence.check import snapshot
from scripts.provenance.rules import PayableRule

if TYPE_CHECKING:
    from pathlib import Path

_SEEDED = {"id": "a", "origin": "seeded", "state": "absent"}
_TEXT = {"id": "b", "origin": "text", "state": "implemented"}


def test_a_limitation_row_links_its_limitation() -> None:
    """The row of a CCNL limitation takes its variant as id and links it."""
    ccnl = load_ccnl("commercio-confcommercio")
    limitation = next(
        lim for lim in ccnl.limitations if lim.variant == "sickness_net_basis"
    )

    row = generate.limitation_row(limitation)

    assert row["id"] == "sickness_net_basis"
    assert row["remediation"] == limitation.remediation
    assert row["links"] == {"limitations": [limitation.id]}
    assert row["origin"] == "seeded"


def test_an_engine_limitation_row_takes_the_engine_id() -> None:
    """An engine limitation is named by its id, not by its variant."""
    engine = {lim.id: lim for lim in load_engine_limitations()}

    row = generate.limitation_row(engine["sickness_inps_daily_base"])

    assert row["id"] == "sickness_inps_daily_base"
    assert row["remediation"] == engine["sickness_inps_daily_base"].remediation


def test_a_weak_rule_row_links_its_rule() -> None:
    """A missing rule is absent, an assumed one unverified."""
    missing = PayableRule(
        "agreement/x.json", "parameters.accrual_rule", ("tfr",), "missing"
    )
    assumed = PayableRule("sector/2027/industria.json", "tfr", ("tfr",), "assumed")

    assert generate.rule_row(missing) | {"links": None} == {
        "id": "rule_parameters_accrual_rule",
        "institute": "tfr",
        "variant": "all",
        "rule": "agreement/x.json#parameters.accrual_rule",
        "calculation": "tfr",
        "state": "absent",
        "remediation": generate.WEAK_REMEDIATION,
        "origin": "seeded",
        "links": None,
    }
    assert generate.rule_row(assumed)["id"] == "rule_sector_2027_industria_tfr"
    assert generate.rule_row(assumed)["state"] == "unverified"


def test_a_long_rule_path_keeps_a_digest() -> None:
    """Ids stay within 64 characters and distinct."""
    long = PayableRule(
        "agreement/x.json", "levels[" + "x" * 80 + "]", ("base_salary",), "assumed"
    )
    other = PayableRule(
        "agreement/x.json", "levels[" + "x" * 81 + "]", ("base_salary",), "assumed"
    )

    assert len(generate.rule_row_id(long)) == 64
    assert generate.rule_row_id(long) != generate.rule_row_id(other)


def test_merge_keeps_text_rows_and_rebuilds_seeded_ones() -> None:
    """A text row replaces a seeded row of the same id; old seeded rows go."""
    existing = {"requirements": [_SEEDED, _TEXT]}
    fresh = [{"id": "b", "origin": "seeded"}, {"id": "c", "origin": "seeded"}]

    merged = generate.merge(existing, "x", fresh)

    assert merged["requirements"] == [_TEXT, {"id": "c", "origin": "seeded"}]


def test_merge_rejects_two_seeded_rows_with_one_id() -> None:
    """Two limitations of one CCNL must not collapse into one row."""
    with pytest.raises(ValueError, match="share an id"):
        generate.merge(None, "x", [{"id": "a"}, {"id": "a"}])


def test_every_weak_rule_and_open_limitation_has_a_row() -> None:
    """The census reconciles all the weak evidence of the bundle."""
    files = generate.build()
    censuses = [Census.model_validate(json.loads(text)) for text in files.values()]
    linked_rules = {
        r for c in censuses for row in c.requirements for r in row.links.rules
    }
    linked = {
        i for c in censuses for row in c.requirements for i in row.links.limitations
    }
    evidence = snapshot()

    assert linked_rules == {
        f"{file}#{path}"
        for file, paths in evidence.weak_rules.items()
        for path in paths
    }
    assert linked == {i for ids in evidence.open_limitations.values() for i in ids}
    assert all(row.remediation for c in censuses for row in c.requirements)


def test_the_bundled_census_is_up_to_date(tmp_path: Path) -> None:
    """``--check`` passes on the bundle and fails on an empty directory."""
    assert generate.main(["--check"]) == 0
    assert generate.main(["--check"], root=tmp_path) == 1
    assert generate.main([], root=tmp_path) == 0
    assert generate.main(["--check"], root=tmp_path) == 0
