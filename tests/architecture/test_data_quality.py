"""Validate provenance of the payable rules and of the expected-value fixtures.

Every payable rule of the bundled knowledge data carries a provenance record
with a known status; the inventory lives in :mod:`scripts.ci.payable_rules`,
shared with ``scripts/ci/check_provenance.py``.

The JSON files in ``tests/fixtures/expected/`` each declare a known
``verification`` status consistent with their ``source`` block, and carry the
inputs and expected values that
``tests/acceptance/public_api/test_reference_cases.py`` executes. The rules
live in :mod:`tests.architecture._provenance`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.ci.payable_rules import (
    STATUSES,
    ccnl_rules,
    count_by_status,
    fiscal_rules,
    inventory,
    rule_errors,
)
from tests.architecture._provenance import (
    CASES_DIR,
    load_case,
    verification_errors,
)
from tests.architecture._provenance import count_by_status as count_cases

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
    assert sum(count_cases(cases).values()) == len(cases)


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
    counts = count_cases([{"verification": "source_linked"}])
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


_RULES = inventory()
_RECORD = {"status": "derived", "location": {"section": "Art. 1"}}


def test_every_payable_rule_has_a_provenance_record() -> None:
    """No bundled payable rule lacks a record or has an unknown status."""
    assert _RULES
    assert rule_errors(_RULES) == []


def test_payable_statuses_cover_every_rule() -> None:
    """Every rule falls into exactly one known status bucket."""
    counts = count_by_status(_RULES)
    assert counts["none"] == 0
    assert sum(counts[status] for status in STATUSES) == len(_RULES)


def test_nothing_is_verified_without_a_named_reviewer() -> None:
    """The bundle records no reviewer, so no payable rule is verified."""
    assert count_by_status(_RULES)["verified"] == 0


def test_salary_period_without_provenance_fails() -> None:
    """A salary period without its own record or a level record fails."""
    ccnl = {
        "levels": [
            {
                "code": "Q",
                "base_salary": {
                    "periods": [{"valid_from": "2026-01-01", "value": "1"}]
                },
            }
        ]
    }
    (error,) = rule_errors(tuple(ccnl_rules("ccnl/data/x.json", ccnl)))
    assert error.endswith("levels[Q].base_salary[2026-01-01]: no provenance record")


def test_level_record_covers_its_periods_and_allowances() -> None:
    """A period or an allowance without a record inherits the level's."""
    ccnl = {
        "levels": [
            {
                "code": "1",
                "provenance": _RECORD,
                "base_salary": {
                    "periods": [{"valid_from": "2026-01-01", "value": "1"}]
                },
                "fixed_allowances": [{"code": "edr"}],
            }
        ],
        "parameters": {
            "seniority_increments": {"provenance": _RECORD},
            "additional_months": {
                "periods": [
                    {"valid_from": "2025-01-01", "gap_kind": "missing"},
                    {"valid_from": "2026-01-01", "value": "13", "provenance": _RECORD},
                ]
            },
            "accrual_rule": {"provenance": _RECORD},
        },
    }
    rules = tuple(ccnl_rules("ccnl/data/x.json", ccnl))
    assert [rule.status for rule in rules] == ["derived"] * 5
    assert rule_errors(rules) == []


@pytest.mark.parametrize(
    ("file", "data", "fragment"),
    [
        ("tax/data/2026-x.json", {"tfr": {"accrual_divisor": "13.5"}}, "tfr"),
        ("tax/data/2026-x.json", {"irpef_brackets": []}, "irpef_brackets"),
        ("inps/data/2026-x.json", {"inps": {"provenance": None}}, "inps"),
        ("surtax/data/regionale-2026.json", {"rates": {}}, "rates"),
        ("tax/data/variable-pay-rules.json", {"pdr": {}}, "pdr"),
        (
            "tax/data/variable-pay-rules.json",
            {"rinnovo": {"source_status": "derived"}},
            "rinnovo",
        ),
    ],
)
def test_fiscal_block_without_provenance_fails(
    file: str, data: dict[str, object], fragment: str
) -> None:
    """A fiscal block, a table or a regime without a record fails."""
    (error,) = rule_errors(tuple(fiscal_rules(file, data)))
    assert f": {fragment}: no provenance record" in error


def test_missing_status_is_allowed_but_unknown_status_fails() -> None:
    """``missing`` is a valid status; any other string is rejected."""
    data = {
        "tfr": {"provenance": {"status": "missing"}},
        "fixed_term_additional_rate": "0.014",
        "fixed_term_additional_rate_provenance": {"status": "unknown"},
    }
    rules = tuple(fiscal_rules("tax/data/2026-x.json", data))
    assert [rule.status for rule in rules] == ["unknown", "missing"]
    (error,) = rule_errors(rules)
    assert "unknown status 'unknown'" in error
