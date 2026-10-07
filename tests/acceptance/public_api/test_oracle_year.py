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
from ccnl_engine.inputs import EmploymentPeriod, PeriodState
from tests.fixtures.seniority import new_hire

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
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
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
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


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


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "on chained runs the quattordicesima of a worker leaving on 16 "
        "November cannot be paid: fourteenth(2026, 11) is refused as already "
        "closed by June and the November run has no blocker for the July to "
        "November twelfths (CCNL Terziario art. 221) that the competence "
        "year pays"
    ),
)
def test_termination_fourteenth_is_paid_on_chained_runs() -> None:
    """Commercio level 4 from 15 March to 16 November 2026, both paths.

    The two paths compute the same employment, so they pay the same gross.
    """
    year = engine.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_LEAVER, employer=_EMPLOYER)
    )
    planned = sum((r.period_gross for r in year.period_results), Decimal(0))
    assert _chained_gross() == planned
