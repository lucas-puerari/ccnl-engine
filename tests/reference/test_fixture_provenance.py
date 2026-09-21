"""Validate provenance metadata on reference case fixtures.

These tests run against the JSON files in ``tests/reference/cases/`` and
assert that their ``source`` blocks are structurally correct.  They are
distinct from ``test_reference.py`` (which checks engine output) and from
``test_result_schema_enforcement.py`` (which validates result/schema shape).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_CASES_DIR = Path(__file__).parent / "cases"
_ALL_CASES = sorted(_CASES_DIR.glob("*.json"))
_VALID_VERIFICATION_STATUSES = frozenset({"verified", "unverified"})


def _load(path: Path) -> dict[str, object]:
    data: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    return data


@pytest.mark.parametrize("path", _ALL_CASES, ids=lambda p: p.stem)
def test_source_is_dict_when_present(path: Path) -> None:
    """A 'source' field, if present, must be a JSON object, not a string."""
    case = _load(path)
    src = case.get("source")
    if src is not None:
        assert isinstance(src, dict), (
            f"{path.name}: 'source' must be a dict, got {type(src).__name__}"
        )


@pytest.mark.parametrize("path", _ALL_CASES, ids=lambda p: p.stem)
def test_verification_status_is_known_value(path: Path) -> None:
    """'source.verification_status', if present, must be a known value."""
    case = _load(path)
    src = case.get("source")
    if not isinstance(src, dict):
        return
    status = src.get("verification_status")
    if status is not None:
        assert status in _VALID_VERIFICATION_STATUSES, (
            f"{path.name}: unknown verification_status {status!r}; "
            f"allowed: {sorted(_VALID_VERIFICATION_STATUSES)}"
        )
