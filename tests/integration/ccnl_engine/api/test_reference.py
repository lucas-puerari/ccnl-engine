"""The API reference documents the public API, and only the public API.

Each public name has a ``::: <namespace>.<name>`` directive on a page of
``docs/api/``, and every directive there names a public module or one of
its names: the reference never documents an internal module, whose path
may change without notice.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

from tests.integration.ccnl_engine.api.test_public_exports import EXPECTED_PUBLIC

_API_DOCS = Path(__file__).parents[4] / "docs" / "api"
_DIRECTIVE = re.compile(r"^::: ([\w.]+)$", re.MULTILINE)


def _directives() -> set[str]:
    """Return the targets of every mkdocstrings directive of the reference.

    Returns:
        Dotted paths, e.g. ``"ccnl_engine.inputs.Apprentice"``.
    """
    return {
        target
        for page in _API_DOCS.glob("*.md")
        for target in _DIRECTIVE.findall(page.read_text(encoding="utf-8"))
    }


@pytest.mark.parametrize("module", sorted(EXPECTED_PUBLIC))
def test_every_public_name_is_documented(module: str) -> None:
    """Each name of ``__all__`` has a directive under its import path."""
    documented = _directives()
    names = importlib.import_module(module).__all__

    missing = sorted(name for name in names if f"{module}.{name}" not in documented)
    assert missing == []


def test_the_reference_documents_no_internal_module() -> None:
    """A directive names a public module or a name it exports."""
    public = set(EXPECTED_PUBLIC) | {
        f"{module}.{name}"
        for module, names in EXPECTED_PUBLIC.items()
        for name in names
    }

    assert _directives() - public == set()
