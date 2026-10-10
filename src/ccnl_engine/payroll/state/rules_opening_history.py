"""Whether the state a run opens with holds the history of the employment.

IRPEF is withheld on the progressive totals of the tax year (art. 23 c. 1
and c. 3 DPR 600/1973), and the IVS massimale and the additional 1% of the
year are counted on the INPS base of the whole competence year (L. 335/1995
art. 2 c. 18; D.L. 384/1992 art. 3-ter).  A run that opens with a zero state
after the start of the employment restarts those totals from zero, and on
the first run of a tax year it drops the surtax and the recoveries the
conguaglio of the year before carried.  The opening state is therefore a
fact of the run, not a default: a run whose state misses part of the
history is computed as a simulation and reported with a ``missing_fact``
issue naming ``opening_state``.

The history is missing when:

- the state descends from a run whose closing state misses it: a run that
  opened without it, or a conguaglio that could not determine the surtax
  of the year for lack of the residence
  (:attr:`~ccnl_engine.payroll.state.models.PeriodState.history_known`
  is ``False``);
- a regular month of the competence year of the run, from January or from
  the start of the employment, before the month of the run, is not closed
  in it;
- the employment began before the competence year of the run, or its start
  is not stated, and the state carries nothing of an earlier tax year: no
  run closed and no tax year bound.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.period.models_run import RunKind
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.models_run import PayrollRunId
    from ccnl_engine.payroll.state.models import PeriodState

__all__ = ["FACT", "opening_gap", "opening_state_issue"]

#: Public fact the issue names.
FACT = "opening_state"
_CODE = "opening_state_unknown"
#: First month of a year the employment starts after: no month is required.
_NO_MONTH = 13
_REMEDY = (
    "pass the closing state of the previous run, close_tax_year() of the "
    "previous tax year, or the balances imported with "
    "import_opening_balances(); PeriodState.zero() only opens the first run "
    "of an employment whose start is stated"
)


def opening_gap(
    opening: PeriodState,
    run_id: PayrollRunId,
    started_on: date | None,
    uncovered: tuple[PayrollRunId, ...] = (),
) -> str | None:
    """Return what the opening state of ``run_id`` misses of the history.

    Args:
        opening: State the run opens with.
        run_id: The run.
        started_on: First day of the employment, ``None`` when not stated.
        uncovered: Runs a year calculation left out because the bundle
            holds no pay rules on their date; already reported as
            ``run_not_computed`` on the year, they are not missing history.

    Returns:
        A description of the missing history, or ``None`` when the state
        holds it.
    """
    if not opening.history_known:
        return (
            "it descends from a run whose closing state misses the history "
            "(a run opened without it, or a conguaglio without the residence)"
        )
    year = run_id.year
    earlier = started_on is None or started_on < date(year, 1, 1)
    closed = {
        r.month
        for r in (*opening.accrual.runs_of(year), *uncovered)
        if r.kind is RunKind.REGULAR and r.year == year
    }
    first = _first_month(year, started_on)
    missing = [month for month in range(first, run_id.month) if month not in closed]
    if missing:
        return f"the regular runs of {year} in months {missing} are not closed in it"
    if earlier and _carries_nothing(opening):
        start = "is not stated" if started_on is None else f"is {started_on}"
        return (
            f"the start of the employment {start}, before {year}, and it "
            "carries nothing of an earlier tax year"
        )
    return None


def opening_state_issue(
    opening: PeriodState,
    run_id: PayrollRunId,
    started_on: date | None,
    uncovered: tuple[PayrollRunId, ...] = (),
) -> CalculationIssue | None:
    """Return the missing-fact issue of a run opened without its history.

    Returns:
        An incomplete issue naming ``opening_state``, or ``None``.
    """
    gap = opening_gap(opening, run_id, started_on, uncovered)
    if gap is None:
        return None
    return CalculationIssue(
        code=_CODE,
        message=(
            f"the opening state of run '{run_id}' misses the history of the "
            f"employment: {gap}.  The progressive IRPEF (art. 23 DPR 600/1973; "
            "art. 33 D.Lgs. 33/2025 from 2027), "
            "the INPS base of the year and the carried obligations are "
            f"computed from zero as a simulation: {_REMEDY}"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FACT,
    )


def _first_month(year: int, started_on: date | None) -> int:
    """Return the first regular month of ``year`` the employment holds.

    Returns:
        January for an employment begun earlier or whose start is not
        stated, the month of the start within ``year``, and a month after
        December for a start after ``year``.
    """
    if started_on is None or started_on.year < year:
        return 1
    return started_on.month if started_on.year == year else _NO_MONTH


def _carries_nothing(opening: PeriodState) -> bool:
    return not opening.accrual.competence_runs and opening.cash == TaxCashState()
