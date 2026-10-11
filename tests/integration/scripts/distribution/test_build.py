"""Tests that guard against silent packaging and demo startup failures.

Build hook: scripts/distribution/build.py compresses into .json.gz for the
wheel the knowledge manifest and every resource it lists.  A listed resource
missing on disk would fail the build; one not listed would be left out of the
wheel and unreadable at runtime.

Demo glue: demo/app.py imports ccnl_engine modules that run inside Pyodide.
An obsolete import path lets the wheel build succeed but crashes the browser at
runtime with ModuleNotFoundError.  demo/index.html or demo/ui.js carries a
WHEEL_VERSION placeholder that the build substitutes; if it goes missing, the
browser receives a literal filename and micropip.install fails silently.

All checks use AST parsing or plain string search so that neither hatchling
nor a browser runtime is required in the test environment.
"""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_BUILD_HOOK = _PROJECT_ROOT / "scripts" / "distribution" / "build.py"
_APP_PY = _PROJECT_ROOT / "demo" / "app.py"
_INDEX_HTML = _PROJECT_ROOT / "demo" / "index.html"


_KNOWLEDGE = _PROJECT_ROOT / "src" / "ccnl_engine" / "knowledge"


def _hook_functions() -> set[str]:
    """Return the names of the functions the build hook defines.

    Returns:
        Function names, read by AST so hatchling is not imported.
    """
    tree = ast.parse(_BUILD_HOOK.read_text(encoding="utf-8"))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


class TestBuildHookKnowledge:
    """The wheel carries the manifest and every resource it lists."""

    def test_the_hook_reads_the_manifest(self) -> None:
        """The hook compresses the files the manifest lists, not a directory glob."""
        source = _BUILD_HOOK.read_text(encoding="utf-8")
        assert "_knowledge_files" in _hook_functions()
        assert '"manifest.json"' in source

    def test_every_listed_resource_is_on_disk(self) -> None:
        """A path the manifest lists must exist, or the wheel build fails."""
        manifest = json.loads((_KNOWLEDGE / "manifest.json").read_text("utf-8"))
        missing = [
            entry["path"]
            for entry in manifest["resources"]
            if not (_KNOWLEDGE / entry["path"]).is_file()
        ]
        assert manifest["resources"]
        assert missing == []


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
        """WHEEL_VERSION must appear in index.html or ui.js for sed substitution."""
        ui_js = _PROJECT_ROOT / "demo" / "ui.js"
        html = _INDEX_HTML.read_text(encoding="utf-8")
        js = ui_js.read_text(encoding="utf-8") if ui_js.exists() else ""
        assert "WHEEL_VERSION" in html or "WHEEL_VERSION" in js, (
            "Neither demo/index.html nor demo/ui.js contains WHEEL_VERSION. "
            "The pages.yml sed pass would silently produce a broken page."
        )
