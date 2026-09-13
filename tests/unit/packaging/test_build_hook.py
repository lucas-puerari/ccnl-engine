"""Tests that guard against silent packaging and demo startup failures.

Build hook: scripts/packaging/build_hook.py lists source directories whose JSON
files it compresses into .json.gz for the wheel.  A typo in any of those
paths silently produces an empty wheel — no data files are found, no error is
raised — which breaks all runtime data access without any test failure.

Demo glue: demo/app.py imports ccnl_engine modules that run inside Pyodide.
An obsolete import path lets the wheel build succeed but crashes the browser at
runtime with ModuleNotFoundError.  demo/index.html carries a WHEEL_VERSION
placeholder that pages.yml substitutes at publish time; if it goes missing, the
browser receives a literal filename and micropip.install fails silently.

All checks use AST parsing or plain string search so that neither hatchling
nor a browser runtime is required in the test environment.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_BUILD_HOOK = _PROJECT_ROOT / "scripts" / "packaging" / "build_hook.py"
_APP_PY = _PROJECT_ROOT / "demo" / "app.py"
_INDEX_HTML = _PROJECT_ROOT / "demo" / "index.html"


def _extract_data_dirs() -> list[tuple[str, str]]:
    """Parse _DATA_DIRS from build_hook.py without importing it.

    Returns:
        List of (dist_prefix, src_rel) tuples, same as _DATA_DIRS.

    Raises:
        AssertionError: If _DATA_DIRS cannot be found in the build hook.
    """
    tree = ast.parse(_BUILD_HOOK.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        # _DATA_DIRS uses a type annotation so it is an AnnAssign, not Assign.
        if not (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_DATA_DIRS"
            and isinstance(node.value, ast.List)
        ):
            continue
        pairs: list[tuple[str, str]] = []
        for elt in node.value.elts:
            if not isinstance(elt, ast.Tuple) or len(elt.elts) != 2:
                continue
            a, b = elt.elts
            if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
                pairs.append((str(a.value), str(b.value)))
        return pairs
    msg = "_DATA_DIRS not found in build_hook.py"
    raise AssertionError(msg)


_DATA_DIRS = _extract_data_dirs()


@pytest.mark.parametrize(
    ("dist_prefix", "src_rel"),
    _DATA_DIRS,
    ids=[src for _, src in _DATA_DIRS],
)
class TestBuildHookDataDirs:
    """Each entry in _DATA_DIRS must point to a real, populated directory."""

    def test_source_dir_exists(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory listed in the build hook must exist."""
        src_dir = _PROJECT_ROOT / src_rel
        assert src_dir.is_dir(), (
            f"Build hook source directory not found: {src_rel!r}. "
            "Check the _DATA_DIRS entries in scripts/packaging/build_hook.py."
        )

    def test_source_dir_has_json_files(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory must contain at least one .json file."""
        src_dir = _PROJECT_ROOT / src_rel
        json_files = list(src_dir.glob("*.json"))
        assert len(json_files) > 0, (
            f"No .json files found in {src_rel!r}. "
            "The wheel would be built without any data files."
        )


def _ccnl_imports_in(source: str) -> list[str]:
    """Return ccnl_engine module names from top-level ``from X import Y`` nodes.

    Returns:
        Unique module name strings that start with ``ccnl_engine``.
    """
    tree = ast.parse(source)
    return [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("ccnl_engine")
    ]


class TestDemoGlue:
    """Demo startup must not be broken by stale imports or a missing placeholder."""

    def test_app_py_imports_resolve(self) -> None:
        """Every ccnl_engine import in demo/app.py must exist in the package."""
        modules = _ccnl_imports_in(_APP_PY.read_text(encoding="utf-8"))
        assert modules, "No ccnl_engine imports found in demo/app.py"
        for module in modules:
            importlib.import_module(module)

    def test_index_html_has_wheel_version_placeholder(self) -> None:
        """WHEEL_VERSION must appear in index.html for the pages.yml sed pass."""
        html = _INDEX_HTML.read_text(encoding="utf-8")
        assert "WHEEL_VERSION" in html, (
            "demo/index.html does not contain the WHEEL_VERSION placeholder. "
            "The pages.yml sed substitution would silently produce a broken page."
        )
