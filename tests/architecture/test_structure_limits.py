"""Source layout limits of the ``ccnl_engine`` package.

- every directory holding Python sources is a package with ``__init__.py``;
- a layer directory (``application``, ``service``, ``domain``) holds at least
  one module besides ``__init__.py``;
- the size and depth limits of ``scripts/ci/check_structure.py`` hold
  against its baseline.

Hidden directories and ``__pycache__`` are skipped.
"""

from __future__ import annotations

import importlib.resources
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

_PACKAGE = Path(str(importlib.resources.files("ccnl_engine")))
_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check_structure.py"
_MODULE = "_ci_check_structure"
_LAYERS = frozenset({"application", "service", "domain"})


def _check_structure() -> types.ModuleType:
    """Load ``scripts/ci/check_structure.py``, the owner of the size rules.

    Returns:
        The loaded module, shared with other tests through ``sys.modules``.
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


# ---------------------------------------------------------------------------
# Real sources
# ---------------------------------------------------------------------------


def test_structure_limits_hold_against_baseline() -> None:
    """Size and depth limits hold; baseline entries only shrink."""
    script = _check_structure()
    report = script.check(script.ROOT, script.BASELINE)
    assert report.problems == []


def test_every_source_directory_is_a_package() -> None:
    """Every directory holding Python sources has an ``__init__.py``."""
    assert missing_init(_PACKAGE) == []


def test_no_empty_layer_directory() -> None:
    """Layer directories exist only when they hold a module."""
    assert empty_layers(_PACKAGE) == []


def test_analysis_sees_the_package() -> None:
    """The layout checks walk real sources, not an empty tree."""
    assert Path("api.py") in _sources(_PACKAGE)


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
