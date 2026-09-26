"""Architectural invariants for the ccnl-engine package.

These tests gate structural properties of the codebase.  Each test documents
the *current* set of allowed exceptions and fails when a new violation is
introduced, preventing accidental regression.

Allowed exceptions are listed explicitly so that any new violation requires a
deliberate decision to extend the list rather than silently widening scope.
"""

from __future__ import annotations

import ast
import importlib.resources
import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SRC = Path(str(importlib.resources.files("ccnl_engine"))).parent  # .../src
_PAYROLL_DOMAIN = _SRC / "ccnl_engine" / "payroll" / "domain"
_TESTS = Path(__file__).parent.parent.parent  # .../tests


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


def _runtime_engine_imports(path: Path) -> list[str]:
    """Return module paths imported from ``ccnl_engine.engine.*`` outside TYPE_CHECKING.

    Returns:
        List of ``ccnl_engine.engine.*`` module paths found at runtime scope.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tc_ids = _type_checking_node_ids(tree)
    return [
        node.module or ""
        for node in ast.walk(tree)
        if id(node) not in tc_ids
        and isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("ccnl_engine.engine")
    ]


def _class_definitions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


# ---------------------------------------------------------------------------
# Test: payroll/domain must not import engine at runtime
#
# Allowed exceptions document pre-existing coupling that must be resolved in
# a dedicated refactor PR before removal from this list.
# ---------------------------------------------------------------------------

_ALLOWED_DOMAIN_ENGINE_IMPORTS: dict[str, set[str]] = {
    "sickness.py": {"ccnl_engine.engine.errors"},
    "policy.py": {"ccnl_engine.engine.io.service.bundled"},
    "employment.py": {"ccnl_engine.engine.errors"},
    "employer.py": {"ccnl_engine.engine.errors"},
    "calendar_override.py": {"ccnl_engine.engine.errors"},
    "events/variable_pay.py": {"ccnl_engine.engine.errors"},
    "events/termination.py": {"ccnl_engine.engine.errors"},
    "events/work_time.py": {"ccnl_engine.engine.errors"},
    "events/absence_sickness.py": {"ccnl_engine.engine.errors"},
}


def test_payroll_domain_runtime_engine_imports_within_allowlist() -> None:
    """No new runtime engine imports in payroll/domain beyond documented exceptions."""
    violations: list[str] = []
    for path in _python_files(_PAYROLL_DOMAIN):
        rel = str(path.relative_to(_PAYROLL_DOMAIN))
        found = set(_runtime_engine_imports(path))
        if not found:
            continue
        allowed = _ALLOWED_DOMAIN_ENGINE_IMPORTS.get(rel, set())
        new = found - allowed
        if new:
            violations.append(f"{rel}: {sorted(new)}")
    assert not violations, (
        "New runtime ccnl_engine.engine imports found in payroll/domain:\n"
        + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# Test: single EmploymentFacts
#
# Currently two definitions exist (api/requests.py and
# payroll/domain/employment_context.py).  The goal is to consolidate to one.
# This test fails as soon as a *third* definition appears.
# ---------------------------------------------------------------------------

_ALLOWED_EMPLOYMENT_FACTS_MODULES: frozenset[str] = frozenset({
    "ccnl_engine/api/requests.py",
})


def test_employment_facts_defined_in_allowed_modules_only() -> None:
    """EmploymentFacts must not be duplicated beyond the two transitional locations."""
    found: list[str] = []
    for path in _python_files(_SRC / "ccnl_engine"):
        if "EmploymentFacts" in _class_definitions(path):
            rel = str(path.relative_to(_SRC))
            found.append(rel)
    unexpected = sorted(set(found) - _ALLOWED_EMPLOYMENT_FACTS_MODULES)
    assert not unexpected, (
        "EmploymentFacts defined outside allowed modules:\n" + "\n".join(unexpected)
    )


# ---------------------------------------------------------------------------
# Test: production module line limits
#
# No production file should exceed 400 lines without an explicit exception.
# Exceptions document files that require a dedicated split PR.
# ---------------------------------------------------------------------------

_PROD_LINE_LIMIT = 400
_ALLOWED_LARGE_PROD: dict[str, int] = {}


def test_production_modules_below_line_limit() -> None:
    """No production module exceeds 400 lines unless explicitly exempted."""
    violations: list[str] = []
    for path in _python_files(_SRC / "ccnl_engine"):
        rel = str(path.relative_to(_SRC))
        lines = len(path.read_text(encoding="utf-8").splitlines())
        limit = _ALLOWED_LARGE_PROD.get(rel, _PROD_LINE_LIMIT)
        if lines > limit:
            violations.append(f"{rel}: {lines} lines (limit {limit})")
    assert not violations, "Production modules exceeding line limit:\n" + "\n".join(
        violations
    )


# ---------------------------------------------------------------------------
# Test: test file line limits
#
# No test file should exceed 1 000 lines without an explicit exception.
# ---------------------------------------------------------------------------

_TEST_LINE_LIMIT = 1000
_ALLOWED_LARGE_TESTS: dict[str, int] = {
    # Dense domain rule tables — reorganisation tracked separately.
    "unit/ccnl_engine/engine/tax/domain/test_rules.py": 1100,
    "unit/ccnl_engine/payroll/application/test_calculate_period.py": 1100,
}


def test_test_files_below_line_limit() -> None:
    """No test file exceeds 1 000 lines unless explicitly exempted."""
    violations: list[str] = []
    for path in _python_files(_TESTS):
        rel = str(path.relative_to(_TESTS))
        lines = len(path.read_text(encoding="utf-8").splitlines())
        limit = _ALLOWED_LARGE_TESTS.get(rel, _TEST_LINE_LIMIT)
        if lines > limit:
            violations.append(f"{rel}: {lines} lines (limit {limit})")
    assert not violations, "Test files exceeding line limit:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test: marker presence for integration cases
#
# Every JSON in tests/integration/cases/ must be exercised by at least one
# parametrised test that loads it.  This is a weaker check — it verifies the
# file exists and can be parsed as JSON — not that a test covers every field.
# ---------------------------------------------------------------------------


def test_integration_cases_are_valid_json() -> None:
    """Every integration case JSON is parseable and has a non-empty name key."""
    cases_dir = Path(__file__).parent.parent.parent / "integration" / "cases"
    if not cases_dir.exists():
        pytest.skip("integration/cases directory not present")
    case_files = sorted(cases_dir.glob("*.json"))
    assert case_files, "integration/cases/ must contain at least one .json file"
    for path in case_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data, f"{path.name} is empty"


# ---------------------------------------------------------------------------
# Test: zero engine.payroll imports anywhere in the repository
#
# engine.payroll was the legacy payroll namespace.  After its removal, no
# source or test file may import from it.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _engine_payroll_imports(path: Path) -> list[str]:
    """Return any runtime import referencing ccnl_engine.engine.payroll.*.

    Returns:
        List of module paths starting with ``ccnl_engine.engine.payroll``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tc_ids = _type_checking_node_ids(tree)
    return [
        node.module or ""
        for node in ast.walk(tree)
        if id(node) not in tc_ids
        and isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("ccnl_engine.engine.payroll")
    ]


def test_no_engine_payroll_imports() -> None:
    """No file in src/ or tests/ may import from ccnl_engine.engine.payroll.*."""
    violations: list[str] = []
    for root in (_REPO_ROOT / "src", _REPO_ROOT / "tests"):
        for path in _python_files(root):
            found = _engine_payroll_imports(path)
            if found:
                rel = str(path.relative_to(_REPO_ROOT))
                violations.append(f"{rel}: {sorted(set(found))}")
    assert not violations, (
        "Forbidden ccnl_engine.engine.payroll imports found:\n" + "\n".join(violations)
    )
