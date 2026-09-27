"""The CCNL accrual rule: threshold, comparison and a required source."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.compensation import (
    AccrualComparison,
    ExtraMonthAccrualRule,
)

_LOCATED: dict[str, Any] = {
    "status": "derived",
    "location": {
        "source_document": {
            "document_id": "ccnl-x",
            "title": "CCNL X",
            "kind": "associazione",
        },
        "section": "Art. 1",
    },
}


def test_rule_reads_threshold_and_comparison() -> None:
    """A sourced rule keeps its threshold, comparison and provenance."""
    rule = ExtraMonthAccrualRule.model_validate({
        "min_days": 15,
        "comparison": "more_than",
        "provenance": _LOCATED,
    })
    assert rule.min_days == 15
    assert rule.comparison is AccrualComparison.MORE_THAN
    assert rule.provenance.location is not None


@pytest.mark.parametrize(
    ("comparison", "min_days"),
    [("at_least", 0), ("at_least", 29), ("more_than", 28), ("more_than", -1)],
)
def test_threshold_out_of_range_fails(comparison: str, min_days: int) -> None:
    """A threshold a full month cannot pass, or below one day, is rejected."""
    with pytest.raises(ValidationError, match="min_days must be between"):
        ExtraMonthAccrualRule.model_validate({
            "min_days": min_days,
            "comparison": comparison,
            "provenance": _LOCATED,
        })


def test_missing_provenance_is_not_stored() -> None:
    """A rule without a source is left out of the data, not stored missing."""
    with pytest.raises(ValidationError, match="needs a source"):
        ExtraMonthAccrualRule.model_validate({
            "min_days": 15,
            "comparison": "at_least",
            "provenance": {"status": "missing"},
        })
