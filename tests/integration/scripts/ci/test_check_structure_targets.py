"""Tests for the Markdown rule and the 80% targets of check_structure.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

    import pytest

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "check_structure.py"
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


def _write(root: Path, rel: str, lines: int = 0) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x\n" * lines, encoding="utf-8")


def _markdown_tree(root: Path) -> None:
    _write(root, "README.md", 5)
    _write(root, "REVIEW.md", 5)
    _write(root, "TODO.md", 5)
    _write(root, "docs/guide.md", 5)
    _write(root, "docs/engine/fiscal.md", 2)
    _write(root, "docs/contracts/generated.md", 5)
    _write(root, "docs/_build/docs/page.md", 5)
    _write(root, "docs/.hidden/page.md", 5)
    _write(root, "docs/notes.txt", 5)


def test_markdown_files_skip_audit_notes_and_generated_pages(tmp_path: Path) -> None:
    """Only hand-written pages are measured: top level and ``docs``."""
    _markdown_tree(tmp_path)
    assert [path.as_posix() for path in cs.markdown_files(tmp_path)] == [
        "README.md",
        "docs/engine/fiscal.md",
        "docs/guide.md",
    ]


def test_markdown_files_without_docs(tmp_path: Path) -> None:
    """A repository without ``docs`` measures its top-level pages only."""
    _write(tmp_path, "README.md", 1)
    assert cs.markdown_files(tmp_path) == [Path("README.md")]


def test_long_markdown_page_offends(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A page above the Markdown limit is an offender like a long module."""
    monkeypatch.setitem(cs.LIMITS, "markdown_lines", 3)
    _markdown_tree(tmp_path)
    assert cs.measure_tree(tmp_path) == {
        "markdown_lines": {"README.md": 5, "docs/guide.md": 5}
    }


def test_markdown_rule_is_a_known_baseline_rule(tmp_path: Path) -> None:
    """The baseline accepts Markdown entries."""
    baseline = tmp_path / "baseline.json"
    baseline.write_text('{"markdown_lines": {"README.md": 700}}', encoding="utf-8")
    assert cs.load_baseline(baseline) == {"markdown_lines": {"README.md": 700}}


def test_targets_sit_at_or_below_the_limits() -> None:
    """Every rule has a target that does not exceed its hard limit."""
    assert cs.TARGETS.keys() == cs.LIMITS.keys()
    assert all(cs.TARGETS[rule] <= limit for rule, limit in cs.LIMITS.items())


def test_measure_tree_with_targets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Measuring against the targets records values above them only."""
    monkeypatch.setitem(cs.TARGETS, "markdown_lines", 2)
    monkeypatch.setitem(cs.TARGETS, "function_lines", 2)
    _markdown_tree(tmp_path)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text(
        "def f() -> None:\n" + "    x = 1\n" * 2, encoding="utf-8"
    )
    assert cs.measure_tree(tmp_path, cs.TARGETS) == {
        "markdown_lines": {"README.md": 5, "docs/guide.md": 5},
        "function_lines": {"scripts/tool.py::f": 3},
    }
    assert cs.measure_tree(tmp_path) == {}


def test_target_report_lines() -> None:
    """The report lists entries in rule order, then by key."""
    above = {
        "markdown_lines": {"docs/b.md": 500, "docs/a.md": 460},
        "production_file_lines": {"src/ccnl_engine/m.py": 250},
    }
    assert cs.target_report(above) == [
        "production_file_lines: src/ccnl_engine/m.py is 250 (target 240)",
        "markdown_lines: docs/a.md is 460 (target 450)",
        "markdown_lines: docs/b.md is 500 (target 450)",
    ]


def _run(root: Path, *extra: str) -> int:
    baseline = root / "baseline.json"
    baseline.write_text("{}", encoding="utf-8")
    return int(cs.main(["--root", str(root), "--baseline", str(baseline), *extra]))


def test_targets_never_fail_the_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Entries above a target are counted, listed on request, never failed."""
    monkeypatch.setitem(cs.TARGETS, "markdown_lines", 2)
    _markdown_tree(tmp_path)
    assert _run(tmp_path) == 0
    out = capsys.readouterr().out
    assert "markdown_lines 2" in out.splitlines()[-1]
    assert "target:" not in out
    assert _run(tmp_path, "--targets") == 0
    assert "target: markdown_lines: docs/guide.md is 5 (target 2)" in (
        capsys.readouterr().out
    )
