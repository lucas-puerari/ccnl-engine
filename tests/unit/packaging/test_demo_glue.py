"""Smoke tests for the demo glue layer (demo/app.py and demo/index.html).

These tests run in CPython and do not require Pyodide or a browser.  They
guard against two classes of silent failure:

- An obsolete import in app.py that lets the wheel build succeed but crashes
  the browser at runtime with ``ModuleNotFoundError``.
- A missing ``WHEEL_VERSION`` substitution that leaves the placeholder
  literal in the served HTML, causing ``micropip.install`` to fail.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_APP_PY = _PROJECT_ROOT / "demo" / "app.py"
_INDEX_HTML = _PROJECT_ROOT / "demo" / "index.html"


def _extract_top_level_imports(source: str) -> list[str]:
    """Return all module names from top-level ``from X import Y`` statements.

    Returns:
        Module name strings, one per ``from X import Y`` node found.
    """
    tree = ast.parse(source)
    return [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]


class TestDemoAppImports:
    """All ccnl_engine imports in app.py must resolve in the installed package."""

    def test_all_ccnl_imports_are_valid(self) -> None:
        """Every ccnl_engine import in app.py must be importable."""
        source = _APP_PY.read_text(encoding="utf-8")
        modules = _extract_top_level_imports(source)
        ccnl_modules = [m for m in modules if m.startswith("ccnl_engine")]
        assert ccnl_modules, "No ccnl_engine imports found in demo/app.py"
        for module in ccnl_modules:
            importlib.import_module(module)


class TestDemoIndexHtml:
    """index.html must carry the WHEEL_VERSION placeholder for CI substitution."""

    def test_wheel_version_placeholder_present(self) -> None:
        """WHEEL_VERSION must appear in index.html for the pages.yml sed pass."""
        html = _INDEX_HTML.read_text(encoding="utf-8")
        assert "WHEEL_VERSION" in html, (
            "demo/index.html does not contain the WHEEL_VERSION placeholder. "
            "The pages.yml sed substitution would silently produce a broken page."
        )
