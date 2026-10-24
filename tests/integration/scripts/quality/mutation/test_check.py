"""The mutation score: its perimeter, its counts and its record."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.quality.mutation.check import (
    changed_modules,
    compute_score,
    evaluate,
    load_floors,
    module_stats,
    mutant_glob,
    record,
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


def test_the_core_scores_together_and_each_floored_module_alone(
    tmp_path: Path,
) -> None:
    """The core must reach the minimum; a floored module only its floor."""
    _meta(tmp_path, "src/core.py", {"c__1": 1, "c__2": 1, "c__3": 1, "c__4": 0})
    _meta(tmp_path, "src/handler.py", {"h__1": 1, "h__2": 0})

    scores, failures = evaluate(
        ("src/core.py", "src/handler.py"), {"src/handler.py": 50.0}, 80.0, tmp_path
    )

    assert scores["core"]["score"] == pytest.approx(75.0)
    assert scores["src/handler.py"]["score"] == pytest.approx(50.0)
    assert failures == ["core: 75.0% is below 80.0%"]


def test_a_floored_module_cannot_fall(tmp_path: Path) -> None:
    """A floored module changed alone is checked against its floor only."""
    _meta(tmp_path, "src/handler.py", {"h__1": 1, "h__2": 0, "h__3": 0})

    scores, failures = evaluate(
        ("src/handler.py",), {"src/handler.py": 50.0}, 93.0, tmp_path
    )

    assert "core" not in scores
    assert failures == ["src/handler.py: 33.3% is below 50.0%"]


def test_every_floor_is_a_module_of_the_perimeter_below_the_minimum() -> None:
    """A floor names a mutated module and stays below the general 93%."""
    floors = load_floors()

    assert set(floors) <= set(source_paths())
    assert all(floor < 93.0 for floor in floors.values())


@pytest.mark.parametrize("versioned", [True, False])
def test_a_full_campaign_writes_the_versioned_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, versioned: bool
) -> None:
    """The artifact always; the versioned record only for the whole perimeter."""
    artifact, versioned_path = tmp_path / "m" / "score.json", tmp_path / "record.json"
    monkeypatch.setattr("scripts.quality.mutation.check._RECORD_PATH", artifact)
    monkeypatch.setattr("scripts.quality.mutation.check.RECORD", versioned_path)

    entry = record({"core": {"score": 95.0}}, ("a.py",), 93.0, versioned=versioned)

    assert json.loads(artifact.read_text(encoding="utf-8")) == entry
    assert entry["min_score"] == pytest.approx(93.0)
    assert entry["perimeter"] == ["a.py"]
    assert versioned_path.exists() is versioned
