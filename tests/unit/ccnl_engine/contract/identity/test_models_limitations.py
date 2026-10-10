"""Simplification notes of a CCNL: typed impact and declared limitations."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.identity.facade import CCNL, CoverageNote
from ccnl_engine.knowledge.limitation.models import MonetaryImpact
from tests.unit.ccnl_engine.builders import make_ccnl_dict

_SPEC: dict[str, Any] = {
    "variant": "missing_band",
    "applies_when": {"levels": ["4"]},
    "remediation": "model the band",
}


def _note(**fields: Any) -> dict[str, Any]:  # noqa: ANN401
    return {"kind": "simplification", "text": "a band is missing"} | fields


def _ccnl(*notes: dict[str, Any]) -> CCNL:
    data = make_ccnl_dict()
    data["coverage"]["notes"] = list(notes)
    return CCNL.model_validate(data)


def test_note_limitation_becomes_a_model_limitation() -> None:
    """The note gives the id, capability, impact and summary."""
    ccnl = _ccnl(
        _note(capability="base_salary", monetary_impact="yes", limitation=_SPEC),
        _note(monetary_impact="no"),
    )
    (limitation,) = ccnl.limitations
    assert limitation.id == "test/missing_band"
    assert limitation.capability == "base_salary"
    assert limitation.monetary_impact is MonetaryImpact.YES
    assert limitation.rulesets == ("test",)
    assert limitation.summary == "a band is missing"
    assert limitation.source == "ccnl/test:coverage.notes"


@pytest.mark.parametrize(
    ("fields", "match"),
    [
        ({}, "state a monetary_impact"),
        ({"monetary_impact": "unknown"}, "must name its capability"),
        (
            {"monetary_impact": "yes", "capability": "base_salary"},
            "declare a limitation",
        ),
        ({"monetary_impact": "no", "limitation": _SPEC}, "must name its capability"),
    ],
)
def test_monetary_simplification_must_be_mapped(
    fields: dict[str, Any], match: str
) -> None:
    """No simplification that can move an amount stays free text."""
    with pytest.raises(ValidationError, match=match):
        CoverageNote.model_validate(_note(**fields))


def test_only_simplifications_carry_impact_or_limitation() -> None:
    """Other note kinds declare neither."""
    with pytest.raises(ValidationError, match="state a monetary_impact"):
        CoverageNote.model_validate({
            "kind": "info",
            "text": "x",
            "monetary_impact": "no",
        })
    with pytest.raises(ValidationError, match="only a 'simplification'"):
        CoverageNote.model_validate({
            "kind": "info",
            "text": "x",
            "capability": "base_salary",
            "limitation": _SPEC,
        })


def test_variants_are_unique_within_a_ccnl() -> None:
    """Two notes of a CCNL cannot declare the same limitation id."""
    note = _note(capability="base_salary", monetary_impact="yes", limitation=_SPEC)
    with pytest.raises(ValidationError, match="declared twice"):
        _ccnl(note, note)


def test_limitation_levels_exist() -> None:
    """A limitation scoped to levels names levels of the CCNL."""
    spec = _SPEC | {"applies_when": {"levels": ["9"]}}
    with pytest.raises(ValidationError, match=r"unknown levels \['9'\]"):
        _ccnl(_note(capability="base_salary", monetary_impact="yes", limitation=spec))
