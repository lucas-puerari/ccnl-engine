"""The IVS massimale eligibility is derived from the contribution history.

L. 335/1995 art. 2 c. 18: the massimale applies to workers without
contributions before 1 January 1996 and to those who opted for the
contributory system under art. 1 c. 23.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.contribution.inputs_eligibility import (
    ContributionHistory,
    IvsCeilingBasis,
)


@pytest.mark.parametrize(
    ("history", "basis", "applies"),
    [
        pytest.param(
            ContributionHistory(first_enrolled_on=date(1995, 12, 31)),
            IvsCeilingBasis.ENROLLED_BEFORE_1996,
            False,
            id="last-day-of-1995",
        ),
        pytest.param(
            ContributionHistory(first_enrolled_on=date(1996, 1, 1)),
            IvsCeilingBasis.FIRST_ENROLMENT_AFTER_1995,
            True,
            id="first-day-of-1996",
        ),
        pytest.param(
            ContributionHistory(first_enrolled_on=date(2010, 5, 3)),
            IvsCeilingBasis.FIRST_ENROLMENT_AFTER_1995,
            True,
            id="post-1995",
        ),
        pytest.param(
            ContributionHistory(
                first_enrolled_on=date(1988, 9, 1), contributory_option=True
            ),
            IvsCeilingBasis.CONTRIBUTORY_OPTION,
            True,
            id="pre-1996-opted-in",
        ),
    ],
)
def test_basis_and_applicability(
    history: ContributionHistory, basis: IvsCeilingBasis, applies: bool
) -> None:
    """The first enrolment date and the option decide the massimale."""
    assert history.ivs_ceiling_basis is basis
    assert history.ivs_ceiling_applies is applies


def test_option_defaults_to_false() -> None:
    """Only the first enrolment date is required."""
    history = ContributionHistory(first_enrolled_on=date(2001, 9, 1))
    assert history.contributory_option is False


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({"first_enrolled_on": "1996-01-01"}, id="raw-date"),
        pytest.param(
            {"first_enrolled_on": date(1996, 1, 1), "contributory_option": "yes"},
            id="raw-option",
        ),
    ],
)
def test_rejects_values_of_the_wrong_type(kwargs: dict[str, object]) -> None:
    """A raw value in place of a date or a bool fails at construction."""
    with pytest.raises(InvalidInputError, match="must be") as raised:
        ContributionHistory(**kwargs)  # type: ignore[arg-type]
    assert raised.value.feature == "contribution_history"
