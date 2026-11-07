"""How an employment ends: the cause, the just cause and their checks."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.employment.period.inputs import (
    CollectiveDismissal,
    EmploymentPeriod,
    NaspiCase,
    TerminationCause,
)
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


@pytest.mark.parametrize(
    ("cause", "case"),
    [
        (TerminationCause.RESIGNATION, NaspiCase.PROTECTED_MATERNITY),
        (TerminationCause.MUTUAL_AGREEMENT, NaspiCase.CONCILIATION),
        (TerminationCause.MUTUAL_AGREEMENT, NaspiCase.TRANSFER),
        (TerminationCause.DISMISSAL, NaspiCase.CONTRACTOR_CHANGE),
        (TerminationCause.DISMISSAL, NaspiCase.SITE_CLOSURE),
        (TerminationCause.DEATH, NaspiCase.ORDINARY),
        (TerminationCause.DISMISSAL, CollectiveDismissal(True, False)),
    ],
)
def test_a_naspi_case_goes_with_its_cause(
    cause: TerminationCause, case: NaspiCase | CollectiveDismissal
) -> None:
    """Each case of the NASpI contribution belongs to one way of ending."""
    period = EmploymentPeriod(_START, _END, cause, naspi_case=case)

    assert period.naspi_case == case


def test_the_naspi_case_is_read_from_its_value() -> None:
    """A string value of the case is normalized."""
    period = EmploymentPeriod(
        _START,
        _END,
        TerminationCause.DISMISSAL,
        naspi_case="site_closure",  # type: ignore[arg-type]
    )

    assert period.naspi_case is NaspiCase.SITE_CLOSURE


@pytest.mark.parametrize(
    ("cause", "case"),
    [
        (TerminationCause.DISMISSAL, NaspiCase.PROTECTED_MATERNITY),
        (TerminationCause.RESIGNATION, NaspiCase.CONCILIATION),
        (TerminationCause.RESIGNATION, NaspiCase.CONTRACTOR_CHANGE),
        (TerminationCause.MUTUAL_AGREEMENT, CollectiveDismissal(False, True)),
        (None, NaspiCase.ORDINARY),
        (TerminationCause.DISMISSAL, "layoff"),
    ],
)
def test_a_naspi_case_of_another_cause_is_rejected(
    cause: TerminationCause | None, case: object
) -> None:
    """A case that does not fit the cause, or none stated, is an error."""
    with pytest.raises(InvalidInputError) as error:
        EmploymentPeriod(_START, _END, cause, naspi_case=case)  # type: ignore[arg-type]

    assert error.value.field == "EmploymentPeriod.naspi_case"


@pytest.mark.parametrize("field", ["union_agreement", "cigs_employer"])
def test_the_collective_flags_are_booleans(field: str) -> None:
    """``1`` is not a flag."""
    flags: dict[str, object] = {"union_agreement": True, "cigs_employer": True}
    flags[field] = 1
    with pytest.raises(InvalidInputError) as error:
        CollectiveDismissal(**flags)  # type: ignore[arg-type]

    assert error.value.field == f"CollectiveDismissal.{field}"


def test_probation_until_must_not_precede_the_start() -> None:
    """The probation ends on or after the first day of employment."""
    with pytest.raises(InvalidInputError, match="probation_until"):
        EmploymentPeriod(date(2026, 3, 1), probation_until=date(2026, 2, 28))
    assert EmploymentPeriod(date(2026, 3, 1), probation_until=date(2026, 3, 1))
