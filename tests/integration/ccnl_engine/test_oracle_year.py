"""Oracle cases of a competence year: the extra months paid in their own run.

Each case is verified against the computation chain; expected values are frozen
and must NOT be auto-updated from the engine.  A failing assertion means a
computation-affecting change was made without reviewing these oracle cases.

Source for values: hand-traced payroll computation chains and CCNL source data.
All monetary amounts in EUR.
"""

from __future__ import annotations

import contextlib
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import EmploymentPeriod, PeriodState, Permanent
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

engine = PayrollEngine.bundled()


# ---------------------------------------------------------------------------
# Mensilità aggiuntive (area: tredicesima)
# ---------------------------------------------------------------------------


def test_tredicesima_commercio_level4() -> None:
    """Tredicesima for commercio level 4, computed via full-year run.

    The standard calendar is derived from the CCNL: tredicesima and
    quattordicesima, 14 runs.
    """
    yr = engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(50)
            ),
        )
    )
    tredicesima = next(
        r
        for r in yr.period_results
        if r.run is not None and r.run.run_id == "2026-12-thirteenth"
    )
    assert tredicesima.period_gross == Decimal("1818.75")
    assert len(yr.period_results) == 14


# ---------------------------------------------------------------------------
# Mensilità aggiuntive at termination (area: quattordicesima)
# ---------------------------------------------------------------------------

_LEAVER = Employment(
    ccnl_slug="commercio-confcommercio.json",
    level_code="4",
    seniority=new_hire(),
    employment_period=EmploymentPeriod(date(2026, 3, 15), date(2026, 11, 16)),
    contract_type=Permanent(),
)
_EMPLOYER = EmployerProfile(provincial_pay_element=False, headcount=Headcount(50))


def _run(run: PayrollRun, opening: PeriodState) -> PeriodResult:
    return engine.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, run.month, 28),
            employment=_LEAVER,
            employer=_EMPLOYER,
            opening_state=opening,
        )
    )


def _chained_gross() -> Decimal:
    """Return the gross of March to November run by hand, extra months included.

    The quattordicesima of June and every regular month are chained; the
    termination extra months of November are attempted after the November
    run, and one the engine refuses counts as not paid.

    Returns:
        The total gross of the runs the engine accepted.
    """
    state = PeriodState.zero()
    paid = Decimal(0)
    runs = [PayrollRun.regular(2026, month) for month in range(3, 12)]
    runs.insert(4, PayrollRun.fourteenth(2026, 6))
    runs += [PayrollRun.thirteenth(2026, 11), PayrollRun.fourteenth(2026, 11)]
    for run in runs:
        with contextlib.suppress(InvalidInputError):
            result = _run(run, state)
            state, paid = result.closing_state, paid + result.period_gross
    return paid


def test_termination_fourteenth_is_paid_on_chained_runs() -> None:
    """Commercio level 4 from 15 March to 16 November 2026, both paths.

    The two paths compute the same employment, so they pay the same gross.
    """
    year = engine.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_LEAVER, employer=_EMPLOYER)
    )
    planned = sum((r.period_gross for r in year.period_results), Decimal(0))
    assert _chained_gross() == planned


def _chained_november() -> PeriodResult:
    """Return the November regular run chained after March to October.

    Returns:
        The run of the termination month, the quattordicesima of June paid.
    """
    state = PeriodState.zero()
    runs = [PayrollRun.regular(2026, month) for month in range(3, 11)]
    runs.insert(4, PayrollRun.fourteenth(2026, 6))
    for run in runs:
        state = _run(run, state).closing_state
    return _run(PayrollRun.regular(2026, 11), state)


def test_termination_month_liquidates_the_ratei_on_chained_runs() -> None:
    """The November run pays 9/12 of the tredicesima and 5/12 of the fourteenth.

    CCNL Terziario Confcommercio, Testo Unico 30 July 2019
    (https://www.ebinter.it/ebinter-site/wp-content/uploads/2022/01/
    CCNL-Terziario-Distribuzione-e-Servizi_30-Luglio-2019.pdf):

    - art. 220: the tredicesima counts the 12 months before Christmas Eve,
      so the window of 2026 is January to December; art. 221: the
      quattordicesima is paid on 1 July with the pay in force on 30 June
      and counts the 12 months before it, so the window after June 2026 is
      July 2026 to June 2027;
    - art. 204 (referred to by both): a fraction of a month of at least 15
      days counts as a whole month.

    Tredicesima: 15-31 March is 17 days (a month), April to October 7
    months, 1-16 November 16 days (a month): 9/12.  Quattordicesima: July to
    October 4 months and 1-16 November: 5/12.
    """
    november = _chained_november()

    ratei = {
        item.month_number: item.quantity
        for item in november.pay_items
        if item.kind == "extra_month_earning"
    }
    assert ratei == {13: Decimal(9) / 12, 14: Decimal(5) / 12}


@pytest.mark.parametrize(
    "run",
    [
        PayrollRun.thirteenth(2026, 11),
        PayrollRun.fourteenth(2026, 11),
        PayrollRun.thirteenth(2026, 12),
    ],
    ids=["thirteenth-november", "fourteenth-november", "thirteenth-december"],
)
def test_extra_month_run_after_the_liquidation_is_refused(run: PayrollRun) -> None:
    """The ratei the November run liquidated are not paid a second time."""
    november = _chained_november()

    with pytest.raises(InvalidInputError, match="liquidates on the run"):
        _run(run, november.closing_state)
