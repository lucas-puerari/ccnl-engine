"""Ratei at the termination on runs computed on their own: what blocks them.

CCNL Terziario Confcommercio, Testo Unico 30 July 2019
(https://www.ebinter.it/ebinter-site/wp-content/uploads/2022/01/
CCNL-Terziario-Distribuzione-e-Servizi_30-Luglio-2019.pdf), art. 220: the
tredicesima counts the months of the calendar year, art. 221: the
quattordicesima the twelve months before 1 July.  A run computed on its own
does not know what an earlier extra-month run of the window paid, nor the
absences of the earlier months that suspend the accrual: it names both
instead of settling them.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.extra_month.liquidation.services import _window_months
from ccnl_engine.inputs import EmploymentPeriod, PayrollRunId, PeriodState, Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _employment(
    started: date, ended: date, slug: str = "commercio-confcommercio"
) -> Employment:
    return Employment(
        ccnl_id=slug,
        level_code="4" if slug.startswith("commercio") else "C3",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(started, ended),
        contract_type=Permanent(),
    )


def _run(employment: Employment, run: PayrollRun, opening: PeriodState) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, run.month, 28),
            employment=employment,
            employer=_EMPLOYER,
            opening_state=opening,
        )
    )


def _chain(employment: Employment, runs: list[PayrollRun]) -> PeriodState:
    state = PeriodState.zero()
    for run in runs:
        state = _run(employment, run, state).closing_state
    return state


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def _ratei(result: PeriodResult) -> dict[int, Decimal]:
    return {
        item.month_number: item.quantity
        for item in result.pay_items
        if item.kind == "extra_month_earning"
    }


_LEAVER = _employment(date(2026, 3, 15), date(2026, 11, 16))


def test_an_early_tredicesima_is_not_liquidated_again() -> None:
    """A tredicesima paid in October leaves only the quattordicesima ratei.

    The window of the tredicesima of 2026 is January to December (art.
    220): the October run already paid ratei of it, so the November run
    liquidates the quattordicesima alone (July to 16 November, 5/12) and
    names the residual it cannot compute.
    """
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    runs.insert(4, PayrollRun.fourteenth(2026, 6))
    runs.append(PayrollRun.thirteenth(2026, 10))
    november = _run(_LEAVER, PayrollRun.regular(2026, 11), _chain(_LEAVER, runs))

    assert _ratei(november) == {14: Decimal(5) / 12}
    assert "extra_month_paid_before_termination" in _codes(november)
    assert not november.is_payable


def test_chained_ratei_name_the_absences_of_the_earlier_months() -> None:
    """March to October closed before: their absences are not in the state."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    november = _run(_LEAVER, PayrollRun.regular(2026, 11), _chain(_LEAVER, runs))

    assert "termination_window_absences_unknown" in _codes(november)
    assert "extra_month_paid_before_termination" not in _codes(november)


def test_an_employment_of_one_month_has_no_earlier_absences() -> None:
    """Hired on 2 November and leaving on 30 November: the run is the window."""
    leaver = _employment(date(2026, 11, 2), date(2026, 11, 30))
    november = _run(leaver, PayrollRun.regular(2026, 11), PeriodState.zero())

    assert _ratei(november)
    assert "termination_window_absences_unknown" not in _codes(november)


def test_a_termination_run_after_the_regular_run_settles_nothing_again() -> None:
    """The regular run of November paid the ratei: its termination run does not."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 12)]
    termination = _run(
        _LEAVER,
        PayrollRun.of(PayrollRunId.parse("2026-11-termination")),
        _chain(_LEAVER, runs),
    )

    assert not _ratei(termination)
    assert not _codes(termination) & {
        "termination_window_absences_unknown",
        "extra_month_paid_before_termination",
    }


def test_a_calendar_with_nothing_left_to_liquidate_names_nothing() -> None:
    """Metalmeccanico pays the tredicesima in December: leaving on 31 December.

    The tredicesima is paid on its own run, so the December regular run
    liquidates no ratei and names no issue of them.
    """
    leaver = _employment(
        date(2026, 1, 1), date(2026, 12, 31), "metalmeccanico-federmeccanica"
    )
    runs = [PayrollRun.regular(2026, month) for month in range(1, 12)]
    december = _run(leaver, PayrollRun.regular(2026, 12), _chain(leaver, runs))

    assert not _ratei(december)
    assert "termination_window_absences_unknown" not in _codes(december)


def _issue(result: PeriodResult, code: str) -> CalculationIssue:
    return next(issue for issue in result.issues if issue.code == code)


def test_the_residual_issue_names_its_extra_month_and_blocks() -> None:
    """The paid-early issue is incomplete, on the base salary, and says which."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    runs.append(PayrollRun.thirteenth(2026, 10))
    november = _run(_LEAVER, PayrollRun.regular(2026, 11), _chain(_LEAVER, runs))
    issue = _issue(november, "extra_month_paid_before_termination")

    assert issue.capability == "base_salary"
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.message.startswith("a thirteenth run closed earlier in the window")


def test_the_absences_issue_is_provisional_on_the_base_salary() -> None:
    """The earlier months of the window may hold absences the state lacks."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    november = _run(_LEAVER, PayrollRun.regular(2026, 11), _chain(_LEAVER, runs))
    issue = _issue(november, "termination_window_absences_unknown")

    assert issue.capability == "base_salary"
    assert issue.status is CalculationStatus.PROVISIONAL
    assert issue.message.startswith(
        "the ratei liquidated at the termination count the absences of this run"
    )


def test_a_termination_run_pays_the_ratei_its_month_has_not_paid() -> None:
    """Without a closed regular run of November, the termination run pays."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    termination = _run(
        _LEAVER,
        PayrollRun.of(PayrollRunId.parse("2026-11-termination")),
        _chain(_LEAVER, runs),
    )

    assert _ratei(termination)


def test_a_termination_run_after_its_regular_run_names_no_early_payment() -> None:
    """A tredicesima paid in October is the regular run's issue, not again."""
    runs = [PayrollRun.regular(2026, month) for month in range(3, 12)]
    runs.insert(8, PayrollRun.thirteenth(2026, 10))
    termination = _run(
        _LEAVER,
        PayrollRun.of(PayrollRunId.parse("2026-11-termination")),
        _chain(_LEAVER, runs),
    )

    assert "extra_month_paid_before_termination" not in _codes(termination)


@pytest.mark.parametrize("month", [11, 12])
def test_an_extra_month_run_the_termination_liquidates_is_refused(month: int) -> None:
    """A tredicesima in or after the month of leaving would pay it twice."""
    runs = [PayrollRun.regular(2026, m) for m in range(3, 11)]
    with pytest.raises(InvalidInputError, match="liquidates") as refused:
        _run(_LEAVER, PayrollRun.thirteenth(2026, month), _chain(_LEAVER, runs))

    assert refused.value.field == "PayrollRun.run_kind"
    assert refused.value.feature == "payroll_run"


def test_an_extra_month_paid_inside_the_employment_is_not_refused() -> None:
    """Metalmeccanico leaving on 31 December pays its tredicesima as usual."""
    leaver = _employment(
        date(2026, 1, 1), date(2026, 12, 31), "metalmeccanico-federmeccanica"
    )
    runs = [PayrollRun.regular(2026, month) for month in range(1, 12)]
    thirteenth = _run(leaver, PayrollRun.thirteenth(2026, 12), _chain(leaver, runs))

    assert thirteenth.period_gross > 0


def test_a_regular_run_of_the_year_before_is_no_earlier_month_of_the_window() -> None:
    """Hired in December 2026, leaving in January: no 2027 month closed before."""
    leaver = _employment(date(2026, 12, 1), date(2027, 1, 20))
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=leaver, employer=_EMPLOYER)
    )
    january = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2027, 1),
            payment_date=date(2027, 1, 28),
            employment=leaver,
            employer=_EMPLOYER,
            opening_state=year.next_opening_state,
        )
    )

    assert _ratei(january)
    assert "termination_window_absences_unknown" not in _codes(january)


@pytest.mark.parametrize(
    ("payment_month", "ended_month", "months"),
    [
        (6, 11, range(7, 12)),
        (11, 11, range(1, 12)),
        (12, 11, range(1, 12)),
        (12, 1, range(1, 2)),
    ],
)
def test_the_window_runs_from_the_month_after_the_payment_to_the_leaving(
    payment_month: int, ended_month: int, months: range
) -> None:
    """A payment before the leaving month opens the window the month after it."""
    assert _window_months(payment_month, ended_month) == months
