"""The missing-fact issue of an unknown INPS base of other employments.

The unknown base has no upper bound: it can matter to every run whose INPS
rules carry a massimale the worker may be subject to or a 1% threshold.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.contribution.inputs_eligibility import ContributionHistory
from ccnl_engine.payroll.contribution.models_inps_base import InpsBaseYtd
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_accrual import EmploymentAccrualState
from tests.fixtures.period_requests import period_request

_CODE = "other_employment_inps_base_unknown"
#: Enrolled in 1990: the massimale does not apply, the 1% threshold does.
_BEFORE_1996 = ContributionHistory(date(1990, 3, 1))
_AFTER_1996 = ContributionHistory(date(2005, 3, 1))


def _facts(
    history: ContributionHistory | None, other_employers: Decimal | None
) -> dict[str, str | None]:
    """Return the fact each issue of January names, keyed by issue code.

    Returns:
        The issues of the run opened with ``other_employers`` stated.
    """
    opening = PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, Decimal(0), other_employers),)
        )
    )
    result = calculate_period(
        period_request(1, opening=opening, contribution_history=history)
    )
    return {issue.code: issue.fact for issue in result.issues}


@pytest.mark.parametrize(
    "history",
    [None, _BEFORE_1996, _AFTER_1996],
    ids=["history_unknown", "before_1996", "after_1996"],
)
def test_an_unknown_base_is_reported_whatever_the_history(
    history: ContributionHistory | None,
) -> None:
    """The 1% threshold applies to every history; the massimale from 1996."""
    assert _facts(history, None)[_CODE] == "other_employers"


def test_a_stated_base_is_not_reported() -> None:
    """Zero states that there is no other employment."""
    assert _CODE not in _facts(_AFTER_1996, Decimal(0))


def test_a_domestic_run_reads_no_base_of_other_employments() -> None:
    """Domestic contributions are per hour, without massimale or threshold."""
    result = calculate_period(
        period_request(
            1,
            ccnl="lavoro-domestico-non-convivente.json",
            level="B",
            weekly_hours=25,
            contributable_hours=Decimal(108),
        )
    )

    assert _CODE not in {issue.code for issue in result.issues}
