"""Tests for the layout rules of check_structure.py.

``underscore_files`` and ``technical_directories`` freeze the files whose
name starts with an underscore and the directories named after a technical
layer: the baseline lists the current ones and only shrinks.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

    import pytest

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "structure" / "check.py"
_MODULE = "_ci_check_structure"


def _load() -> types.ModuleType:
    """Load the script once; its dataclass needs a ``sys.modules`` entry.

    Returns:
        The loaded module.
    """
    if _MODULE in sys.modules:
        return sys.modules[_MODULE]
    spec = importlib.util.spec_from_file_location(_MODULE, _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE] = module
    spec.loader.exec_module(module)
    return module


cs = _load()


def _write(root: Path, *paths: str) -> None:
    for rel in paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")


def _layout_tree(root: Path) -> None:
    _write(
        root,
        "src/ccnl_engine/__init__.py",
        "src/ccnl_engine/payroll/__init__.py",
        "src/ccnl_engine/payroll/domain/_private.py",
        "src/ccnl_engine/payroll/domain/models.py",
        "src/ccnl_engine/knowledge/ccnl/data/agreement.json",
        "src/ccnl_engine/payroll/__pycache__/_cached.pyc",
        "tests/fixtures/builders.py",
        "tests/.hidden/_note.txt",
        "scripts/ci/_helper.py",
        "demo/_build/_site.html",
        "demo/wheels/_wheel.whl",
        "demo/app.py",
    )
    (root / "src/ccnl_engine/payroll/__init__.py").write_text("X = 1\n", "utf-8")
    (root / "demo" / "service").mkdir(parents=True)


def _run(root: Path, baseline: Path, *extra: str) -> int:
    return int(cs.main(["--root", str(root), "--baseline", str(baseline), *extra]))


def test_layout_offenders_skip_root_init_hidden_cache_and_demo_build(
    tmp_path: Path,
) -> None:
    """Every file and directory type counts; the exempt places do not."""
    _layout_tree(tmp_path)
    files, dirs = cs.layout_offenders(tmp_path)
    assert [path.as_posix() for path in files] == [
        "scripts/ci/_helper.py",
        "src/ccnl_engine/payroll/__init__.py",
        "src/ccnl_engine/payroll/domain/_private.py",
    ]
    assert [path.as_posix() for path in dirs] == [
        "demo/service",
        "src/ccnl_engine/knowledge/ccnl/data",
        "src/ccnl_engine/payroll/domain",
        "tests/fixtures",
    ]


def test_layout_offenders_of_a_tree_without_roots(tmp_path: Path) -> None:
    """Absent roots hold no offender."""
    assert cs.layout_offenders(tmp_path) == ([], [])


def test_measure_tree_records_each_layout_offender_once(tmp_path: Path) -> None:
    """Each offender is one baseline entry with the value 1."""
    _write(tmp_path, "src/ccnl_engine/__init__.py", "tests/unit/data/_case.py")
    found = cs.measure_tree(tmp_path)
    assert found["underscore_files"] == {"tests/unit/data/_case.py": 1}
    assert found["technical_directories"] == {"tests/unit/data": 1}


def test_layout_rules_have_a_zero_limit_and_target() -> None:
    """Any new offender fails; the target equals the limit."""
    for rule in ("underscore_files", "technical_directories"):
        assert cs.LIMITS[rule] == 0
        assert cs.TARGETS[rule] == 0


def test_new_init_file_fails_against_the_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A baselined tree passes; a new ``__init__.py`` with code or directory fails.

    A docstring-only package marker under ``src`` is not an offender.
    """
    _layout_tree(tmp_path)
    baseline = tmp_path / "baseline.json"
    assert _run(tmp_path, baseline, "--write-baseline") == 0
    recorded = json.loads(baseline.read_text(encoding="utf-8"))
    assert len(recorded["underscore_files"]) == 3
    assert len(recorded["technical_directories"]) == 4
    assert _run(tmp_path, baseline) == 0
    marker = tmp_path / "src" / "ccnl_engine" / "payroll" / "ledger" / "__init__.py"
    marker.parent.mkdir(parents=True)
    marker.write_text('"""The ledger domain (package marker)."""\n', encoding="utf-8")
    assert _run(tmp_path, baseline) == 0
    code = tmp_path / "src" / "ccnl_engine" / "payroll" / "period" / "__init__.py"
    code.parent.mkdir(parents=True)
    code.write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "tests" / "unit" / "application").mkdir(parents=True)
    assert _run(tmp_path, baseline) == 1
    err = capsys.readouterr().err
    assert (
        "FAIL: underscore_files: src/ccnl_engine/payroll/period/__init__.py is 1 "
        "(limit 0)"
    ) in err
    assert "FAIL: technical_directories: tests/unit/application is 1" in err


def test_removed_offender_must_leave_the_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The baseline shrinks: a renamed module must drop its entry."""
    _layout_tree(tmp_path)
    baseline = tmp_path / "baseline.json"
    assert _run(tmp_path, baseline, "--write-baseline") == 0
    private = tmp_path / "src/ccnl_engine/payroll/domain/_private.py"
    private.rename(private.with_name("rules.py"))
    assert _run(tmp_path, baseline) == 1
    assert (
        "underscore_files: src/ccnl_engine/payroll/domain/_private.py is within "
        "the limit, remove it from the baseline"
    ) in capsys.readouterr().err


def test_repository_baseline_lists_the_current_layout() -> None:
    """The real baseline holds every underscore file and technical directory."""
    baseline = cs.load_baseline(cs.BASELINE)
    files, dirs = cs.layout_offenders(cs.ROOT)
    underscore = baseline.get("underscore_files", {})
    assert set(underscore) == {path.as_posix() for path in files}
    assert set(baseline.get("technical_directories", {})) == {
        path.as_posix() for path in dirs
    }
    assert "src/ccnl_engine/__init__.py" not in underscore
