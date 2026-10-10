"""IVS massimale eligibility of a real run, decided from the history.

Metalmeccanico C3, June 2026, industrial employer with 50 employees.
Sources, written by hand and not read from the engine:

- gross of the run: minimo C3 from June 2026, 2,211.43
  (``tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026``);
- employee INPS 9.49%, of which IVS 9.19% and CIGS 0.30%; employer IVS
  23.81%; 1% addizionale on the pay of the month above 4,685.00 (INPS
  circ. 6/2026 par. 5, mensilizzazione), whatever the YTD base: June is a
  regular month, not a conguaglio, and 2,211.43 is below it;
- massimale 2026: 122,295.00 (INPS, L. 335/1995 art. 2 c. 18).

Employee INPS of the full month uncapped, on the base of 2,211 (the
2,211.43 to the whole euro, INPS circ. 208/2001): IVS 2,211 x 0.0919 =
203.1909 -> 203.19; CIGS 2,211 x 0.0030 = 6.633 -> 6.63; no addizionale;
total 209.82.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CEILING = Decimal("122295.00")
_UNCAPPED_EMPLOYEE = Decimal("209.82")
#: The INPS base of the run, the June minimum to the whole euro.
_BASE = Decimal("2211.00")
_POST_1995 = ContributionHistory(first_enrolled_on=date(2001, 9, 1))
_PRE_1996 = ContributionHistory(first_enrolled_on=date(1990, 3, 1))
_OPTED_IN = ContributionHistory(
    first_enrolled_on=date(1990, 3, 1), contributory_option=True
)


def _june(ytd: Decimal, history: ContributionHistory | None) -> PeriodResult:
    opening = PeriodState(
        accrual=EmploymentAccrualState(inps_bases=(InpsBaseYtd(2026, ytd),))
    )
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 26),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=opening,
            contribution_history=history,
        )
    )


def _decision(result: PeriodResult, capability: str) -> CalculationDecision:
    (decision,) = [d for d in result.decisions if d.capability == capability]
    return decision


def _eligibility(result: PeriodResult) -> CalculationDecision:
    return _decision(result, "ivs_ceiling_eligibility")


def _missing(result: PeriodResult) -> bool:
    return any(issue.fact == "contribution_history" for issue in result.issues)


@pytest.mark.parametrize(
    ("offset", "missing"),
    [
        pytest.param("-0.01", False, id="one-cent-below"),
        pytest.param("0.00", False, id="at-the-massimale"),
        pytest.param("0.01", True, id="one-cent-above"),
    ],
)
def test_missing_history_around_the_massimale(offset: str, *, missing: bool) -> None:
    """YTD + 2,211 against 122,295.00, with no contribution history.

    The base of the run is 2,211.43 to the whole euro (INPS circ.
    208/2001).  YTD = 122,295.00 - 2,211 + offset: 120,083.99 / 84.00 /
    84.01.  Up to the massimale both branches coincide and the run is final;
    one cent beyond, the fact is missing and the INPS amounts are
    undetermined.
    """
    ytd = _CEILING - _BASE + Decimal(offset)
    result = _june(ytd, None)

    decision = _eligibility(result)
    employee = _decision(result, "inps_employee")
    assert _missing(result) is missing
    assert result.contribution_breakdown.employee == _UNCAPPED_EMPLOYEE
    if missing:
        assert decision.reason_code == "required_fact_missing"
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.inputs["ceiling_applies"] == "undetermined"
        assert employee.amount is None
        assert employee.status is CalculationStatus.INCOMPLETE
    else:
        assert decision.reason_code == "ceiling_not_reached"
        assert decision.status is CalculationStatus.FINAL
        assert employee.amount == _UNCAPPED_EMPLOYEE


def test_missing_history_beyond_the_massimale_lists_both_branches() -> None:
    """YTD 130,000 is past the massimale: the two branches differ.

    Capped: no IVS, employee CIGS 6.63 only; employer IVS 0.  Uncapped:
    employee 209.82; employer IVS 2,211 x 0.2381 = 526.4391 -> 526.44
    more than capped.
    """
    result = _june(Decimal("130000.00"), None)

    inputs = _eligibility(result).inputs
    assert inputs["employee_capped"] == Decimal("6.63")
    assert inputs["employee_uncapped"] == _UNCAPPED_EMPLOYEE
    employer_gap = Decimal(inputs["employer_uncapped"]) - Decimal(
        inputs["employer_capped"]
    )
    assert employer_gap == Decimal("526.44")
    assert _decision(result, "inps_employer").amount is None
    assert _missing(result)
    assert "inps/2026/industria" in {r.identity.id for r in result.rulesets}


@pytest.mark.parametrize(
    ("history", "reason", "employee"),
    [
        pytest.param(_PRE_1996, "enrolled_before_1996", "209.82", id="pre-1996"),
        pytest.param(_POST_1995, "first_enrolment_after_1995", "6.63", id="post-1995"),
        pytest.param(_OPTED_IN, "contributory_option", "6.63", id="opt-in"),
    ],
)
def test_known_history_decides_the_branch(
    history: ContributionHistory, reason: str, employee: str
) -> None:
    """YTD 130,000: pre-1996 pays IVS on the full base, the others do not."""
    result = _june(Decimal("130000.00"), history)

    decision = _eligibility(result)
    assert decision.reason_code == reason
    assert decision.status is CalculationStatus.FINAL
    assert decision.amount is None
    assert decision.inputs["first_enrolled_on"] == (
        history.first_enrolled_on.isoformat()
    )
    assert decision.inputs["ceiling"] == _CEILING
    assert "employee_capped" not in decision.inputs
    assert decision.rule.endswith(":inps.ceiling")
    assert decision.source is not None
    assert result.contribution_breakdown.employee == Decimal(employee)
    assert _decision(result, "inps_employee").amount == Decimal(employee)
    assert not _missing(result)


def test_ytd_beyond_the_massimale_capped_run_has_no_ivs_or_addizionale() -> None:
    """Post-1995 at YTD 130,000: only the CIGS 6.63 remains."""
    result = _june(Decimal("130000.00"), _POST_1995)

    names = {c.name: c.amount for c in result.contribution_breakdown.components}
    assert names["ivs_employee"] == Decimal(0)
    assert "addizionale_1pct" not in names
    assert names["non_ivs_employee"] == Decimal("6.63")
