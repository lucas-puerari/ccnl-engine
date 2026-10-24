"""The validation matrix: what validates each CCNL, kept in step with the data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from scripts.documentation.validation_matrix.generate import (
    PAGE,
    Row,
    build_page,
    main,
    matrix,
)
from scripts.provenance.reference_case.check import AXES, AXIS_OF
from scripts.provenance.replay.check import credited_records

if TYPE_CHECKING:
    from pathlib import Path


def test_the_page_is_up_to_date() -> None:
    """The committed page is the one the data render."""
    assert main(["--check"]) == 0


def test_every_production_ccnl_is_listed_with_evidence() -> None:
    """A production CCNL always has a reference case, so it has evidence."""
    rows = matrix()
    production = [c for c, r in rows.items() if r.readiness == "production"]

    assert production
    assert all(rows[c].has_evidence for c in production)


def test_the_independence_of_each_kind_of_evidence_is_kept_apart() -> None:
    """Metalmeccanico has all three kinds; a source-linked case is no output."""
    metal = matrix()["metalmeccanico-federmeccanica"]
    autoscuole = matrix()["autoscuole-unasca"]

    assert metal.independence == {"hand oracle", "provider output", "source-linked"}
    assert {"termination", "extra month"} <= metal.cycles
    assert {"tfr", "employer_cost", "net"} <= metal.outputs.keys()
    assert autoscuole.independence == {"source-linked"}


def test_an_output_keeps_the_independence_of_its_own_evidence() -> None:
    """A provider output on the base salary lends nothing to the net.

    Metalmeccanico holds a provider output on the base salary and hand
    oracles on every total: only the base salary is independently covered.
    """
    metal = matrix()["metalmeccanico-federmeccanica"]

    assert metal.covered("base_salary", "provider output")
    assert metal.covered("net", "hand oracle")
    assert not metal.covered("net", "provider output")


def test_the_page_shows_the_strongest_independence_of_each_output() -> None:
    """A row with a provider base salary and a hand-oracle net says so."""
    row = _row()
    row.pin(["base_salary", "net"], "hand oracle")
    row.pin(["base_salary"], "provider output")
    row.sources.add("primary")

    page = build_page({"x": row})

    assert "base_salary (provider output), net (hand oracle)" in page
    assert "net (provider output)" not in page


def _row() -> Row:
    return Row(readiness="production", last_review="—", review_due="—")


def test_fixed_allowances_do_not_cover_the_gross() -> None:
    """The allowances are a component of the gross, listed apart from it."""
    row = _row()
    row.pin(["base_salary", "fixed_allowances"], "provider output")

    assert row.outputs.keys() == {"base_salary"}
    assert row.components.keys() == {"fixed_allowances"}


def test_an_inps_rate_does_not_cover_the_contributions() -> None:
    """A rate fixes how contributions are computed, not their amount."""
    row = _row()
    row.pin(["employee_inps_rate", "employer_inps_rate"], "provider output")

    assert row.outputs == {}
    assert row.rules.keys() == {"employee_inps_rate", "employer_inps_rate"}


@pytest.mark.parametrize("axis", AXES)
def test_each_complete_total_covers_its_output(axis: str) -> None:
    """A compared total lands in the totals, nowhere else."""
    row = _row()
    row.pin([axis], "hand oracle")

    assert row.outputs == {axis: {"hand oracle"}}
    assert row.components == row.rules == {}


def test_an_unknown_label_fails() -> None:
    """A label that is no total, component or rule is a typo, not evidence."""
    with pytest.raises(ValueError, match="'contributions'"):
        _row().pin(["contributions"], "hand oracle")


def test_an_unknown_independence_fails() -> None:
    """Independence is one of the three kinds, never free text."""
    with pytest.raises(ValueError, match="'provider'"):
        _row().pin(["net"], "provider")


def test_the_replayed_components_and_rates_stay_apart_from_the_totals() -> None:
    """The commercio payslips pin a rate, never the contributions it sets.

    The row of commercio also holds the totals of its hand oracles, so the
    replays are pinned on a row of their own.
    """
    row = _row()
    for replay in credited_records(datetime.now(tz=UTC).date()).values():
        if replay["inputs"]["ccnl_id"] == "commercio-confcommercio":
            row.pin((AXIS_OF[key] for key in replay["expected"]), "provider output")

    assert "employee_inps_rate" in row.rules
    assert not row.outputs.keys() & {"employee_contributions", "employer_contributions"}


def test_divergences_show_their_decision() -> None:
    """The logistica blocker and the p25 fix appear as outcomes."""
    rows = matrix()

    assert "blocker" in rows["logistica-trasporto-confetra"].outcomes
    assert {"engine bug fixed", "explained variance"} <= rows[
        "commercio-confcommercio"
    ].outcomes


def test_a_stale_page_fails_the_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--check`` fails on a page that differs, and writing fixes it."""
    page = tmp_path / "validation-matrix.md"
    page.write_text("stale", encoding="utf-8")
    monkeypatch.setattr("scripts.documentation.validation_matrix.generate.PAGE", page)

    assert main(["--check"]) == 1
    assert main([]) == 0
    assert page.read_text(encoding="utf-8") == build_page(matrix())
    assert PAGE.name == page.name
