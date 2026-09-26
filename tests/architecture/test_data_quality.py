"""Validate provenance metadata and shape of the expected-value fixtures.

These tests run against the JSON files in ``tests/fixtures/expected/`` and
assert that each declares a known ``verification`` status consistent with its
``source`` block. The rules live in :mod:`tests.architecture._provenance`.
Scenario fixtures in ``tests/fixtures/expected/scenarios/`` must parse as
non-empty JSON.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.architecture._provenance import (
    CASES_DIR,
    count_by_status,
    load_case,
    verification_errors,
)

if TYPE_CHECKING:
    from pathlib import Path

_ALL_CASES = sorted(CASES_DIR.glob("*.json"))
_SCENARIOS_DIR = CASES_DIR / "scenarios"
_SOURCE: dict[str, object] = {"document": "CCNL", "section": "Art. 1"}


def test_cases_exist() -> None:
    """The fixture directory is not accidentally empty."""
    assert _ALL_CASES


@pytest.mark.parametrize("path", _ALL_CASES, ids=lambda p: p.stem)
def test_case_verification_is_valid(path: Path) -> None:
    """Every case declares a known status consistent with its source."""
    assert verification_errors(load_case(path)) == [], path.name


def test_status_counts_cover_every_case() -> None:
    """Every case falls into exactly one known status bucket."""
    cases = [load_case(path) for path in _ALL_CASES]
    assert sum(count_by_status(cases).values()) == len(cases)


@pytest.mark.parametrize(
    "case",
    [
        {"verification": "engine_generated"},
        {"verification": "engine_generated", "source": _SOURCE},
        {"verification": "source_linked", "source": _SOURCE},
        {"verification": "verified", "source": _SOURCE},
    ],
)
def test_valid_cases_are_accepted(case: dict[str, object]) -> None:
    """Consistent status and source pass validation."""
    assert verification_errors(case) == []


@pytest.mark.parametrize(
    ("case", "fragment"),
    [
        ({}, "missing 'verification'"),
        ({"source": _SOURCE}, "missing 'verification'"),
        ({"verification": "unverified"}, "unknown verification"),
        ({"verification": "source_linked"}, "requires a non-empty 'source'"),
        (
            {"verification": "source_linked", "source": {}},
            "requires a non-empty 'source'",
        ),
        ({"verification": "verified"}, "requires a non-empty 'source'"),
        (
            {"verification": "source_linked", "source": "CCNL Art. 1"},
            "'source' must be an object",
        ),
    ],
)
def test_invalid_cases_are_rejected(case: dict[str, object], fragment: str) -> None:
    """Missing, unknown, or unsupported statuses are rejected."""
    errors = verification_errors(case)
    assert len(errors) == 1
    assert fragment in errors[0]


def test_load_case_rejects_non_object(tmp_path: Path) -> None:
    """A case file must hold a JSON object."""
    path = tmp_path / "case.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(TypeError, match="must be a JSON object"):
        load_case(path)


def test_count_by_status_reports_zero_for_missing_buckets() -> None:
    """Statuses with no cases still appear with a zero count."""
    counts = count_by_status([{"verification": "engine_generated"}])
    assert counts == {"verified": 0, "source_linked": 0, "engine_generated": 1}


def test_scenario_cases_are_valid_json() -> None:
    """Every scenario case JSON is parseable and not empty."""
    case_files = sorted(_SCENARIOS_DIR.glob("*.json"))
    assert case_files, "fixtures/expected/scenarios/ must hold at least one case"
    for path in case_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data, f"{path.name} is empty"
