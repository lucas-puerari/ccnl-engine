"""Source layout limits of the ``ccnl_engine`` package.

- at most three directories under ``ccnl_engine`` before a source file,
  i.e. ``ccnl_engine/<capability>/<layer>/<subfeature>/file.py``;
- every directory holding Python sources is a package with ``__init__.py``;
- a layer directory (``application``, ``service``, ``domain``) holds at least
  one module besides ``__init__.py``;
- no production module exceeds the line limit.

``data`` resource directories are exempt from the depth limit; hidden
directories and ``__pycache__`` are skipped.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

import pytest

_PACKAGE = Path(str(importlib.resources.files("ccnl_engine")))
_MAX_DEPTH = 3
_LAYERS = frozenset({"application", "service", "domain"})
_RESOURCE_DIRS = frozenset({"data"})
_PROD_LINE_LIMIT = 400

#: Modules allowed above :data:`_PROD_LINE_LIMIT`, with their own limit.
#: Each entry needs a reason and may only be removed.
_ALLOWED_LARGE_PROD: dict[str, int] = {}


def _skipped(part: str) -> bool:
    return part.startswith(".") or part == "__pycache__"


def _sources(package: Path) -> list[Path]:
    """Return the ``.py`` files of *package*, skipping hidden and cache dirs.

    Returns:
        Paths relative to *package*, sorted.
    """
    return sorted(
        path.relative_to(package)
        for path in package.rglob("*.py")
        if not any(_skipped(part) for part in path.relative_to(package).parts)
    )


def depth_violations(package: Path) -> list[str]:
    """Return source files nested deeper than :data:`_MAX_DEPTH` directories.

    Returns:
        Sorted relative paths with their depth.
    """
    return [
        f"{rel.as_posix()}: {len(rel.parts) - 1} directories"
        for rel in _sources(package)
        if len(rel.parts) - 1 > _MAX_DEPTH
        and not _RESOURCE_DIRS.intersection(rel.parts[:-1])
    ]


def missing_init(package: Path) -> list[str]:
    """Return directories on the path to a source file without ``__init__.py``.

    Returns:
        Sorted relative directory paths.
    """
    dirs = {parent for rel in _sources(package) for parent in rel.parents}
    return sorted(
        d.as_posix() for d in dirs if not (package / d / "__init__.py").is_file()
    )


def empty_layers(package: Path) -> list[str]:
    """Return layer directories whose only module is ``__init__.py``.

    Returns:
        Sorted relative directory paths.
    """
    sources = _sources(package)
    layers = {
        parent for rel in sources for parent in rel.parents if parent.name in _LAYERS
    }
    return sorted(
        layer.as_posix()
        for layer in layers
        if not any(
            layer in rel.parents and rel.name != "__init__.py" for rel in sources
        )
    )


def oversized_modules(package: Path, limit: int, allowed: dict[str, int]) -> list[str]:
    """Return modules longer than *limit* lines, or their entry in *allowed*.

    Returns:
        Sorted descriptions with line counts.
    """
    bad: list[str] = []
    for rel in _sources(package):
        lines = len((package / rel).read_text(encoding="utf-8").splitlines())
        cap = allowed.get(rel.as_posix(), limit)
        if lines > cap:
            bad.append(f"{rel.as_posix()}: {lines} lines (limit {cap})")
    return bad


# ---------------------------------------------------------------------------
# Real sources
# ---------------------------------------------------------------------------


def test_source_depth_within_limit() -> None:
    """No source file sits more than three directories under ccnl_engine."""
    assert depth_violations(_PACKAGE) == []


def test_every_source_directory_is_a_package() -> None:
    """Every directory holding Python sources has an ``__init__.py``."""
    assert missing_init(_PACKAGE) == []


def test_no_empty_layer_directory() -> None:
    """Layer directories exist only when they hold a module."""
    assert empty_layers(_PACKAGE) == []


def test_production_modules_below_line_limit() -> None:
    """No production module exceeds 400 lines unless explicitly exempted."""
    assert oversized_modules(_PACKAGE, _PROD_LINE_LIMIT, _ALLOWED_LARGE_PROD) == []


def test_analysis_sees_the_package() -> None:
    """The layout checks walk real sources, not an empty tree."""
    assert Path("api/facade.py") in _sources(_PACKAGE)


# ---------------------------------------------------------------------------
# Synthetic violations
# ---------------------------------------------------------------------------


def _tree(root: Path, *files: str) -> Path:
    """Create *files* (relative paths, empty content) under ``root/pkg``.

    Returns:
        The package directory.
    """
    package = root / "pkg"
    for name in files:
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return package


def test_deep_source_is_rejected(tmp_path: Path) -> None:
    """A file four directories deep is reported; data and caches are exempt."""
    package = _tree(
        tmp_path,
        "a/b/c/ok.py",
        "a/b/c/d/deep.py",
        "a/data/b/c/d/resource.py",
        "a/b/c/.cache/d/e.py",
        "a/b/c/__pycache__/x.py",
    )
    assert depth_violations(package) == ["a/b/c/d/deep.py: 4 directories"]


def test_directory_without_init_is_rejected(tmp_path: Path) -> None:
    """A source directory, or one of its parents, without __init__ is reported."""
    package = _tree(tmp_path, "__init__.py", "a/__init__.py", "a/x.py", "b/c/y.py")
    (package / "b" / "c" / "__init__.py").write_text("", encoding="utf-8")
    assert missing_init(package) == ["b"]


def test_empty_layer_is_rejected(tmp_path: Path) -> None:
    """A layer holding only ``__init__.py`` is reported; a nested module counts."""
    package = _tree(
        tmp_path,
        "cap/domain/__init__.py",
        "cap/service/__init__.py",
        "cap/service/sub/__init__.py",
        "cap/service/sub/x.py",
        "cap/other/__init__.py",
    )
    assert empty_layers(package) == ["cap/domain"]


@pytest.mark.parametrize(
    ("allowed", "expected"),
    [
        ({}, ["a.py: 3 lines (limit 2)"]),
        ({"a.py": 3}, []),
    ],
)
def test_oversized_module_is_rejected(
    tmp_path: Path, allowed: dict[str, int], expected: list[str]
) -> None:
    """A module above the limit is reported unless it has its own limit."""
    package = _tree(tmp_path, "a.py", "b.py")
    (package / "a.py").write_text("1\n2\n3\n", encoding="utf-8")
    assert oversized_modules(package, 2, allowed) == expected
