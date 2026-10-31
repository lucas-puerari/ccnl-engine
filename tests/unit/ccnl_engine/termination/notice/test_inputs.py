"""The act that ends the employment: its checks and who owes the notice."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.termination.notice.inputs import NoticeIndemnityEvent
from ccnl_engine.termination.notice.models import TerminationCause

_DAY = date(2026, 3, 10)


@pytest.mark.parametrize(
    ("cause", "just", "owes"),
    [
        ("dismissal", False, True),
        ("dismissal", True, False),
        ("resignation", False, False),
        ("resignation", True, True),
        ("death", False, True),
        ("mutual_agreement", False, False),
    ],
)
def test_who_owes_the_notice(cause: str, just: bool, owes: bool) -> None:
    """Artt. 2118-2119 c.c.; the cause is read from its value."""
    event = NoticeIndemnityEvent(_DAY, cause, just_cause=just)  # type: ignore[arg-type]

    assert (event.cause, event.event_date, event.employer_owes) == (
        TerminationCause(cause),
        _DAY,
        owes,
    )


@pytest.mark.parametrize(
    ("received", "cause", "just", "field"),
    [
        ("2026-03-10", "dismissal", False, "NoticeIndemnityEvent.received_on"),
        (_DAY, "retirement", False, "NoticeIndemnityEvent.cause"),
        (_DAY, "dismissal", None, "NoticeIndemnityEvent.just_cause"),
    ],
)
def test_wrong_acts_are_rejected(
    received: object, cause: str, just: object, field: str
) -> None:
    """A date, a cause of the list, a just cause stated."""
    with pytest.raises(InvalidInputError) as error:
        NoticeIndemnityEvent(received, cause, just_cause=just)  # type: ignore[arg-type]

    assert (error.value.field, error.value.feature) == (field, "termination_notice")
