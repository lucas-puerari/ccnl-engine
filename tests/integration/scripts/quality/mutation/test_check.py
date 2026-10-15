"""The mutation score: its perimeter, its counts and its record."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.quality.mutation.check import (
    changed_modules,
    compute_score,
    module_stats,
    mutant_glob,
    source_paths,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_the_perimeter_is_the_mutmut_source_paths() -> None:
    """The money-moving modules the campaigns mutate exist."""
    paths = source_paths()

    assert "src/ccnl_engine/irpef/deduction/rules.py" in paths
    assert all(path.startswith("src/ccnl_engine/") for path in paths)


def test_a_module_maps_to_the_pattern_of_its_mutants() -> None:
    """Mutmut names a mutant by the dotted module, then the function."""
    assert mutant_glob("src/ccnl_engine/irpef/rules.py") == "ccnl_engine.irpef.rules.*"


def test_only_changed_modules_of_the_perimeter_are_selected() -> None:
    """Nothing changed since HEAD; a ref with no common file gives nothing."""
    assert changed_modules("HEAD", source_paths()) == ()


def _meta(root: Path, module: str, codes: dict[str, int | None]) -> None:
    path = root / f"{module}.meta"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"exit_code_by_key": codes}), encoding="utf-8")


def test_the_counts_come_from_each_mutant_of_the_modules(tmp_path: Path) -> None:
    """1 and 3 kill, 0 survives, None did not run, anything else is other."""
    _meta(tmp_path, "src/a.py", {"a.x__1": 1, "a.x__2": 0, "a.x__3": None})
    _meta(tmp_path, "src/b.py", {"b.x__1": 3, "b.x__2": 36})

    stats = module_stats(("src/a.py", "src/b.py"), tmp_path)

    assert stats == {
        "killed": 2,
        "survived": 1,
        "other": 1,
        "not_checked": 1,
        "total": 4,
    }
    assert compute_score(stats) == pytest.approx(50.0)


def test_a_module_without_results_is_an_error(tmp_path: Path) -> None:
    """A score over modules that did not run is no score."""
    with pytest.raises(FileNotFoundError):
        module_stats(("src/missing.py",), tmp_path)


def test_no_mutant_scores_zero() -> None:
    """A campaign with no mutants does not pass by accident."""
    assert not compute_score({"killed": 0, "total": 0})
