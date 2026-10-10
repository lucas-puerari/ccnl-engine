"""Layout of the test suite.

- the top level holds the categories ``knowledge``, ``unit`` and
  ``integration``, plus ``conftest.py`` and ``README.md``;
- a category holds only its mirror roots: ``ccnl_engine`` for ``knowledge``
  and ``unit``, ``ccnl_engine``, ``demo`` and ``scripts`` for ``integration``;
- a unit test, and an integration test below a mirror root directory, mirrors
  the module it tests: ``tests/unit/ccnl_engine/x/y/test_z.py`` needs
  ``src/ccnl_engine/x/y/z.py`` (or a ``z`` package); ``test_z_<suffix>.py``
  is accepted too.  Knowledge tests, the public API tests at the root of
  ``integration/ccnl_engine`` and the repository-rule tests of
  ``integration/scripts`` keep descriptive names;
- a test that mirrors no module and sits in ``knowledge`` or at the root of
  ``integration/ccnl_engine`` imports ``ccnl_engine`` only through the public
  API: its root and its public namespaces;
- besides tests, a directory holds only ``conftest.py``, ``builders[_x].py``,
  ``oracles[_x].py`` and ``support[_x].py``;
- at most five directories under ``tests`` before a file.

``scripts/structure/inventory.py`` checks every test path against the target
code tree; the test file line limit belongs to ``scripts/structure/check.py``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.integration.scripts.structure.support_imports import PUBLIC_NAMESPACES

_TESTS = Path(__file__).parents[3]
_REPO = _TESTS.parent
_TOP_FILES = frozenset({"conftest.py", "README.md"})
_MIRROR_ROOTS: dict[str, Path] = {
    "ccnl_engine": _REPO / "src" / "ccnl_engine",
    "scripts": _REPO / "scripts",
    "demo": _REPO / "demo",
}
#: Mirror roots allowed per category.
_CATEGORY_ROOTS: dict[str, frozenset[str]] = {
    "knowledge": frozenset({"ccnl_engine"}),
    "unit": frozenset({"ccnl_engine"}),
    "integration": frozenset(_MIRROR_ROOTS),
}
#: Tests that mirror no module yet read internal modules, with the reason.
_INTERNAL_READERS: dict[str, str] = {
    "integration/ccnl_engine/test_public_exports.py": (
        "pins the public surface against the modules that define it"
    ),
    "knowledge/ccnl_engine/knowledge/limitation/test_registry.py": (
        "matches the limitation registry with the modules that raise each one"
    ),
}
_HELPER = re.compile(r"^(?:conftest|(?:builders|oracles|support)(?:_[a-z0-9_]+)?)\.py$")
_MAX_DEPTH = 5


def _skipped(part: str) -> bool:
    return part.startswith(".") or part == "__pycache__"


def _files(root: Path, pattern: str) -> list[Path]:
    """Return files under *root* matching *pattern*, skipping cache dirs.

    Returns:
        Paths relative to *root*, sorted.
    """
    return sorted(
        path.relative_to(root)
        for path in root.rglob(pattern)
        if not any(_skipped(part) for part in path.relative_to(root).parts)
    )


def _test_files(root: Path) -> list[Path]:
    return _files(root, "test_*.py")


def category_violations(
    tests: Path, category_roots: dict[str, frozenset[str]]
) -> list[str]:
    """Return entries outside the categories and their mirror roots.

    Returns:
        Sorted relative paths of unexpected top-level and category entries.
    """
    bad: list[str] = []
    for entry in tests.iterdir():
        if _skipped(entry.name):
            continue
        if entry.is_file():
            if entry.name not in _TOP_FILES:
                bad.append(entry.name)
        elif entry.name not in category_roots:
            bad.append(entry.name)
        else:
            bad.extend(
                f"{entry.name}/{inner.name}"
                for inner in entry.iterdir()
                if not _skipped(inner.name)
                and inner.name not in category_roots[entry.name]
            )
    return sorted(bad)


def helper_violations(tests: Path) -> list[str]:
    """Return Python files that are neither tests nor named helpers.

    Returns:
        Sorted relative paths.
    """
    return [
        rel.as_posix()
        for rel in _files(tests, "*.py")
        if len(rel.parts) > 1
        and not rel.name.startswith("test_")
        and not _HELPER.match(rel.name)
    ]


def depth_violations(tests: Path) -> list[str]:
    """Return files nested deeper than :data:`_MAX_DEPTH` directories.

    Returns:
        Sorted relative paths with their depth.
    """
    return [
        f"{rel.as_posix()}: {len(rel.parts) - 1} directories"
        for rel in _files(tests, "*.py")
        if len(rel.parts) - 1 > _MAX_DEPTH
    ]


def _module_names(directory: Path) -> set[str]:
    """Return the module and package names in *directory*.

    Returns:
        Names of ``*.py`` modules other than ``__init__`` and of packages.
    """
    names = {path.stem for path in directory.glob("*.py") if path.name != "__init__.py"}
    names.update(
        path.name
        for path in directory.iterdir()
        if path.is_dir() and not _skipped(path.name)
    )
    return names


def _mirrors(stem: str, directory: Path) -> bool:
    if not directory.is_dir():
        return False
    return any(
        stem == name or stem.startswith(f"{name}_") for name in _module_names(directory)
    )


def _descriptive(category: str, rel: Path) -> bool:
    """Return whether a test of *category* at *rel* may keep a descriptive name.

    Returns:
        True for knowledge tests, public API tests and repository-rule tests.
    """
    root = rel.parts[0]
    return (
        category == "knowledge"
        or (
            category == "integration"
            and root == "ccnl_engine"
            and rel.parent.name == root
        )
        or root == "scripts"
    )


def mirror_violations(
    tests: Path,
    roots: dict[str, Path],
    category_roots: dict[str, frozenset[str]],
) -> list[str]:
    """Return tests below a mirror root that mirror no code directory or module.

    Returns:
        Sorted relative paths with the reason they do not mirror the code.
    """
    violations: list[str] = []
    for category, allowed in sorted(category_roots.items()):
        base = tests / category
        if not base.is_dir():
            continue
        for rel in _test_files(base):
            shown = f"{category}/{rel.as_posix()}"
            if len(rel.parts) < 2 or rel.parts[0] not in allowed:
                violations.append(f"{shown}: outside {sorted(allowed)}")
                continue
            directory = roots[rel.parts[0]].joinpath(*rel.parts[1:-1])
            stem = rel.stem.removeprefix("test_")
            if not directory.is_dir():
                violations.append(f"{shown}: no code directory {rel.parent}")
            elif not _descriptive(category, rel) and not _mirrors(stem, directory):
                violations.append(f"{shown}: no module for {stem!r}")
    return violations


def _imported_modules(tree: ast.Module) -> list[str]:
    """Return every module named by an ``import`` or ``from ... import``.

    Returns:
        Module names in source order; relative imports are skipped.
    """
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
    return names


def _public_only(tests: Path, roots: dict[str, Path]) -> list[Path]:
    """Return the tests that must reach ``ccnl_engine`` through its public API.

    Returns:
        Paths relative to *tests*: the knowledge tests and the root tests of
        ``integration/ccnl_engine`` that mirror no module.
    """
    knowledge = tests / "knowledge"
    found = [Path("knowledge") / rel for rel in _test_files(knowledge)]
    root = tests / "integration" / "ccnl_engine"
    found.extend(
        Path("integration", "ccnl_engine", path.name)
        for path in sorted(root.glob("test_*.py"))
        if not _mirrors(path.stem.removeprefix("test_"), roots["ccnl_engine"])
    )
    return found


def internal_import_violations(tests: Path, roots: dict[str, Path]) -> list[str]:
    """Return public API tests importing below the public API.

    Returns:
        Sorted ``path: module`` entries, one per internal import.
    """
    return sorted(
        f"{rel.as_posix()}: {name}"
        for rel in _public_only(tests, roots)
        if rel.as_posix() not in _INTERNAL_READERS
        for name in _imported_modules(
            ast.parse((tests / rel).read_text(encoding="utf-8"))
        )
        if name.startswith("ccnl_engine.") and name not in PUBLIC_NAMESPACES
    )


# ---------------------------------------------------------------------------
# The repository
# ---------------------------------------------------------------------------


def test_top_level_holds_only_categories() -> None:
    """Only the three categories and their mirror roots sit under ``tests``."""
    assert category_violations(_TESTS, _CATEGORY_ROOTS) == []


def test_helpers_are_named_by_role() -> None:
    """Besides tests, only conftests, builders, oracles and support modules."""
    assert helper_violations(_TESTS) == []


def test_test_depth_within_limit() -> None:
    """No file is nested deeper than five directories under ``tests``."""
    assert depth_violations(_TESTS) == []


def test_tests_mirror_the_code() -> None:
    """Each test sits in a code directory and, unless descriptive, its module."""
    assert mirror_violations(_TESTS, _MIRROR_ROOTS, _CATEGORY_ROOTS) == []


def test_public_api_tests_use_only_the_public_api() -> None:
    """Knowledge and public API tests import ``ccnl_engine`` publicly."""
    assert internal_import_violations(_TESTS, _MIRROR_ROOTS) == []


def test_internal_readers_still_exist() -> None:
    """Each exception names a test of the public API areas; the list only shrinks."""
    public = {rel.as_posix() for rel in _public_only(_TESTS, _MIRROR_ROOTS)}
    assert set(_INTERNAL_READERS) <= public


def test_analysis_sees_the_suite() -> None:
    """The checks above run on real trees, not on an empty directory."""
    assert _TESTS.name == "tests"
    assert all(root.is_dir() for root in _MIRROR_ROOTS.values())
    for category in _CATEGORY_ROOTS:
        assert _test_files(_TESTS / category), category


# ---------------------------------------------------------------------------
# The checks reject what they are meant to reject
# ---------------------------------------------------------------------------


def _touch(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_unknown_category_or_root_is_rejected(tmp_path: Path) -> None:
    """Entries outside the categories and their mirror roots are flagged."""
    for rel in (
        "acceptance/test_x.py",
        "test_loose.py",
        "conftest.py",
        "README.md",
        "unit/ccnl_engine/test_a.py",
        "unit/scripts/test_b.py",
        "integration/scripts/test_c.py",
        "knowledge/demo/test_d.py",
    ):
        _touch(tmp_path, rel)
    assert category_violations(tmp_path, _CATEGORY_ROOTS) == [
        "acceptance",
        "knowledge/demo",
        "test_loose.py",
        "unit/scripts",
    ]


def test_unnamed_helper_is_rejected(tmp_path: Path) -> None:
    """A helper must say its role: builders, oracles, support or conftest."""
    for rel in (
        "conftest.py",
        "unit/ccnl_engine/conftest.py",
        "unit/ccnl_engine/builders.py",
        "unit/ccnl_engine/x/oracles_2026.py",
        "unit/ccnl_engine/x/support_imports.py",
        "unit/ccnl_engine/x/test_a.py",
        "unit/ccnl_engine/x/helpers.py",
        "unit/ccnl_engine/x/_private.py",
    ):
        _touch(tmp_path, rel)
    assert helper_violations(tmp_path) == [
        "unit/ccnl_engine/x/_private.py",
        "unit/ccnl_engine/x/helpers.py",
    ]


def test_deep_file_is_rejected(tmp_path: Path) -> None:
    """Six directories under ``tests`` exceed the limit."""
    _touch(tmp_path, "unit/ccnl_engine/a/b/c/test_ok.py")
    _touch(tmp_path, "unit/ccnl_engine/a/b/c/d/test_deep.py")
    assert depth_violations(tmp_path) == [
        "unit/ccnl_engine/a/b/c/d/test_deep.py: 6 directories",
    ]


@pytest.mark.parametrize(
    ("test_path", "reason"),
    [
        ("unit/ccnl_engine/pkg/ledger/test_models.py", None),
        ("unit/ccnl_engine/pkg/ledger/test_models_posting.py", None),
        ("unit/ccnl_engine/pkg/ledger/test_events_union.py", None),
        ("unit/ccnl_engine/test_api_facade.py", None),
        ("integration/ccnl_engine/test_payslip_scenario.py", None),
        ("integration/scripts/ci/test_report.py", None),
        ("integration/scripts/ci/test_repository_rule.py", None),
        ("knowledge/ccnl_engine/pkg/ledger/test_legal_scenario.py", None),
        ("unit/ccnl_engine/pkg/ledger/test_missing.py", "no module for 'missing'"),
        ("unit/ccnl_engine/pkg/ledger/test_modelsx.py", "no module for 'modelsx'"),
        ("unit/ccnl_engine/test_scenario.py", "no module for 'scenario'"),
        (
            "integration/ccnl_engine/pkg/ledger/test_scenario.py",
            "no module for 'scenario'",
        ),
        ("unit/ccnl_engine/pkg/absent/test_models.py", "no code directory"),
        ("knowledge/ccnl_engine/absent/test_case.py", "no code directory"),
        ("unit/scripts/ci/test_report.py", "outside ['ccnl_engine']"),
        ("unit/test_loose.py", "outside ['ccnl_engine']"),
    ],
)
def test_mirror_check(tmp_path: Path, test_path: str, reason: str | None) -> None:
    """Tests sit in a code directory and, unless descriptive, name its module."""
    src = tmp_path / "src"
    _touch(src, "ccnl_engine/api.py")
    _touch(src, "ccnl_engine/pkg/ledger/models.py")
    _touch(src, "ccnl_engine/pkg/ledger/events/types.py")
    _touch(src, "scripts/ci/report.py")
    tests = tmp_path / "tests"
    _touch(tests, test_path)
    roots = {"ccnl_engine": src / "ccnl_engine", "scripts": src / "scripts"}
    category_roots = {
        "knowledge": frozenset({"ccnl_engine"}),
        "unit": frozenset({"ccnl_engine"}),
        "integration": frozenset(roots),
    }
    violations = mirror_violations(tests, roots, category_roots)
    if reason is None:
        assert violations == []
    else:
        assert len(violations) == 1
        assert violations[0].startswith(f"{test_path}: {reason}")


def test_internal_import_in_public_api_test_is_rejected(tmp_path: Path) -> None:
    """Deep imports are flagged in public API tests, not in mirrored tests."""
    src = tmp_path / "src" / "ccnl_engine"
    _touch(src, "api.py")
    imports = (
        "import ccnl_engine\n"
        "from ccnl_engine import PayrollEngine\n"
        "from ccnl_engine.events import OvertimeEvent\n"
        "from ccnl_engine.payroll.period.models_run import RunKind\n"
    )
    tests = tmp_path / "tests"
    _touch(tests, "integration/ccnl_engine/test_scenario.py", imports)
    _touch(tests, "integration/ccnl_engine/test_api.py", imports)
    _touch(tests, "knowledge/ccnl_engine/payroll/test_case.py", imports)
    _touch(tests, "knowledge/ccnl_engine/payroll/builders.py", imports)
    deep = "ccnl_engine.payroll.period.models_run"
    assert internal_import_violations(tests, {"ccnl_engine": src}) == [
        f"integration/ccnl_engine/test_scenario.py: {deep}",
        f"knowledge/ccnl_engine/payroll/test_case.py: {deep}",
    ]
