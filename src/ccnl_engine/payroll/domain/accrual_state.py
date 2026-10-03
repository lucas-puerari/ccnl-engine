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
ratei liquidati are the extra-month runs closed here.  The INPS base
toward the IVS massimale follows competence too
(:mod:`~ccnl_engine.payroll.domain.inps_base`), so it is counted here per
competence year.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import final

from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["EmploymentAccrualState"]

_FEATURE = "accrual_state"
_FIELD = "EmploymentAccrualState.competence_runs"
_BASES = "EmploymentAccrualState.inps_bases"
_ZERO = Decimal(0)
_EXTRA_MONTHS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


@final
@dataclass(frozen=True)
class EmploymentAccrualState:
    """Competence runs closed over the employment, in closing order.

    Invariants: a run closes once, so a competence year has at most twelve
    regular months and one run per extra month.  Within one competence year
    the regular months close in month order and nothing closes after the
    termination run.  Extra months and adjustment runs are not ordered
    against the regular months: the ratei of a tredicesima or a
    quattordicesima are counted from the employment dates, not from the
    regular runs closed, so an employer may pay the tredicesima before the
    December salary, or the quattordicesima before a July salary paid in
    August.  The order of the payments themselves is a cash matter, kept by
    :class:`~ccnl_engine.payroll.domain.tax_cash_state.TaxCashState`.  Runs
    of different competence years are not ordered against each other: a
    late December of one year may be paid after January of the next.

    Attributes:
        competence_runs: Identifiers of the runs closed, in closing order.
        inps_bases: INPS base toward the massimale of each competence year
            with a base, one per year, in year order.

    Raises:
        InvalidInputError: When a run id is not a
            :class:`~ccnl_engine.payroll.domain.run.PayrollRunId`, is
            repeated, is a regular month closing after a later regular month
            of its competence year, or closes after its termination run; or
            when two INPS bases are of the same year or out of year order.
    """

    competence_runs: tuple[PayrollRunId, ...] = ()
    inps_bases: tuple[InpsBaseYtd, ...] = ()

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
        bases = tuple_of(
            self.inps_bases,
            _BASES,
            items_of_type(InpsBaseYtd, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "inps_bases", bases)
        years = [b.year for b in bases]
        if years != sorted(set(years)):
            msg = f"inps_bases must hold one base per year, in year order; got {years}"
            raise InvalidInputError(msg, field=_BASES, feature=_FEATURE)

    def check_next_run(self, run_id: PayrollRunId) -> None:
        """Check that ``run_id`` can close next.

        A run already closed, a regular month before a closed regular month
        of its competence year, or a run after its termination run raises
        ``InvalidInputError``.
        """
        _check_next(self.competence_runs, run_id)

    def after(
        self, run_id: PayrollRunId, inps_base: Decimal = _ZERO
    ) -> EmploymentAccrualState:
        """Return the state with ``run_id`` closed and its INPS base added.

        Args:
            run_id: The run closed.
            inps_base: INPS base of the run, added to its competence year.

        Returns:
            A new state with ``run_id`` appended; it is validated again.
        """
        base = self.inps_base(run_id.year).plus(inps_base)
        others = [b for b in self.inps_bases if b.year != run_id.year]
        return EmploymentAccrualState(
            competence_runs=(*self.competence_runs, run_id),
            inps_bases=tuple(sorted((*others, base), key=lambda b: b.year)),
        )

    def inps_base(self, year: int) -> InpsBaseYtd:
        """Return the INPS base of competence year ``year``.

        Returns:
            The base of the year, zero when none is recorded.
        """
        return next((b for b in self.inps_bases if b.year == year), InpsBaseYtd(year))

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
        InvalidInputError: When ``run_id``, or the extra month of its year
            paid in another month, is in ``closed``; when it is a
            regular month and a later regular month of its competence year
            is in ``closed``; or when a termination run of its competence
            year is in ``closed`` and ``run_id`` is not an adjustment.
    """
    twin = next((r for r in closed if r.payment_key == run_id.payment_key), None)
    if twin is not None:
        msg = (
            f"run '{run_id}' is already closed as '{twin}': a run closes once, "
            "an extra month once per year whatever its month"
        )
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
    same_year = [r for r in closed if r.year == run_id.year]
    blocking = [r for r in same_year if r.kind is RunKind.TERMINATION]
    if run_id.kind is RunKind.ADJUSTMENT:
        return
    if run_id.kind is RunKind.REGULAR:
        blocking += [
            r for r in same_year if r.kind is RunKind.REGULAR and r.month > run_id.month
        ]
    if blocking:
        msg = (
            f"run '{run_id}' is out of order: run '{blocking[0]}' of competence "
            f"year {run_id.year} is already closed"
        )
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
