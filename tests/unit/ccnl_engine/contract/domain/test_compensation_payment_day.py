"""The CCNL payment day of an extra month: a calendar day with a source."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.compensation import PaymentDay

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


def test_day_reads_month_and_day() -> None:
    """A sourced day keeps its month, day and provenance."""
    day = PaymentDay.model_validate({"month": 7, "day": 1, "provenance": _LOCATED})

    assert (day.month, day.day) == (7, 1)
    assert day.provenance.location is not None


@pytest.mark.parametrize(("month", "day"), [(0, 1), (13, 1), (7, 0), (7, 29)])
def test_day_outside_every_month_fails(month: int, day: int) -> None:
    """A month outside 1-12 or a day some month lacks is rejected."""
    with pytest.raises(ValidationError):
        PaymentDay.model_validate({"month": month, "day": day, "provenance": _LOCATED})


def test_missing_provenance_is_not_stored() -> None:
    """A day without a source is left out of the data, not stored missing."""
    with pytest.raises(ValidationError, match="needs a source"):
        PaymentDay.model_validate({
            "month": 7,
            "day": 1,
            "provenance": {"status": "missing"},
        })
