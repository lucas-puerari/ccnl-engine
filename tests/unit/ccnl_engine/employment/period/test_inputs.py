"""How an employment ends: the cause, the just cause and their checks."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.employment.period.inputs import EmploymentPeriod, TerminationCause
from ccnl_engine.errors import InvalidInputError

_START, _END = date(2020, 1, 1), date(2026, 3, 31)


def test_the_cause_is_read_from_its_value() -> None:
    """A string value of the cause is normalized."""
    period = EmploymentPeriod(_START, _END, "dismissal", True)  # type: ignore[arg-type]

    assert (period.ended_by, period.just_cause) == (TerminationCause.DISMISSAL, True)


@pytest.mark.parametrize(
    ("ended", "cause", "just", "field"),
    [
        (None, TerminationCause.DISMISSAL, None, "EmploymentPeriod.ended_by"),
        (_END, "retirement", None, "EmploymentPeriod.ended_by"),
        (_END, TerminationCause.DEATH, False, "EmploymentPeriod.just_cause"),
        (_END, None, True, "EmploymentPeriod.just_cause"),
        (_END, TerminationCause.RESIGNATION, 1, "EmploymentPeriod.just_cause"),
    ],
)
def test_a_cause_needs_an_end_and_a_just_cause_its_kind(
    ended: date | None, cause: object, just: object, field: str
) -> None:
    """The cause ends a period; just cause goes with dismissal or resignation."""
    with pytest.raises(InvalidInputError) as error:
        EmploymentPeriod(_START, ended, cause, just)  # type: ignore[arg-type]

    assert (error.value.field, error.value.feature) == (field, "employment_facts")
