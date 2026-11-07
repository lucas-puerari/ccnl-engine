"""The test tree mirrors the code, apart from the listed exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.quality.test_tree.check import (
    EXCEPTIONS,
    OUTSIDE_MUTATION,
    ROOT,
    main,
    misplaced,
    outside_mutation,
)

if TYPE_CHECKING:
    import pytest

if TYPE_CHECKING:
    from pathlib import Path


def test_the_real_tree_mirrors_the_code() -> None:
    """Every test directory is a code directory, a module or an exception."""
    assert misplaced() == []
    assert main() == 0


def test_every_exception_still_exists() -> None:
    """A listed exception that was moved away is removed from the list."""
    missing = [
        name
        for name in EXCEPTIONS
        if not (
            ROOT
            / "tests"
            / name.split("/", 1)[0]
            / "ccnl_engine"
            / name.split("/", 1)[1]
        ).is_dir()
    ]
    assert missing == []


def test_a_directory_that_mirrors_nothing_is_reported(tmp_path: Path) -> None:
    """A test under a made-up concept is named; one under a module is not."""
    (tmp_path / "src" / "ccnl_engine" / "period").mkdir(parents=True)
    (tmp_path / "src" / "ccnl_engine" / "period" / "services.py").touch()
    for folder in ("period/services", "made_up"):
        path = tmp_path / "tests" / "unit" / "ccnl_engine" / folder
        path.mkdir(parents=True)
        (path / "test_x.py").touch()
    assert misplaced(tmp_path) == ["unit/made_up"]


def test_the_mutation_category_mirrors_the_code(tmp_path: Path) -> None:
    """The tests mutmut runs follow the same mirror rule as the others."""
    (tmp_path / "src" / "ccnl_engine" / "irpef").mkdir(parents=True)
    for folder in ("irpef", "made_up"):
        path = tmp_path / "tests" / "mutation" / "ccnl_engine" / folder
        path.mkdir(parents=True)
        (path / "test_x.py").touch()
    assert misplaced(tmp_path) == ["mutation/made_up"]


def test_every_test_of_a_mutated_module_is_under_mutation() -> None:
    """The real tree keeps every test of a mutated module in mutation/."""
    assert outside_mutation() == []


def test_every_test_kept_out_of_mutation_still_tests_a_mutated_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A listed file that was moved or renamed is removed from the list."""
    monkeypatch.setattr("scripts.quality.test_tree.check.OUTSIDE_MUTATION", {})

    assert set(OUTSIDE_MUTATION) <= set(outside_mutation())


def test_a_test_of_a_mutated_module_outside_mutation_is_reported(
    tmp_path: Path,
) -> None:
    """Named after the module or in its directory, outside mutation/: reported."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.mutmut]\nsource_paths = ["src/ccnl_engine/irpef/rules.py"]\n',
        encoding="utf-8",
    )
    files = (
        "integration/ccnl_engine/irpef/test_rules_wiring.py",
        "knowledge/ccnl_engine/irpef/rules/test_oracle.py",
        "unit/ccnl_engine/irpef/test_rules.py",
        "mutation/ccnl_engine/irpef/test_rules.py",
        "unit/ccnl_engine/irpef/test_services.py",
        "unit/ccnl_engine/irpef/test_rulesets.py",
    )
    for name in files:
        path = tmp_path / "tests" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    assert outside_mutation(tmp_path) == list(files[:3])
