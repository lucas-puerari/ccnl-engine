"""Competence state of an employment: the runs whose competence is closed.

Competence and cash are two clocks.  A run is the competence of a month or
an extra month and closes once over the whole employment, whatever tax year
pays it; the tax cash state
(:class:`~ccnl_engine.payroll.domain.tax_cash_state.TaxCashState`) counts
the payments of one tax year instead.  This state is therefore carried
unchanged across the change of tax year
(:func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`):
December 2026 closed in 2026 cannot be paid again in 2027.

The extra-month ratei maturati are counted from the employment dates
(:class:`~ccnl_engine.payroll.domain.accrual.ExtraMonthAccrual`); the
ratei liquidati are the extra-month runs closed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["EmploymentAccrualState"]

_FEATURE = "accrual_state"
_FIELD = "EmploymentAccrualState.competence_runs"
_EXTRA_MONTHS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


@final
@dataclass(frozen=True)
class EmploymentAccrualState:
    """Competence runs closed over the employment, in closing order.

    Invariants: a run closes once, so a competence year has at most twelve
    regular months and one run per extra month; within one competence year
    the runs close in payment order (month, then regular before extra
    months before termination), adjustment runs excepted.  Runs of
    different competence years are not ordered against each other: a late
    December of one year may be paid after January of the next.

    Attributes:
        competence_runs: Identifiers of the runs closed, in closing order.

    Raises:
        InvalidInputError: When a run id is not a
            :class:`~ccnl_engine.payroll.domain.run.PayrollRunId`, is
            repeated, or closes out of order within its competence year.
    """

    competence_runs: tuple[PayrollRunId, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        runs = tuple_of(
            self.competence_runs,
            _FIELD,
            items_of_type(PayrollRunId, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "competence_runs", runs)
        for index, run_id in enumerate(runs):
            _check_next(runs[:index], run_id)

    def check_next_run(self, run_id: PayrollRunId) -> None:
        """Check that ``run_id`` can close next.

        A run already closed, or before a closed run of its competence year
        (adjustment runs excepted), raises ``InvalidInputError``.
        """
        _check_next(self.competence_runs, run_id)

    def after(self, run_id: PayrollRunId) -> EmploymentAccrualState:
        """Return the state with ``run_id`` closed.

        Returns:
            A new state with ``run_id`` appended; it is validated again.
        """
        return EmploymentAccrualState(competence_runs=(*self.competence_runs, run_id))

    def runs_of(self, year: int) -> tuple[PayrollRunId, ...]:
        """Return the closed runs of competence year ``year``.

        Returns:
            The runs of ``year``, in closing order.
        """
        return tuple(r for r in self.competence_runs if r.year == year)

    def regular_months(self, year: int) -> int:
        """Return how many regular months of ``year`` are closed.

        Returns:
            The count, at most 12: a regular run closes once.
        """
        return sum(1 for r in self.runs_of(year) if r.kind is RunKind.REGULAR)

    def extra_months_paid(self, year: int) -> tuple[PayrollRunId, ...]:
        """Return the extra-month runs of ``year`` closed.

        Returns:
            The thirteenth and fourteenth runs of ``year`` closed: the ratei
            liquidati.
        """
        return tuple(r for r in self.runs_of(year) if r.kind in _EXTRA_MONTHS)


def _check_next(closed: tuple[PayrollRunId, ...], run_id: PayrollRunId) -> None:
    """Check that ``run_id`` can close after the runs ``closed``.

    Raises:
        InvalidInputError: When ``run_id`` is in ``closed``, or is not an
            adjustment run and a run of its competence year after it (other
            than an adjustment) is in ``closed``.
    """
    if run_id in closed:
        msg = f"run '{run_id}' is already closed: a run closes once"
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
    if run_id.kind is RunKind.ADJUSTMENT:
        return
    later = [
        r
        for r in closed
        if r.year == run_id.year
        and r.kind is not RunKind.ADJUSTMENT
        and r.order_key > run_id.order_key
    ]
    if later:
        msg = (
            f"run '{run_id}' is out of order: run '{later[0]}' of competence "
            f"year {run_id.year} is already closed"
        )
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
