"""Tests for scripts/ci/check_structure.py measurements and baseline ratchet."""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "check_structure.py"
_MODULE = "_ci_check_structure"

_Measurements = dict[str, dict[str, int]]


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

_TIGHT = {
    "production_file_lines": 3,
    "test_file_lines": 3,
    "function_lines": 3,
    "class_lines": 4,
    "public_methods": 1,
    "source_depth": 1,
}


@pytest.fixture
def tight(monkeypatch: pytest.MonkeyPatch) -> None:
    """Shrink every limit so tiny synthetic sources can offend."""
    for rule, limit in _TIGHT.items():
        monkeypatch.setitem(cs.LIMITS, rule, limit)


def _write(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")


def _measure(text: str) -> _Measurements:
    found: _Measurements = {}
    cs.measure_source("m.py", textwrap.dedent(text), found)
    return found


# ---------------------------------------------------------------------------
# Line counting
# ---------------------------------------------------------------------------


def test_code_lines_skip_blanks_and_comments() -> None:
    """Blank and comment-only lines hold no code; a multi-line string does."""
    source = 'x = 1\n\n# note\ny = """a\nb"""  # tail\n'
    assert cs.code_lines(source) == {1, 4, 5}


def test_docstring_lines_cover_every_docstring() -> None:
    """Module, class and function docstrings count; other first lines do not."""
    source = textwrap.dedent('''\
        """Module."""


        class A:
            """Class
            docstring."""

            x = ...


        def f() -> None:
            print()


        async def g() -> None:
            """Async."""


        class B:
            ...
    ''')
    assert cs.docstring_lines(ast.parse(source)) == {1, 5, 6, 16}


def test_docstring_lines_of_empty_module() -> None:
    """An empty module has no docstring."""
    assert cs.docstring_lines(ast.parse("")) == set()


def test_function_lines_exclude_docstring_and_comments(tight: None) -> None:
    """Signature and code count; docstring, comments and blanks do not."""
    found = _measure('''\
        def f(
            a: int,
        ) -> int:
            """Doc
            string."""
            # comment

            return a
    ''')
    assert found == {"function_lines": {"m.py::f": 4}}


# ---------------------------------------------------------------------------
# Definitions and classes
# ---------------------------------------------------------------------------


def test_nested_definitions_have_dotted_names(tight: None) -> None:
    """Functions inside classes, functions and compound statements are found."""
    found = _measure("""\
        try:
            import x
        except ImportError:
            async def late() -> None:
                a = 1
                b = 2
                c = 3
        def outer() -> None:
            def inner() -> None:
                a = 1
                b = 2
                c = 3
    """)
    assert found["function_lines"] == {
        "m.py::late": 4,
        "m.py::outer": 5,
        "m.py::outer.inner": 4,
    }


def test_duplicate_names_keep_the_largest(tight: None) -> None:
    """A redefined name records the larger of its measurements."""
    found = _measure("""\
        if True:
            def f() -> None:
                a = 1
                b = 2
                c = 3
                d = 4
        else:
            def f() -> None:
                a = 1
                b = 2
                c = 3
    """)
    assert found["function_lines"] == {"m.py::f": 5}


@pytest.mark.parametrize(
    ("decorator", "declarative"),
    [
        ("field_validator('a')", True),
        ("pydantic.model_validator(mode='after')", True),
        ("validator", True),
        ("staticmethod", False),
        ("registry[0]", False),
    ],
)
def test_declarative_class_detection(decorator: str, declarative: bool) -> None:
    """Only validator and serializer methods keep a class declarative."""
    source = f"class A:\n    @{decorator}\n    def m(cls) -> None: ...\n"
    node = ast.parse(source).body[0]
    assert isinstance(node, ast.ClassDef)
    assert cs.is_declarative(node) is declarative


def test_class_without_methods_is_declarative() -> None:
    """A data-only class is declarative."""
    node = ast.parse("class A:\n    x: int\n").body[0]
    assert isinstance(node, ast.ClassDef)
    assert cs.is_declarative(node)


def test_class_rules(tight: None) -> None:
    """Long behaviour classes and public methods offend; data classes do not."""
    found = _measure("""\
        class Model:
            a: int
            b: int
            c: int
            d: int
            e: int

        class Service:
            def run(self) -> None: ...
            def stop(self) -> None: ...
            def _helper(self) -> None: ...
            x = 1
    """)
    assert found == {
        "class_lines": {"m.py::Service": 5},
        "public_methods": {"m.py::Service": 2},
    }


# ---------------------------------------------------------------------------
# Tree walk
# ---------------------------------------------------------------------------


def test_measure_tree(tmp_path: Path, tight: None) -> None:
    """File length, depth and definitions are measured per tree."""
    long_text = "a = 1\nb = 2\nc = 3\nd = 4\n"
    _write(tmp_path, "src/ccnl_engine/__init__.py")
    _write(tmp_path, "src/ccnl_engine/big.py", long_text)
    _write(tmp_path, "src/ccnl_engine/a/b/deep.py")
    _write(tmp_path, "src/ccnl_engine/a/data/b/resource.py")
    _write(tmp_path, "src/ccnl_engine/a/b/__pycache__/cached.py", long_text)
    _write(tmp_path, "tests/test_big.py", long_text)
    _write(tmp_path, "scripts/tool.py", "def f() -> None:\n" + "    x = 1\n" * 3)
    assert cs.measure_tree(tmp_path) == {
        "production_file_lines": {"src/ccnl_engine/big.py": 4},
        "source_depth": {"src/ccnl_engine/a/b/deep.py": 2},
        "test_file_lines": {"tests/test_big.py": 4},
        "function_lines": {"scripts/tool.py::f": 4},
    }


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("[]", "expected a JSON object"),
        ('{"nope": {}}', "unknown rule 'nope'"),
        ('{"function_lines": []}', "must map keys to integers"),
        ('{"function_lines": {"k": "1"}}', "must map keys to integers"),
    ],
)
def test_invalid_baseline_is_rejected(
    tmp_path: Path, content: str, message: str
) -> None:
    """A malformed baseline raises with the reason."""
    path = tmp_path / "baseline.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        cs.load_baseline(path)


def test_valid_baseline_is_loaded(tmp_path: Path) -> None:
    """A well-formed baseline round-trips."""
    path = tmp_path / "baseline.json"
    path.write_text('{"function_lines": {"k": 70}}', encoding="utf-8")
    assert cs.load_baseline(path) == {"function_lines": {"k": 70}}


def test_new_offender_fails() -> None:
    """An offender absent from the baseline is a problem."""
    report = cs.compare({"function_lines": {"k": 61}}, {})
    assert report.problems == ["function_lines: k is 61 (limit 60)"]
    assert report.notes == []


def test_worsened_offender_fails() -> None:
    """An offender above its baseline value is a problem."""
    report = cs.compare({"class_lines": {"k": 160}}, {"class_lines": {"k": 155}})
    assert report.problems == ["class_lines: k grew to 160 (baseline 155)"]


def test_stale_entry_fails() -> None:
    """A baseline entry that no longer offends must be removed."""
    report = cs.compare({}, {"source_depth": {"k": 4}})
    assert report.problems == [
        "source_depth: k is within the limit, remove it from the baseline"
    ]


def test_unchanged_and_improved_offenders_pass() -> None:
    """Matching or shrinking offenders pass; an improvement leaves a note."""
    report = cs.compare(
        {"test_file_lines": {"a": 600, "b": 510}},
        {"test_file_lines": {"a": 600, "b": 520}},
    )
    assert report.problems == []
    assert report.notes == ["test_file_lines: b improved to 510, lower its baseline"]


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def _long_test_tree(root: Path) -> None:
    _write(root, "src/ccnl_engine/__init__.py")
    _write(root, "tests/test_big.py", "a = 1\nb = 2\nc = 3\nd = 4\n")
    _write(root, "scripts/__init__.py")


def _run(root: Path, baseline: Path, *extra: str) -> int:
    return int(cs.main(["--root", str(root), "--baseline", str(baseline), *extra]))


def test_write_baseline_then_check_passes(
    tmp_path: Path, tight: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """A freshly written baseline matches the tree it was taken from."""
    _long_test_tree(tmp_path)
    baseline = tmp_path / "baseline.json"
    assert _run(tmp_path, baseline, "--write-baseline") == 0
    assert json.loads(baseline.read_text(encoding="utf-8")) == {
        "test_file_lines": {"tests/test_big.py": 4}
    }
    assert _run(tmp_path, baseline) == 0
    assert "test_file_lines 1" in capsys.readouterr().out


def test_check_reports_improvement_and_problems(
    tmp_path: Path, tight: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Improvements print a note; problems fail with exit code 1."""
    _long_test_tree(tmp_path)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        '{"test_file_lines": {"tests/test_big.py": 9}}', encoding="utf-8"
    )
    assert _run(tmp_path, baseline) == 0
    assert "note: test_file_lines: tests/test_big.py improved to 4" in (
        capsys.readouterr().out
    )
    baseline.write_text("{}", encoding="utf-8")
    assert _run(tmp_path, baseline) == 1
    assert "FAIL: test_file_lines: tests/test_big.py is 4" in capsys.readouterr().err


def test_unreadable_input_exits_with_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing baseline or an unparsable module is an error."""
    _long_test_tree(tmp_path)
    assert _run(tmp_path, tmp_path / "absent.json") == 2
    baseline = tmp_path / "baseline.json"
    baseline.write_text("{}", encoding="utf-8")
    _write(tmp_path, "scripts/broken.py", "def (:\n")
    assert _run(tmp_path, baseline) == 2
    assert capsys.readouterr().err.startswith("ERROR:")


def test_check_uses_the_given_baseline(tmp_path: Path, tight: None) -> None:
    """``check`` measures the tree and compares it with the baseline file."""
    _long_test_tree(tmp_path)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        '{"test_file_lines": {"tests/test_big.py": 4}}', encoding="utf-8"
    )
    assert cs.check(tmp_path, baseline) == cs.Report()
