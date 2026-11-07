"""The mutation score: its perimeter, its counts and its record."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from scripts.quality.mutation.check import (
    RECORD,
    changed_modules,
    compute_score,
    evaluate,
    has_mutants,
    load_equivalent,
    load_floors,
    main,
    matching_modules,
    module_stats,
    mutant_glob,
    record,
    source_paths,
)


def test_the_perimeter_is_the_mutmut_source_paths() -> None:
    """The money-moving modules the campaigns mutate exist."""
    paths = source_paths()

    assert "src/ccnl_engine/irpef/deduction/rules.py" in paths
    assert all(path.startswith("src/ccnl_engine/") for path in paths)


def test_a_module_maps_to_the_pattern_of_its_mutants() -> None:
    """Mutmut names a mutant by the dotted module, then the function."""
    assert mutant_glob("src/ccnl_engine/irpef/rules.py") == "ccnl_engine.irpef.rules.*"


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        ("src/ccnl_engine/irpef/rules.py", True),
        ("src/ccnl_engine/ledger/models.py", False),
    ],
)
def test_a_module_of_declarations_only_yields_no_mutant(
    module: str, expected: bool
) -> None:
    """The enums of the ledger give mutmut nothing to mutate: no pattern."""
    assert has_mutants(module) is expected


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
        "equivalent": 0,
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


def test_the_core_scores_together_and_each_module_alone(
    tmp_path: Path,
) -> None:
    """A strong module never hides a weak one in the core.

    The core reaches the minimum together, but ``src/weak.py`` misses it
    alone; a floored module is held to its floor only.
    """
    _meta(tmp_path, "src/core.py", {f"c__{i}": 1 for i in range(9)})
    _meta(tmp_path, "src/weak.py", {"w__1": 1, "w__2": 0})
    _meta(tmp_path, "src/handler.py", {"h__1": 1, "h__2": 0})
    _meta(tmp_path, "src/models.py", {})

    scores, failures = evaluate(
        ("src/core.py", "src/weak.py", "src/handler.py", "src/models.py"),
        {"src/handler.py": 50.0},
        80.0,
        tmp_path,
    )

    assert scores["core"]["score"] == pytest.approx(90.9)
    assert scores["src/handler.py"]["score"] == pytest.approx(50.0)
    assert "src/models.py" not in scores
    assert failures == ["src/weak.py: 50.0% is below 80.0%"]


def test_an_equivalent_mutant_is_neither_killed_nor_survived(tmp_path: Path) -> None:
    """A classified mutant leaves the counts; it is reported apart."""
    _meta(tmp_path, "src/a.py", {"a__1": 1, "a__2": 0})

    stats = module_stats(("src/a.py",), tmp_path, frozenset({"a__2"}))

    assert stats["equivalent"] == 1
    assert stats["survived"] == 0
    assert compute_score(stats) == pytest.approx(100.0)


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


@pytest.fixture
def written(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Point the artifact and the versioned record at a temporary directory.

    Returns:
        The artifact and the versioned record paths; the perimeter is
        ``a.py`` and ``b.py``.
    """
    artifact, versioned = tmp_path / "m" / "score.json", tmp_path / "record.json"
    monkeypatch.setattr("scripts.quality.mutation.check._RECORD_PATH", artifact)
    monkeypatch.setattr("scripts.quality.mutation.check.RECORD", versioned)
    monkeypatch.setattr(
        "scripts.quality.mutation.check.source_paths", lambda: ("a.py", "b.py")
    )
    return artifact, versioned


def test_a_full_campaign_writes_the_versioned_record(
    written: tuple[Path, Path],
) -> None:
    """A check of the whole perimeter is the record the repository vouches for."""
    artifact, versioned = written

    entry = record({"core": {"score": 95.0}}, ("a.py", "b.py"), 93.0, versioned=True)

    assert json.loads(artifact.read_text(encoding="utf-8")) == entry
    assert entry["scope"] == "full"
    assert entry["min_score"] == pytest.approx(93.0)
    assert json.loads(versioned.read_text(encoding="utf-8"))["perimeter"] == [
        "a.py",
        "b.py",
    ]


def test_a_partial_check_is_marked_and_never_versioned(
    written: tuple[Path, Path],
) -> None:
    """Fewer modules than source_paths: a partial artifact, no record.json."""
    artifact, versioned = written

    entry = record({"core": {"score": 95.0}}, ("a.py",), 93.0)

    assert json.loads(artifact.read_text(encoding="utf-8"))["scope"] == "partial"
    assert entry["perimeter"] == ["a.py"]
    assert not versioned.exists()
    with pytest.raises(ValueError, match="whole source_paths"):
        record({}, ("a.py",), 93.0, versioned=True)
    assert not versioned.exists()


@pytest.mark.parametrize(
    ("argv", "perimeter", "scope"),
    [
        ([], ["a.py", "b.py"], "full"),
        (["--modules", "a.*"], ["a.py"], "partial"),
    ],
)
def test_the_command_versions_only_a_run_of_the_whole_perimeter(
    written: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    perimeter: list[str],
    scope: str,
) -> None:
    """``make mutation MODULE=GLOB`` scores the matched modules alone."""
    artifact, versioned = written
    monkeypatch.setattr(
        "scripts.quality.mutation.check.matching_modules",
        lambda globs, paths: tuple(p for p in paths if p.startswith(globs[0][0])),
    )
    monkeypatch.setattr(
        "scripts.quality.mutation.check.evaluate", lambda *_a, **_k: ({}, [])
    )
    monkeypatch.setattr(sys, "argv", ["check.py", *argv])

    main()

    entry = json.loads(artifact.read_text(encoding="utf-8"))
    assert entry["perimeter"] == perimeter
    assert entry["scope"] == scope
    assert versioned.exists() is (scope == "full")


def test_modules_matching_no_pattern_is_an_error(
    written: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pattern that selects nothing scores nothing: exit 1, nothing written."""
    artifact, _ = written
    monkeypatch.setattr(
        "scripts.quality.mutation.check.matching_modules", lambda *_a: ()
    )
    monkeypatch.setattr(sys, "argv", ["check.py", "--modules", "nothing.*"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    assert not artifact.exists()


@pytest.mark.parametrize(
    ("glob", "expected"),
    [
        ("ccnl_engine.irpef.rules.*", ("src/ccnl_engine/irpef/rules.py",)),
        (
            "ccnl_engine.irpef.rules.x__marginal_tax__mutmut_1",
            ("src/ccnl_engine/irpef/rules.py",),
        ),
        ("ccnl_engine.ledger.models.*", ()),
        ("ccnl_engine.irpef.r*", ("src/ccnl_engine/irpef/rules.py",)),
    ],
)
def test_a_pattern_selects_the_modules_whose_mutants_it_matches(
    glob: str, expected: tuple[str, ...]
) -> None:
    """The rule of mutmut's filter: fnmatch on the full mutant name."""
    perimeter = (
        "src/ccnl_engine/irpef/rules.py",
        "src/ccnl_engine/irpef/deduction/rules.py",
        "src/ccnl_engine/ledger/models.py",
    )
    assert matching_modules((glob,), perimeter) == expected


def test_every_equivalent_mutant_names_its_module_and_a_reason() -> None:
    """A classification without a reason excuses nothing."""
    globs = tuple(mutant_glob(m).removesuffix("*") for m in source_paths())
    for name, reason in load_equivalent().items():
        assert name.startswith(globs), name
        assert len(reason.split()) >= 5, name


def test_the_versioned_record_covers_the_current_perimeter() -> None:
    """The record measured every module mutated today, at the minimum of CI."""
    entry = json.loads(RECORD.read_text(encoding="utf-8"))
    workflow = Path(".github/workflows/mutation.yml").read_text(encoding="utf-8")

    assert entry["perimeter"] == list(source_paths())
    assert entry["min_score"] == pytest.approx(93.0)
    assert workflow.count("--min-score 93.0") == 2
    assert set(entry["scores"]) == {"core"} | {
        m for m in source_paths() if entry["scores"].get(m, {}).get("total")
    }
