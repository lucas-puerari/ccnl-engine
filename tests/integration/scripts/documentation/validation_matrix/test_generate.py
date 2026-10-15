"""The validation matrix: what validates each CCNL, kept in step with the data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.documentation.validation_matrix.generate import (
    PAGE,
    build_page,
    main,
    matrix,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


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
    alimentari = matrix()["alimentari-federalimentare"]

    assert metal.independence == {"hand oracle", "provider output", "source-linked"}
    assert {"termination", "extra month"} <= metal.cycles
    assert {"tfr", "employer_cost", "net"} <= metal.outputs
    assert alimentari.independence == {"source-linked"}


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
