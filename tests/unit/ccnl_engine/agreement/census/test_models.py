"""Census models: one requirement record per institute and variant."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.census.models import Census, CensusOrigin, Requirement

_SOURCE = {"document_id": "ccnl-2024", "section": "art. 175"}


def _row(**fields: object) -> dict[str, Any]:
    return {
        "id": "sickness_net_basis",
        "institute": "sickness",
        "variant": "all",
        "source": _SOURCE,
        "state": "implemented",
        **fields,
    }


def test_a_row_read_from_the_text_loads() -> None:
    """A text row with its source, state and scenarios is valid."""
    row = Requirement.model_validate(_row(scenarios=["tests/x.py::test_y"]))

    assert row.origin is CensusOrigin.TEXT
    assert row.links.limitations == ()


@pytest.mark.parametrize(
    ("fields", "match"),
    [
        ({"source": None}, "names its source"),
        (
            {
                "state": "not_applicable",
                "source": None,
                "origin": "seeded",
                "remediation": "Read the clause.",
            },
            "needs a source",
        ),
        ({"state": "absent"}, "states its remediation"),
        ({"state": "unverified", "remediation": "  "}, "states its remediation"),
        ({"variant": "All"}, "should match pattern"),
        ({"state": "maybe"}, "Input should be"),
    ],
)
def test_a_malformed_row_is_rejected(fields: dict[str, object], match: str) -> None:
    """Text rows cite a clause, open rows their remediation, ids are snake case."""
    with pytest.raises(ValidationError, match=match):
        Requirement.model_validate(_row(**fields))


def test_a_seeded_open_row_needs_no_source() -> None:
    """A row carried over from a limitation waits for the reading of the text."""
    row = Requirement.model_validate(
        _row(
            source=None,
            origin="seeded",
            state="absent",
            remediation="Model the net daily pay.",
        )
    )

    assert row.remediation == "Model the net daily pay."
    assert row.open


def test_the_rows_of_a_census_are_sorted_and_unique() -> None:
    """Two rows with one id, or out of order, are rejected."""
    first, second = _row(id="a"), _row(id="b")
    Census.model_validate({
        "schema_version": 1,
        "ccnl_id": "x",
        "requirements": [first, second],
    })

    with pytest.raises(ValidationError, match="sorted and unique"):
        Census.model_validate({
            "schema_version": 1,
            "ccnl_id": "x",
            "requirements": [second, first],
        })
