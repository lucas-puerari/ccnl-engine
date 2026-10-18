"""The elemento perequativo clause: a sourced, positive yearly amount."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.compensation.models import PerequativoElement

_LOCATED: dict[str, Any] = {
    "status": "derived",
    "location": {
        "source_document": {
            "document_id": "ccnl-x",
            "title": "CCNL X",
            "kind": "associazione",
        },
        "section": "Art. 13",
    },
}


def _clause(**changes: object) -> dict[str, Any]:
    clause: dict[str, Any] = {
        "annual_amount": {
            "periods": [
                {"valid_from": "2014-01-01", "valid_until": None, "value": "485.00"}
            ]
        },
        "payment_month": 6,
        "month_rule": {
            "min_days": 15,
            "comparison": "more_than",
            "provenance": _LOCATED,
        },
        "tfr_relevant": False,
        "provenance": _LOCATED,
    }
    clause.update(changes)
    return clause


def test_clause_reads_amount_month_and_rule() -> None:
    """A sourced clause keeps its amount, payment month and month rule."""
    clause = PerequativoElement.model_validate(_clause())

    assert clause.payment_month == 6
    assert clause.month_rule.min_days == 15
    assert clause.tfr_relevant is False


@pytest.mark.parametrize("month", [0, 13])
def test_payment_month_outside_the_year_fails(month: int) -> None:
    """A payment month outside 1-12 is rejected."""
    with pytest.raises(ValidationError):
        PerequativoElement.model_validate(_clause(payment_month=month))


def test_tfr_relevance_is_required() -> None:
    """Whether it enters the TFR base is stated, never defaulted."""
    clause = _clause()
    del clause["tfr_relevant"]
    with pytest.raises(ValidationError, match="tfr_relevant"):
        PerequativoElement.model_validate(clause)


def test_missing_provenance_is_not_stored() -> None:
    """A clause without a source is left out of the data."""
    with pytest.raises(ValidationError, match="needs a source"):
        PerequativoElement.model_validate(_clause(provenance={"status": "missing"}))


def test_non_positive_amount_fails() -> None:
    """A zero yearly amount is a data-entry error."""
    zero = {
        "periods": [{"valid_from": "2014-01-01", "valid_until": None, "value": "0"}]
    }
    with pytest.raises(ValidationError, match="must be > 0"):
        PerequativoElement.model_validate(_clause(annual_amount=zero))


def test_month_rule_changing_over_time_fails() -> None:
    """The month rule holds for every year: no valid_from or previous."""
    rule = {
        "min_days": 15,
        "comparison": "more_than",
        "provenance": _LOCATED,
        "valid_from": "2020-01-01",
    }
    with pytest.raises(ValidationError, match="cannot change over time"):
        PerequativoElement.model_validate(_clause(month_rule=rule))
