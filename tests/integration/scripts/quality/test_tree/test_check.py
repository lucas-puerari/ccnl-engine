"""The test tree mirrors the code, apart from the listed exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.quality.test_tree.check import EXCEPTIONS, ROOT, main, misplaced

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
