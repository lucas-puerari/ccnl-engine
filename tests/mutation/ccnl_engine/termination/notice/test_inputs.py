"""The act that ends the employment and who owes the notice."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.termination.notice.inputs import NoticeIndemnityEvent, employer_owes

_DAY = date(2026, 3, 10)


@pytest.mark.parametrize(
    ("cause", "just", "owes"),
    [
        ("dismissal", False, True),
        ("dismissal", True, False),
        ("dismissal", None, False),
        ("resignation", False, False),
        ("resignation", True, True),
        ("death", None, True),
        ("mutual_agreement", None, False),
    ],
)
def test_who_owes_the_notice(cause: str, just: bool | None, owes: bool) -> None:
    """Artt. 2118-2119 c.c."""
    assert employer_owes(TerminationCause(cause), just) is owes


def test_the_act_is_dated() -> None:
    """The day of the act dates the event; it is a date."""
    assert NoticeIndemnityEvent(_DAY).event_date == _DAY
    with pytest.raises(InvalidInputError) as error:
        NoticeIndemnityEvent("2026-03-10")  # type: ignore[arg-type]

    assert (error.value.field, error.value.feature) == (
        "NoticeIndemnityEvent.received_on",
        "termination_notice",
    )
