"""The validation packet: one certified comparison per output."""

from __future__ import annotations

import copy
import json
from typing import TYPE_CHECKING, Any

import pytest

from scripts.provenance.validation_packet.check import (
    check_all,
    coverage,
    main,
    packet_errors,
)

if TYPE_CHECKING:
    from pathlib import Path

_PACKET: dict[str, Any] = {
    "artifact": {
        "id": "provider-x-2026-03",
        "kind": "provider_output",
        "sha256": "a" * 64,
    },
    "provenance": {
        "source": "Payroll provider X, run of March 2026",
        "obtained_on": "2026-04-02",
        "independence": "Computed by the provider from the input packet alone.",
        "anonymisation": "No name, tax code or address: the case is synthetic.",
        "retention": "Kept under the agreement with the provider.",
    },
    "inputs": {
        "scenario": "ordinary_month",
        "ccnl_id": "commercio-confcommercio",
        "level_code": "4",
        "year": 2026,
        "month": 3,
        "headcount": 20,
        "contract_type": "permanent",
        "comune_belfiore": "F205",
    },
    "outputs": [
        {
            "output": "net",
            "value": "1543.21",
            "perimeter": "Net pay of the month, before advances",
            "tolerance": "0.01",
            "rounding": "half_up_cents",
            "result": "match",
        },
        {
            "output": "employer_cost",
            "value": "2711.00",
            "perimeter": "Gross, employer INPS and INAIL, TFR accrual",
            "tolerance": "0.01",
            "rounding": "half_up_cents",
            "result": "engine_bug",
            "explanation": "INAIL rate of the wrong class; fixed in the engine.",
        },
    ],
    "review": {
        "reviewer": "claude-opus-5-5",
        "date": "2026-04-03",
        "owner": "maintainer",
        "review_by": "2027-04-03",
    },
    "versions": {"engine": "0.6.0", "bundle": "2026.10", "provider": "X 12.4"},
}


def _packet(**changes: object) -> dict[str, Any]:
    packet = copy.deepcopy(_PACKET)
    for path, value in changes.items():
        section, _, key = path.partition("__")
        if key:
            packet[section][key] = value
        else:
            packet[section] = value
    return packet


def test_a_complete_packet_is_valid() -> None:
    """Every section of the protocol is present and well formed."""
    assert packet_errors(_PACKET) == []


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"review": None}, ["review missing"]),
        ({"artifact__kind": "screenshot"}, ["artifact.kind 'screenshot' unknown"]),
        ({"artifact__sha256": "abc"}, ["artifact.sha256 is not a SHA-256"]),
        ({"provenance__retention": ""}, ["provenance.retention missing"]),
        (
            {"provenance__obtained_on": "April"},
            ["provenance.obtained_on is not a date"],
        ),
        ({"inputs__scenario": "bonus"}, ["inputs.scenario 'bonus' unknown"]),
        (
            {"inputs__run_kind": "bonus"},
            [
                (
                    "inputs: 'run_kind' must be one of "
                    "['regular', 'thirteenth', 'fourteenth']"
                )
            ],
        ),
        (
            {"review__review_by": "2026-04-03"},
            ["review.review_by is not a date after review.date"],
        ),
        (
            {"review__date": None},
            [
                "review.date is not a date",
            ],
        ),
        ({"versions__provider": ""}, ["versions.provider missing"]),
        ({"outputs": []}, ["outputs is empty"]),
    ],
)
def test_each_missing_field_is_reported(
    changes: dict[str, Any], expected: list[str]
) -> None:
    """A packet missing a field of the protocol says which."""
    assert packet_errors(_packet(**changes)) == expected


def test_the_inputs_are_the_facts_of_a_replay() -> None:
    """A missing or unknown fact is reported with the keys of a replay."""
    packet = _packet()
    del packet["inputs"]["headcount"]
    packet["inputs"]["salary"] = "1000"

    assert packet_errors(packet) == [
        "inputs: unknown input 'salary'",
        "inputs: missing input 'headcount'",
    ]


def test_each_output_is_judged_on_its_own() -> None:
    """A rate is no total; amounts carry cents; a bug needs an explanation."""
    outputs = [
        {
            "output": "employee_inps_rate",
            "value": "9.19",
            "tolerance": "0.00",
            "perimeter": "rate",
            "rounding": "half_up_cents",
            "result": "match",
        },
        {
            "output": "net",
            "value": "1543",
            "tolerance": "0.01",
            "perimeter": "",
            "rounding": "ceil",
            "result": "artifact_error",
        },
        {
            "output": "net",
            "value": "1.00",
            "tolerance": "0.01",
            "perimeter": "Net",
            "rounding": "whole_euro",
            "result": "maybe",
        },
    ]

    assert packet_errors(_packet(outputs=outputs)) == [
        "outputs: net compared twice",
        "outputs[0].output 'employee_inps_rate' is not a total",
        "outputs[1].value is not an amount with cents",
        "outputs[1].perimeter missing",
        "outputs[1].rounding 'ceil' unknown",
        "outputs[1]: artifact_error without explanation",
        "outputs[2].result 'maybe' unknown",
    ]


def test_a_packet_that_is_no_object_fails() -> None:
    """A list or a string is no packet."""
    assert packet_errors([]) == ["not a JSON object"]


def test_only_independent_matched_outputs_are_covered(tmp_path: Path) -> None:
    """A bug covers nothing; a provisional engine output covers nothing.

    An invalid packet covers nothing either, and its errors are listed.
    """
    provisional = _packet(artifact__kind="engine_provisional", artifact__sha256=None)
    provisional["versions"].pop("provider")
    oracle = _packet(artifact__kind="hand_oracle")
    oracle["inputs"]["ccnl_id"] = "metalmeccanico-federmeccanica"
    broken = _packet(review=None)
    for name, packet in {
        "a": _PACKET,
        "b": provisional,
        "c": oracle,
        "d": broken,
        "e": [1],
    }.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(packet), encoding="utf-8")

    assert coverage(tmp_path) == {
        ("commercio-confcommercio", "net", "provider output"),
        ("metalmeccanico-federmeccanica", "net", "hand oracle"),
    }
    assert check_all(tmp_path) == [
        "d.json: review missing",
        "e.json: not a JSON object",
    ]


def test_the_repository_packets_are_valid(capsys: pytest.CaptureFixture[str]) -> None:
    """The script checks every packet of the repository."""
    assert main() == 0
    assert "Validation packets checked:" in capsys.readouterr().out
