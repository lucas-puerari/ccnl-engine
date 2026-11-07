"""The leave-taken event: a bucket and a positive quantity."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.leave.inputs import LeaveTakenEvent
from ccnl_engine.leave.types import LeaveBucket


def test_bucket_is_parsed_from_its_value() -> None:
    """A bucket given by its value becomes the member."""
    event = LeaveTakenEvent(date(2026, 7, 6), "ferie", Decimal(10))  # type: ignore[arg-type]

    assert event.bucket is LeaveBucket.FERIE


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"event_date": "2026-07-06"}, "LeaveTakenEvent.event_date"),
        ({"bucket": "par"}, "LeaveTakenEvent.bucket"),
        ({"quantity": Decimal(0)}, "LeaveTakenEvent.quantity"),
        ({"quantity": 8}, "LeaveTakenEvent.quantity"),
    ],
)
def test_invalid_event_is_rejected(kwargs: dict[str, object], field: str) -> None:
    """A string date, an unknown bucket, a zero or non-decimal quantity."""
    values: dict[str, object] = {
        "event_date": date(2026, 7, 6),
        "bucket": LeaveBucket.ROL,
        "quantity": Decimal(8),
        **kwargs,
    }
    with pytest.raises(InvalidInputError) as caught:
        LeaveTakenEvent(**values)  # type: ignore[arg-type]
    assert caught.value.field == field
