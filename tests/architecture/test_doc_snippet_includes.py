"""Guard the pymdownx.snippets include markers in the Markdown docs.

A formatter that treats a Python fence as code rewrites the include marker
into an arithmetic expression (dashes, ``8``, ``<`` separated by spaces).
The docs build then renders the marker literally instead of the included
file.  These tests fail on any mangled marker and on any include whose
target file does not exist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).parents[2]
_DOCS_DIR = _ROOT / "docs"
_MARKDOWN_FILES = sorted(
    p for p in _DOCS_DIR.rglob("*.md") if "_build" not in p.relative_to(_DOCS_DIR).parts
)
_VALID_MARKER = "--8<--"
_ANY_MARKER = re.compile(r"-{2}\s*8\s*<\s*-{2}")
_INCLUDE = re.compile(re.escape(_VALID_MARKER) + r' "([^"]+)"')


def _ids(path: Path) -> str:
    return path.relative_to(_DOCS_DIR).as_posix()


def test_markdown_files_found() -> None:
    """The docs tree is present, so the parametrized checks are not vacuous."""
    assert _MARKDOWN_FILES


@pytest.mark.parametrize("page", _MARKDOWN_FILES, ids=_ids)
def test_include_markers_are_well_formed(page: Path) -> None:
    """Every snippet include marker is written exactly, without spaces."""
    bad = [
        match.group()
        for match in _ANY_MARKER.finditer(page.read_text(encoding="utf-8"))
        if match.group() != _VALID_MARKER
    ]
    assert not bad, f"malformed snippet markers: {bad}"


@pytest.mark.parametrize("page", _MARKDOWN_FILES, ids=_ids)
def test_include_targets_exist(page: Path) -> None:
    """Every snippet include points to a file relative to the repo root."""
    targets = _INCLUDE.findall(page.read_text(encoding="utf-8"))
    missing = [t for t in targets if not (_ROOT / t).is_file()]
    assert not missing, f"missing snippet targets: {missing}"
