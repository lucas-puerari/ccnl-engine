"""The rules of a replay: full, partial and not replayable, on synthetic records."""

from __future__ import annotations

import json
from datetime import date
from typing import TYPE_CHECKING

import pytest

from scripts.provenance.reference_case.check import AXES
from scripts.provenance.replay.check import credited_records, replay_errors

if TYPE_CHECKING:
    from pathlib import Path

_TODAY = date(2026, 10, 16)
_KEY_OF = {
    "base_salary": "base_salary",
    "gross": "period_gross",
    "employee_contributions": "employee_contributions",
    "employer_contributions": "employer_contributions",
    "tax": "period_tax",
    "net": "period_net",
    "tfr": "tfr_accrual",
    "employer_cost": "employer_cost",
}
_PERIMETER = {"perimeter": "INPS, TFR and the gross; no INAIL, no IRAP"}


def _spec(key: str) -> dict[str, str]:
    spec = {"printed": f"totals.{key}", "value": "100.00", "tolerance": "0.00"}
    return spec | (_PERIMETER if key in {"employer_cost", "tfr_accrual"} else {})


_INPUTS = {
    "ccnl_slug": "x.json",
    "level_code": "1",
    "year": 2026,
    "month": 3,
    "headcount": 20,
    "contract_type": "permanent",
    "hired_on": "2026-01-01",
}
_FULL_EXPECTED = {key: _spec(key) for key in _KEY_OF.values()}
_FULL: dict[str, object] = {
    "replayability": "full",
    "reason": "Every fact of the payslip has a field in the request.",
    "inputs": _INPUTS,
    "unknown_inputs": [],
    "expected": _FULL_EXPECTED,
    "known_differences": [],
}
_PARTIAL: dict[str, object] = {
    "replayability": "partial",
    "reason": "The superminimo has no field.",
    "inputs": _INPUTS,
    "unknown_inputs": [{"input": "superminimo", "affects": ["gross", "net"]}],
    "expected": {"base_salary": _spec("base_salary")},
    "known_differences": [],
}
_NOT_REPLAYABLE: dict[str, object] = {
    "replayability": "not_replayable",
    "reason": "A period before the tax years of the bundle.",
}


@pytest.mark.parametrize("replay", [_FULL, _PARTIAL, _NOT_REPLAYABLE])
def test_a_valid_replay_passes(replay: dict[str, object]) -> None:
    """A full, a partial and a not replayable record follow the rules."""
    assert replay_errors(replay, _TODAY) == []


def test_an_unknown_input_forbids_the_values_it_affects() -> None:
    """A partial replay cannot credit a total an unknown fact can move."""
    replay = _PARTIAL | {
        "expected": {"base_salary": _spec("base_salary"), "period_net": _spec("x")}
    }

    assert replay_errors(replay, _TODAY) == [
        (
            "expected value 'period_net' reads 'net', which the unknown input "
            "'superminimo' affects"
        )
    ]


def test_a_full_replay_compares_every_total_of_its_perimeter() -> None:
    """A missing total fails, unless the record puts it outside its perimeter."""
    expected = {k: v for k, v in _FULL_EXPECTED.items() if k != "tfr_accrual"}
    replay = _FULL | {"expected": expected}

    assert replay_errors(replay, _TODAY) == [
        "a full replay compares 'tfr' or puts it outside its perimeter"
    ]
    outside = {"outside_perimeter": {"tfr": "the TFS is paid by INPS"}}
    assert replay_errors(replay | outside, _TODAY) == []


def test_a_full_replay_has_no_unknown_input_and_a_partial_one_names_them() -> None:
    """Replayability and unknown inputs agree."""
    unknown = {"unknown_inputs": [{"input": "x", "affects": ["tfr_rate"]}]}

    assert replay_errors(_FULL | unknown, _TODAY) == [
        "a full replay has no 'unknown_inputs'",
        "unknown input 'x' affects unknown label 'tfr_rate'",
    ]
    assert replay_errors(_PARTIAL | {"unknown_inputs": []}, _TODAY) == [
        "a partial replay names its 'unknown_inputs'"
    ]
    assert replay_errors(_PARTIAL | {"unknown_inputs": ["superminimo"]}, _TODAY) == [
        "each unknown input states its 'input' and what it 'affects'"
    ]


@pytest.mark.parametrize(
    ("expected", "error"),
    [
        (
            {"payslip_total": _spec("x")},
            "expected value 'payslip_total' belongs to no axis or element",
        ),
        (
            {"hourly_percentages": _spec("x")},
            "expected value 'hourly_percentages' has no reader in the replay",
        ),
        (
            {"employer_cost": _spec("x")},
            "expected value 'employer_cost' must state its 'perimeter'",
        ),
        (
            {"base_salary": {"value": "1", "tolerance": "0"}},
            "expected value 'base_salary' lacks printed",
        ),
    ],
)
def test_an_expected_value_without_reader_axis_or_field_fails(
    expected: dict[str, object], error: str
) -> None:
    """Each expected value has a reader, an axis, its fields and its scope."""
    assert error in replay_errors(_PARTIAL | {"expected": expected}, _TODAY)


def test_only_the_facts_of_the_api_build_the_request() -> None:
    """A generic override would make the replay circular."""
    inputs = _INPUTS | {"period_net": "100.00", "contract_type": "apprentice"}

    assert replay_errors(_PARTIAL | {"inputs": inputs}, _TODAY) == [
        "unknown input 'period_net'",
        "'contract_type' must be one of ['permanent', 'fixed_term']",
    ]


def test_an_accepted_difference_needs_an_owner_and_expires() -> None:
    """A known difference states its reason and owner, until a date not past."""
    known = {"key": "base_salary", "reason": "r", "owner": "maintainer"}
    expired = known | {"accepted_until": "2026-10-15"}

    assert replay_errors(_PARTIAL | {"known_differences": [expired]}, _TODAY) == [
        "known difference 'base_salary' is expired or has no 'accepted_until'"
    ]
    assert replay_errors(
        _PARTIAL | {"known_differences": [{"key": "period_net"}]}, _TODAY
    ) == ["known difference 'period_net' is no expected value"]


def test_a_not_replayable_record_states_only_why() -> None:
    """Nothing it states could be credited."""
    assert replay_errors(_NOT_REPLAYABLE | {"inputs": _INPUTS}, _TODAY) == [
        "a not_replayable record states no 'inputs'"
    ]
    assert replay_errors({"replayability": "maybe"}, _TODAY) == [
        "'replayability' must be one of ['full', 'partial', 'not_replayable']"
    ]


def test_only_valid_replayable_records_are_credited(tmp_path: Path) -> None:
    """An invalid or a not replayable record credits nothing."""
    records = {
        "a": _FULL,
        "b": _PARTIAL | {"unknown_inputs": []},
        "c": _NOT_REPLAYABLE,
    }
    for pid, replay in records.items():
        (tmp_path / f"{pid}.json").write_text(
            json.dumps({"id": pid, "replay": replay}), encoding="utf-8"
        )

    assert list(credited_records(_TODAY, tmp_path)) == ["a"]
    assert len(AXES) == len(_KEY_OF)


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"run_kind": "adjustment"}, "'run_kind' must be one of"),
        ({"seniority_months": 12}, "'seniority_months' and 'seniority_as_of'"),
        ({"hired_on": "March 2024"}, "'hired_on' must be an ISO date"),
        (
            {"current_year_employment_only_on": "2026"},
            "'current_year_employment_only_on' must be an ISO date",
        ),
        ({"pension_fund": {"fund_code": "cometa"}}, "'pension_fund' is \"none\""),
    ],
)
def test_typed_inputs_are_checked(changes: dict[str, object], error: str) -> None:
    """Run kind, seniority, dates and the pension fund are stated in shape."""
    errors = replay_errors(_PARTIAL | {"inputs": _INPUTS | changes}, _TODAY)

    assert len(errors) == 1
    assert error in errors[0]


def test_a_complete_set_of_typed_inputs_passes() -> None:
    """Seniority with its date, a pension fund and the year facts are valid."""
    inputs = _INPUTS | {
        "run_kind": "thirteenth",
        "seniority_months": 33,
        "seniority_as_of": "2026-12-01",
        "pension_fund": {
            "fund_code": "cometa",
            "employee_rate": "0.012",
            "tfr_to_fund": False,
        },
        "current_year_employment_only_on": "2026-12-01",
    }

    assert replay_errors(_PARTIAL | {"inputs": inputs}, _TODAY) == []
    assert (
        replay_errors(_PARTIAL | {"inputs": _INPUTS | {"pension_fund": "none"}}, _TODAY)
        == []
    )
