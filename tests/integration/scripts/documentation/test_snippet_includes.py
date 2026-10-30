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

_ROOT = Path(__file__).parents[4]
_DOCS_DIR = _ROOT / "docs"
_MARKDOWN_FILES = sorted(
    p for p in _DOCS_DIR.rglob("*.md") if "_build" not in p.relative_to(_DOCS_DIR).parts
)
_VALID_MARKER = "--8<--"
_ANY_MARKER = re.compile(r"-{2}\s*8\s*<\s*-{2}")
_INCLUDE = re.compile(re.escape(_VALID_MARKER) + r' "([^"]+)"')


def _pages() -> list[tuple[str, str]]:
    return [
        (p.relative_to(_DOCS_DIR).as_posix(), p.read_text("utf-8"))
        for p in _MARKDOWN_FILES
    ]


def test_markdown_files_found() -> None:
    """The docs tree is present, so the checks below are not vacuous."""
    assert _MARKDOWN_FILES


def test_include_markers_are_well_formed() -> None:
    """Every snippet include marker is written exactly, without spaces."""
    bad = [
        (page, match.group())
        for page, text in _pages()
        for match in _ANY_MARKER.finditer(text)
        if match.group() != _VALID_MARKER
    ]
    assert bad == []


def test_include_targets_exist() -> None:
    """Every snippet include points to a file relative to the repo root."""
    missing = [
        (page, target)
        for page, text in _pages()
        for target in _INCLUDE.findall(text)
        if not (_ROOT / target).is_file()
    ]
    assert missing == []
