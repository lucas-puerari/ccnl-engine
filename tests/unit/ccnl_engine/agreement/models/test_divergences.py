"""Divergences of a review: each closed by a decision that names its test."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.agreement.metadata.review.models import Divergence, DivergenceDecision
from tests.unit.ccnl_engine.builders import make_ccnl_dict

_BASE: dict[str, Any] = {
    "subject": "employer rate 29.44% against 29.36%",
    "cause": "class not stated",
    "evidence": "DD 135/2025",
}


@pytest.mark.parametrize(
    "fields",
    [
        {"decision": "engine_bug"},
        {"decision": "external_artifact_error"},
        {"decision": "source_context_missing", "limitation": "class_unconfirmed"},
        {"decision": "accepted_external_variance", "review_by": "2027-03-31"},
    ],
)
def test_each_decision_carries_what_makes_it_testable(fields: dict[str, Any]) -> None:
    """A decision is valid with exactly the field it requires."""
    divergence = Divergence.model_validate(_BASE | fields)
    assert divergence.decision is DivergenceDecision(fields["decision"])


@pytest.mark.parametrize(
    ("fields", "match"),
    [
        ({"decision": "source_context_missing"}, "names its limitation"),
        ({"decision": "engine_bug", "limitation": "x"}, "names its limitation"),
        ({"decision": "accepted_external_variance"}, "has a review_by"),
        ({"decision": "engine_bug", "review_by": "2027-03-31"}, "has a review_by"),
        ({"decision": "still_open"}, "decision"),
    ],
)
def test_a_divergence_never_stays_open(fields: dict[str, Any], match: str) -> None:
    """No divergence without a closing decision and its required field."""
    with pytest.raises(ValidationError, match=match):
        Divergence.model_validate(_BASE | fields)


def _ccnl_with(divergence: dict[str, Any]) -> dict[str, Any]:
    data = make_ccnl_dict()
    data["verification"] = {
        "reviews": [
            {
                "id": "r1",
                "date": "2026-10-15",
                "reviewer": "claude-opus-5-5",
                "reviewer_kind": "ai",
                "scope": "cost table",
                "outcome": "flagged",
                "divergences": [divergence],
            }
        ]
    }
    return data


def test_a_blocking_divergence_names_a_declared_limitation() -> None:
    """The limitation a divergence relies on must be declared by the file."""
    data = _ccnl_with(
        _BASE | {"decision": "source_context_missing", "limitation": "undeclared"}
    )
    with pytest.raises(ValidationError, match="undeclared limitation 'undeclared'"):
        CCNL.model_validate(data)


def test_a_divergence_without_limitation_loads() -> None:
    """An engine bug needs no limitation of the file."""
    ccnl = CCNL.model_validate(_ccnl_with(_BASE | {"decision": "engine_bug"}))
    (review,) = ccnl.verification.reviews
    assert review.divergences[0].decision is DivergenceDecision.ENGINE_BUG
