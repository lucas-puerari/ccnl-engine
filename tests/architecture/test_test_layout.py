"""Layout of the test suite.

- the top level holds only the categories ``unit``, ``integration``,
  ``acceptance``, ``architecture`` and ``fixtures``;
- a unit or integration test mirrors the module it tests:
  ``tests/unit/ccnl_engine/x/y/test_z.py`` needs ``src/ccnl_engine/x/y/z.py``
  (or ``_z.py``, or a ``z`` package); ``test_z_<suffix>.py`` is accepted too.
  Integration tests may also mirror ``scripts`` and ``demo``;
- acceptance tests live in ``public_api`` or ``legal_scenarios`` and import
  ``ccnl_engine`` only through its root, the public API;
- ``fixtures`` holds data and helpers, never tests;
- at most five directories under ``tests`` before a file, ``fixtures`` aside;
- no test file exceeds the line limit without an explicit exception.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_TESTS = Path(__file__).parents[1]
_REPO = _TESTS.parent
_CATEGORIES = frozenset({
    "unit",
    "integration",
    "acceptance",
    "architecture",
    "fixtures",
})
_ACCEPTANCE_AREAS = frozenset({"public_api", "legal_scenarios"})
_MIRROR_ROOTS: dict[str, Path] = {
    "ccnl_engine": _REPO / "src" / "ccnl_engine",
    "scripts": _REPO / "scripts",
    "demo": _REPO / "demo",
}
#: Mirror roots allowed per category; unit tests cover the package only.
_CATEGORY_ROOTS: dict[str, frozenset[str]] = {
    "unit": frozenset({"ccnl_engine"}),
    "integration": frozenset(_MIRROR_ROOTS),
}
_MAX_DEPTH = 5

_TEST_LINE_LIMIT = 1000
#: Files allowed above the limit, with their own ceiling; empty by design.
_ALLOWED_LARGE_TESTS: dict[str, int] = {}


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


def category_violations(tests: Path) -> list[str]:
    """Return top-level entries of *tests* outside the known categories.

    Returns:
        Sorted names of unexpected directories and test files at top level.
    """
    return sorted(
        entry.name
        for entry in tests.iterdir()
        if not _skipped(entry.name)
        and (
            (entry.is_dir() and entry.name not in _CATEGORIES)
            or (entry.is_file() and entry.name.startswith("test_"))
        )
    )


def acceptance_violations(tests: Path) -> list[str]:
    """Return acceptance tests outside the public API and legal scenario areas.

    Returns:
        Sorted relative paths of misplaced acceptance tests.
    """
    root = tests / "acceptance"
    if not root.is_dir():
        return []
    return [
        f"acceptance/{rel.as_posix()}"
        for rel in _test_files(root)
        if len(rel.parts) < 2 or rel.parts[0] not in _ACCEPTANCE_AREAS
    ]


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


def internal_import_violations(tests: Path) -> list[str]:
    """Return acceptance modules importing below the ``ccnl_engine`` root.

    Returns:
        Sorted ``path: module`` entries, one per internal import.
    """
    root = tests / "acceptance"
    if not root.is_dir():
        return []
    return sorted(
        f"acceptance/{rel.as_posix()}: {name}"
        for rel in _files(root, "*.py")
        for name in _imported_modules(
            ast.parse((root / rel).read_text(encoding="utf-8"))
        )
        if name.startswith("ccnl_engine.")
    )


def fixture_violations(tests: Path) -> list[str]:
    """Return test modules and conftests found under ``fixtures``.

    Returns:
        Sorted relative paths.
    """
    root = tests / "fixtures"
    if not root.is_dir():
        return []
    found = _test_files(root) + _files(root, "conftest.py")
    return sorted(f"fixtures/{rel.as_posix()}" for rel in found)


def depth_violations(tests: Path) -> list[str]:
    """Return files nested deeper than :data:`_MAX_DEPTH` directories.

    Returns:
        Sorted relative paths with their depth; ``fixtures`` is exempt.
    """
    return [
        f"{rel.as_posix()}: {len(rel.parts) - 1} directories"
        for rel in _files(tests, "*.py")
        if rel.parts[0] != "fixtures" and len(rel.parts) - 1 > _MAX_DEPTH
    ]


def _module_names(directory: Path) -> set[str]:
    """Return the module and package names in *directory*, underscore-stripped.

    Returns:
        Names of ``*.py`` modules other than ``__init__`` and of packages.
    """
    names = {
        path.stem.lstrip("_")
        for path in directory.glob("*.py")
        if path.name != "__init__.py"
    }
    names.update(
        path.name.lstrip("_")
        for path in directory.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )
    return names


def _mirrors(stem: str, directory: Path) -> bool:
    if not directory.is_dir():
        return False
    return any(
        stem == name or stem.startswith(f"{name}_") for name in _module_names(directory)
    )


def mirror_violations(
    tests: Path,
    roots: dict[str, Path],
    category_roots: dict[str, frozenset[str]],
) -> list[str]:
    """Return unit and integration tests that mirror no source module.

    Returns:
        Sorted relative paths with the reason they do not mirror a module.
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
            if not _mirrors(stem, directory):
                violations.append(f"{shown}: no module for {stem!r}")
    return violations


# ---------------------------------------------------------------------------
# The repository
# ---------------------------------------------------------------------------


def test_top_level_holds_only_categories() -> None:
    """Only the five categories sit directly under ``tests``."""
    assert category_violations(_TESTS) == []


def test_acceptance_tests_sit_in_known_areas() -> None:
    """Acceptance tests live in ``public_api`` or ``legal_scenarios``."""
    assert acceptance_violations(_TESTS) == []


def test_acceptance_uses_only_the_public_api() -> None:
    """Acceptance tests import ``ccnl_engine`` names from the root only."""
    assert internal_import_violations(_TESTS) == []


def test_fixtures_hold_no_tests() -> None:
    """``fixtures`` is data, not an executable category."""
    assert fixture_violations(_TESTS) == []


def test_test_depth_within_limit() -> None:
    """No test file is nested deeper than five directories under ``tests``."""
    assert depth_violations(_TESTS) == []


def test_unit_and_integration_mirror_sources() -> None:
    """Each unit and integration test mirrors an existing source module."""
    assert mirror_violations(_TESTS, _MIRROR_ROOTS, _CATEGORY_ROOTS) == []


def test_test_files_below_line_limit() -> None:
    """No test file exceeds 1 000 lines unless explicitly exempted."""
    violations: list[str] = []
    for rel in _files(_TESTS, "*.py"):
        lines = len((_TESTS / rel).read_text(encoding="utf-8").splitlines())
        limit = _ALLOWED_LARGE_TESTS.get(rel.as_posix(), _TEST_LINE_LIMIT)
        if lines > limit:
            violations.append(f"{rel.as_posix()}: {lines} lines (limit {limit})")
    assert not violations, "Test files exceeding line limit:\n" + "\n".join(violations)


def test_large_test_allowlist_has_no_stale_entry() -> None:
    """Every line-limit exception names an existing file above the limit."""
    stale = [
        rel
        for rel in _ALLOWED_LARGE_TESTS
        if not (_TESTS / rel).is_file()
        or len((_TESTS / rel).read_text(encoding="utf-8").splitlines())
        <= _TEST_LINE_LIMIT
    ]
    assert stale == []


def test_analysis_sees_the_suite() -> None:
    """The checks above run on real trees, not on an empty directory."""
    assert _TESTS.name == "tests"
    assert all(root.is_dir() for root in _MIRROR_ROOTS.values())
    for category in ("unit", "integration", "acceptance", "architecture"):
        assert _test_files(_TESTS / category), category


# ---------------------------------------------------------------------------
# The checks reject what they are meant to reject
# ---------------------------------------------------------------------------


def _touch(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_unknown_category_is_rejected(tmp_path: Path) -> None:
    """A top-level directory or test module outside the categories is flagged."""
    _touch(tmp_path, "reference/test_x.py")
    _touch(tmp_path, "test_loose.py")
    _touch(tmp_path, "conftest.py")
    _touch(tmp_path, "unit/__init__.py")
    assert category_violations(tmp_path) == ["reference", "test_loose.py"]


def test_misplaced_acceptance_test_is_rejected(tmp_path: Path) -> None:
    """Acceptance tests outside the two areas are flagged."""
    _touch(tmp_path, "acceptance/test_loose.py")
    _touch(tmp_path, "acceptance/regression/test_x.py")
    _touch(tmp_path, "acceptance/public_api/test_ok.py")
    assert acceptance_violations(tmp_path) == [
        "acceptance/regression/test_x.py",
        "acceptance/test_loose.py",
    ]


def test_missing_areas_yield_no_violation(tmp_path: Path) -> None:
    """A tree without acceptance or fixtures has nothing to flag there."""
    assert acceptance_violations(tmp_path) == []
    assert fixture_violations(tmp_path) == []


def test_internal_import_in_acceptance_is_rejected(tmp_path: Path) -> None:
    """Deep ``ccnl_engine`` imports are flagged; root imports are not."""
    module = tmp_path / "acceptance" / "public_api" / "test_x.py"
    module.parent.mkdir(parents=True)
    module.write_text(
        "import ccnl_engine\n"
        "import ccnl_engine.api\n"
        "from ccnl_engine import PayrollEngine\n"
        "from ccnl_engine.payroll.domain.run import RunKind\n",
        encoding="utf-8",
    )
    assert internal_import_violations(tmp_path) == [
        "acceptance/public_api/test_x.py: ccnl_engine.api",
        "acceptance/public_api/test_x.py: ccnl_engine.payroll.domain.run",
    ]
    assert internal_import_violations(tmp_path / "absent") == []


def test_test_under_fixtures_is_rejected(tmp_path: Path) -> None:
    """Test modules and conftests under ``fixtures`` are flagged."""
    _touch(tmp_path, "fixtures/expected/case.json")
    _touch(tmp_path, "fixtures/helpers.py")
    _touch(tmp_path, "fixtures/contracts/test_x.py")
    _touch(tmp_path, "fixtures/conftest.py")
    assert fixture_violations(tmp_path) == [
        "fixtures/conftest.py",
        "fixtures/contracts/test_x.py",
    ]


def test_deep_test_is_rejected(tmp_path: Path) -> None:
    """Six directories under ``tests`` exceed the limit; fixtures are exempt."""
    _touch(tmp_path, "unit/ccnl_engine/a/b/c/test_ok.py")
    _touch(tmp_path, "unit/ccnl_engine/a/b/c/d/test_deep.py")
    _touch(tmp_path, "fixtures/a/b/c/d/e/f/helper.py")
    assert depth_violations(tmp_path) == [
        "unit/ccnl_engine/a/b/c/d/test_deep.py: 6 directories",
    ]


@pytest.mark.parametrize(
    ("test_path", "reason"),
    [
        ("unit/ccnl_engine/pkg/domain/test_calendar.py", None),
        ("unit/ccnl_engine/pkg/domain/test_calendar_override.py", None),
        ("unit/ccnl_engine/pkg/domain/test_private.py", None),
        ("unit/ccnl_engine/pkg/domain/test_events_union.py", None),
        ("unit/ccnl_engine/test_pkg_version.py", None),
        ("integration/scripts/ci/test_report.py", None),
        ("unit/ccnl_engine/pkg/domain/test_missing.py", "no module for 'missing'"),
        ("unit/ccnl_engine/pkg/domain/test_calendarx.py", "no module for 'calendarx'"),
        ("unit/ccnl_engine/pkg/absent/test_calendar.py", "no module for 'calendar'"),
        ("unit/scripts/ci/test_report.py", "outside ['ccnl_engine']"),
        ("unit/test_loose.py", "outside ['ccnl_engine']"),
    ],
)
def test_mirror_check(tmp_path: Path, test_path: str, reason: str | None) -> None:
    """Tests must name a module, private module or package of their directory."""
    src = tmp_path / "src"
    _touch(src, "ccnl_engine/pkg/__init__.py")
    _touch(src, "ccnl_engine/pkg/domain/calendar.py")
    _touch(src, "ccnl_engine/pkg/domain/_private.py")
    _touch(src, "ccnl_engine/pkg/domain/events/__init__.py")
    _touch(src, "scripts/ci/report.py")
    tests = tmp_path / "tests"
    _touch(tests, test_path)
    roots = {"ccnl_engine": src / "ccnl_engine", "scripts": src / "scripts"}
    category_roots = {
        "unit": frozenset({"ccnl_engine"}),
        "integration": frozenset(roots),
    }
    expected = [] if reason is None else [f"{test_path}: {reason}"]
    assert mirror_violations(tests, roots, category_roots) == expected
