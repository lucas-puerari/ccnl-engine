"""Coverage of the bundled CCNLs: one derivation, no flag of their own.

A CCNL file used to declare ``gross``, ``net`` and ``work_rules`` flags
beside per-feature statuses, and the two disagreed.  Coverage now derives
from the capability registry, lowered by the ``missing`` notes of the file:
no file declares a flag, and no layer reads implemented while one of its
capabilities is not.
"""

from __future__ import annotations

import importlib.resources
import json

import pytest

_DATA = importlib.resources.files("ccnl_engine.knowledge").joinpath("agreement")
_FILENAMES = sorted(
    entry.name for entry in _DATA.iterdir() if entry.name.endswith(".json")
)
_FLAGS = frozenset({"gross", "net", "work_rules", "work_rules_features"})


def test_bundle_is_not_empty() -> None:
    """A packaging mistake must not make the contract below vacuous."""
    assert _FILENAMES


@pytest.mark.parametrize("filename", _FILENAMES)
def test_no_file_declares_a_coverage_flag(filename: str) -> None:
    """The coverage block of a file holds notes only."""
    coverage = json.loads(_DATA.joinpath(filename).read_text(encoding="utf-8"))[
        "coverage"
    ]
    assert not _FLAGS & coverage.keys()
