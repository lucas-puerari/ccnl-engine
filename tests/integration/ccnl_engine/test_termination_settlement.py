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

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import EmploymentPeriod, PayrollRunId, PeriodState, Permanent
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _employment(
    started: date, ended: date, slug: str = "commercio-confcommercio.json"
) -> Employment:
    return Employment(
        ccnl_slug=slug,
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
        date(2026, 1, 1), date(2026, 12, 31), "metalmeccanico-federmeccanica.json"
    )
    runs = [PayrollRun.regular(2026, month) for month in range(1, 12)]
    december = _run(leaver, PayrollRun.regular(2026, 12), _chain(leaver, runs))

    assert not _ratei(december)
    assert "termination_window_absences_unknown" not in _codes(december)
