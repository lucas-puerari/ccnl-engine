"""Validate provenance metadata and shape of the expected-value fixtures.

These tests run against the JSON files in ``tests/fixtures/expected/`` and
assert that each declares a known ``verification`` status consistent with its
``source`` block, and carries the inputs and expected values that
``tests/acceptance/public_api/test_reference_cases.py`` executes. The rules
live in :mod:`tests.architecture._provenance`.
"""

from __future__ import annotations

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
_INPUT_KEYS = frozenset({"ccnl_slug", "level_code", "year", "month", "headcount"})
_EXPECTED_KEYS = frozenset({"base_salary", "fixed_allowances", "period_gross"})
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
        ({"verification": "engine_generated"}, "unknown verification"),
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
    counts = count_by_status([{"verification": "source_linked"}])
    assert counts == {"verified": 0, "source_linked": 1}


@pytest.mark.parametrize("path", _ALL_CASES, ids=lambda p: p.stem)
def test_case_declares_runnable_inputs(path: Path) -> None:
    """Every case carries exactly the inputs and values the runner uses."""
    case = load_case(path)
    inputs = case.get("inputs")
    expected = case.get("expected")
    assert isinstance(inputs, dict), path.name
    assert isinstance(expected, dict), path.name
    assert set(inputs) == _INPUT_KEYS, path.name
    assert set(expected) == _EXPECTED_KEYS, path.name
