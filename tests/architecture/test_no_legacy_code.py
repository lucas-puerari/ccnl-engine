"""Legacy models, wrapper imports and re-export shims stay removed.

Import direction and domain purity live in ``test_dependencies``, source
layout in ``test_structure_limits`` and test layout in ``test_test_layout``.

These tests gate structural properties of the codebase.  Each test documents
the *current* set of allowed exceptions and fails when a new violation is
introduced, preventing accidental regression.

Allowed exceptions are listed explicitly so that any new violation requires a
deliberate decision to extend the list rather than silently widening scope.
"""

from __future__ import annotations

import ast
import importlib.resources
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SRC = Path(str(importlib.resources.files("ccnl_engine"))).parent  # .../src


def _python_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def _is_type_checking_test(node: ast.expr) -> bool:
    """Return True when *node* is a reference to ``TYPE_CHECKING``.

    Returns:
        True for ``if TYPE_CHECKING:`` and ``if typing.TYPE_CHECKING:`` guards.
    """
    return (isinstance(node, ast.Name) and node.id == "TYPE_CHECKING") or (
        isinstance(node, ast.Attribute) and node.attr == "TYPE_CHECKING"
    )


def _type_checking_node_ids(tree: ast.Module) -> set[int]:
    """Return AST node ids of all nodes nested inside TYPE_CHECKING blocks.

    Returns:
        Set of ``id(node)`` for every AST node that is a descendant of an
        ``if TYPE_CHECKING:`` guard in *tree*.
    """
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking_test(node.test):
            ids.update(id(child) for child in ast.walk(node))
    return ids


def _class_definitions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


# ---------------------------------------------------------------------------
# Test: one employment model
#
# The employment relationship has a single public model,
# payroll/domain/employment.py::Employment.  No EmploymentFacts remains.
# ---------------------------------------------------------------------------


def test_employment_defined_once() -> None:
    """Employment is defined once and EmploymentFacts nowhere."""
    found: dict[str, list[str]] = {"Employment": [], "EmploymentFacts": []}
    for path in _python_files(_SRC / "ccnl_engine"):
        for name in set(_class_definitions(path)) & found.keys():
            found[name].append(str(path.relative_to(_SRC)))
    assert found == {
        "Employment": ["ccnl_engine/payroll/domain/employment.py"],
        "EmploymentFacts": [],
    }


# ---------------------------------------------------------------------------
# Test: zero imports of the removed engine wrapper anywhere in the repository
#
# ccnl_engine.engine was the legacy wrapper package (including the legacy
# engine.payroll namespace).  After its removal, no source or test file may
# import from it.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parents[2]


def _engine_wrapper_imports(path: Path) -> list[str]:
    """Return any runtime import referencing ccnl_engine.engine.*.

    Returns:
        List of module paths starting with ``ccnl_engine.engine``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tc_ids = _type_checking_node_ids(tree)
    return [
        node.module or ""
        for node in ast.walk(tree)
        if id(node) not in tc_ids
        and isinstance(node, ast.ImportFrom)
        and (
            node.module == "ccnl_engine.engine"
            or (node.module or "").startswith("ccnl_engine.engine.")
        )
    ]


def test_no_engine_wrapper_imports() -> None:
    """No file in src/ or tests/ may import from ccnl_engine.engine.*."""
    violations: list[str] = []
    for root in (_REPO_ROOT / "src", _REPO_ROOT / "tests"):
        for path in _python_files(root):
            found = _engine_wrapper_imports(path)
            if found:
                rel = str(path.relative_to(_REPO_ROOT))
                violations.append(f"{rel}: {sorted(set(found))}")
    assert not violations, "Forbidden ccnl_engine.engine imports found:\n" + "\n".join(
        violations
    )


# ---------------------------------------------------------------------------
# Test: no re-export-only modules
#
# A module whose body is only imports (plus docstring and __all__) is a shim.
# The package root is the public API; the other exceptions are package
# interfaces over their own underscore-private submodules.
# ---------------------------------------------------------------------------

_ALLOWED_REEXPORT_MODULES: frozenset[str] = frozenset({
    "ccnl_engine/__init__.py",
    "ccnl_engine/contract/domain/identity/__init__.py",
    "ccnl_engine/payroll/domain/events/__init__.py",
    "ccnl_engine/payroll/domain/pay_items/__init__.py",
})


def _is_reexport_only(tree: ast.Module) -> bool:
    """Return True when *tree* holds imports and nothing but metadata.

    Returns:
        True for a module made of a docstring, imports and ``__all__`` only,
        with at least one import other than ``from __future__``.
    """
    has_import = False
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if isinstance(node, ast.Import | ast.ImportFrom):
            has_import = True
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            continue
        return False
    return has_import


def test_no_reexport_only_modules() -> None:
    """No module in src/ only re-exports names defined elsewhere."""
    found = {
        str(path.relative_to(_SRC))
        for path in _python_files(_SRC / "ccnl_engine")
        if _is_reexport_only(ast.parse(path.read_text(encoding="utf-8")))
    }
    assert found == _ALLOWED_REEXPORT_MODULES
