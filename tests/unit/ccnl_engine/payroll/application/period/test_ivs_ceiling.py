"""When the IVS massimale eligibility matters, and what a missing history does.

Massimale 2026: 122,295.00 EUR.  Below or at it the capped and uncapped
branches give the same contributions, so a missing history is irrelevant;
one cent beyond it, the history decides the contributions.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.period._ivs_ceiling import (
    IvsCeiling,
    resolve_ivs_ceiling,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from tests.helpers import make_domestic_year_rules, make_year_rules

_CEILING = Decimal("122295.00")
_YTD = Decimal("120000.00")
_POST_1995 = ContributionHistory(first_enrolled_on=date(2001, 9, 1))
_PRE_1996 = ContributionHistory(first_enrolled_on=date(1990, 3, 1))
_OPTED_IN = ContributionHistory(
    first_enrolled_on=date(1990, 3, 1), contributory_option=True
)


def _ivs(period: str, history: ContributionHistory | None = None) -> IvsCeiling:
    return IvsCeiling(
        ceiling=_CEILING,
        ytd_base=_YTD,
        period_base=Decimal(period),
        history=history,
        source=None,
    )


@pytest.mark.parametrize(
    ("period", "reached"),
    [
        pytest.param("2294.99", False, id="one-cent-below"),
        pytest.param("2295.00", False, id="at-the-massimale"),
        pytest.param("2295.01", True, id="one-cent-above"),
    ],
)
def test_missing_history_matters_only_beyond_the_massimale(
    period: str, *, reached: bool
) -> None:
    """120,000 + period against 122,295: only beyond it is a fact missing."""
    ivs = _ivs(period)
    assert ivs.reached is reached
    assert ivs.undetermined is reached
    assert ivs.applies is False
    if reached:
        assert ivs.reason == "required_fact_missing"
        assert ivs.status is CalculationStatus.PROVISIONAL
    else:
        assert ivs.reason == "ceiling_not_reached"
        assert ivs.status is CalculationStatus.FINAL
        assert ivs.issue() is None


def test_missing_history_beyond_the_massimale_names_the_fact() -> None:
    """The issue is incomplete and names the public field to supply."""
    issue = _ivs("2295.01").issue()
    assert issue is not None
    assert issue.code == "ivs_ceiling_eligibility_unknown"
    assert issue.fact == "contribution_history"
    assert issue.status is CalculationStatus.INCOMPLETE


def test_ytd_already_beyond_the_massimale_needs_the_history() -> None:
    """YTD 125,000 is past 122,295: any positive base of the run matters."""
    ivs = IvsCeiling(
        ceiling=_CEILING,
        ytd_base=Decimal("125000.00"),
        period_base=Decimal("0.01"),
        history=None,
        source=None,
    )
    assert ivs.undetermined is True


@pytest.mark.parametrize(
    ("history", "applies", "reason"),
    [
        pytest.param(_PRE_1996, False, "enrolled_before_1996", id="pre-1996"),
        pytest.param(_POST_1995, True, "first_enrolment_after_1995", id="post-1995"),
        pytest.param(_OPTED_IN, True, "contributory_option", id="opt-in"),
    ],
)
def test_known_history_decides_beyond_the_massimale(
    history: ContributionHistory, *, applies: bool, reason: str
) -> None:
    """With the history the decision is final whatever the base."""
    ivs = _ivs("2295.01", history)
    assert ivs.applies is applies
    assert ivs.reason == reason
    assert ivs.status is CalculationStatus.FINAL
    assert ivs.issue() is None


def test_rules_without_massimale_have_no_eligibility() -> None:
    """Domestic rules carry no INPS block; a sector may carry no massimale."""
    no_ceiling = make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employee_ivs_rate": "0.0919",
            "employer_rate": "0.2381",
            "employer_ivs_rate": "0.2381",
            "ceiling": None,
        }
    )
    for rules in (make_domestic_year_rules(), no_ceiling):
        assert (
            resolve_ivs_ceiling(
                rules, None, ytd_base=_YTD, period_base=Decimal("5000.00")
            )
            is None
        )


def test_rules_with_massimale_read_it_from_the_data() -> None:
    """The massimale and its source come from the INPS rules of the year."""
    rules = make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employee_ivs_rate": "0.0919",
            "employer_rate": "0.2381",
            "employer_ivs_rate": "0.2381",
            "ceiling": "122295.00",
        }
    )
    ivs = resolve_ivs_ceiling(
        rules, _POST_1995, ytd_base=_YTD, period_base=Decimal("100.00")
    )
    assert ivs is not None
    assert ivs.ceiling == _CEILING
    assert rules.inps is not None
    expected = None if rules.inps.provenance is None else rules.inps.provenance.location
    assert ivs.source == expected
