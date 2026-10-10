"""Competence state of an employment: the runs whose competence is closed.

Competence and cash are two clocks.  A run is the competence of a month or
an extra month and closes once over the whole employment, whatever tax year
pays it; the tax cash state
(:class:`~ccnl_engine.payroll.state.models_tax_cash.TaxCashState`) counts
the payments of one tax year instead.  This state is therefore carried
unchanged across the change of tax year
(:func:`~ccnl_engine.payroll.year.rules_close.close_tax_year`):
December 2026 closed in 2026 cannot be paid again in 2027.

The extra-month ratei maturati are counted from the employment dates
(:class:`~ccnl_engine.payroll.accrual.models.ExtraMonthAccrual`); the
ratei liquidati are the extra-month runs closed here.  The INPS base
toward the IVS massimale follows competence too
(:mod:`~ccnl_engine.payroll.contribution.models_inps_base`), so it is counted here per
competence year.  The sickness episodes are counted over the employment
too: a waiting period, an INPS band or a CCNL tier depends on the sick days
before the run, whatever tax year paid them.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.contribution.models_inps_base import InpsBaseYtd
from ccnl_engine.payroll.period.models_run import PayrollRunId, RunKind
from ccnl_engine.payroll.sickness.models import SicknessEpisode
from ccnl_engine.validation import require_date
from ccnl_engine.validation_collection import items_of_type, tuple_of

__all__ = ["EmploymentAccrualState"]

_FEATURE = "accrual_state"
_FIELD = "EmploymentAccrualState.competence_runs"
_BASES = "EmploymentAccrualState.inps_bases"
_SICKNESS = "EmploymentAccrualState.sickness_episodes"
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
    :class:`~ccnl_engine.payroll.state.models_tax_cash.TaxCashState`.  Runs
    of different competence years are not ordered against each other: a
    late December of one year may be paid after January of the next.

    Attributes:
        competence_runs: Identifiers of the runs closed, in closing order.
        inps_bases: INPS base toward the massimale of each competence year
            with a base, one per year, in year order.
        sickness_episodes: Sickness episodes the runs processed, each cut at
            its last processed day, in start order.
        sickness_known_from: First day from which :attr:`sickness_episodes`
            list every sick day of the employment; ``None`` when they list
            all of them (a new employment, or an import that states so).
            A CCNL that counts the sickness of several episodes cannot
            count the days before it.

    Raises:
        InvalidInputError: When a run id is not a
            :class:`~ccnl_engine.payroll.period.models_run.PayrollRunId`, is
            repeated, is a regular month closing after a later regular month
            of its competence year, or closes after its termination run; or
            when two INPS bases are of the same year or out of year order.
    """

    competence_runs: tuple[PayrollRunId, ...] = ()
    inps_bases: tuple[InpsBaseYtd, ...] = ()
    sickness_episodes: tuple[SicknessEpisode, ...] = ()
    sickness_known_from: date | None = None

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
        object.__setattr__(self, "sickness_episodes", _episodes(self, _SICKNESS))
        require_date(
            self.sickness_known_from,
            "EmploymentAccrualState.sickness_known_from",
            feature=_FEATURE,
            optional=True,
        )

    def check_next_run(self, run_id: PayrollRunId) -> None:
        """Check that ``run_id`` can close next.

        A run already closed, a regular month before a closed regular month
        of its competence year, or a run after its termination run raises
        ``InvalidInputError``.
        """
        _check_next(self.competence_runs, run_id)

    def after(
        self,
        run_id: PayrollRunId,
        inps_base: Decimal = _ZERO,
        sickness_episodes: tuple[SicknessEpisode, ...] | None = None,
        additional_ivs: Decimal = _ZERO,
    ) -> EmploymentAccrualState:
        """Return the state with ``run_id`` closed and its INPS base added.

        Args:
            run_id: The run closed.
            inps_base: INPS base of the run, added to its competence year
                and month.
            sickness_episodes: Sickness episodes after the run, ``None``
                when the run processed none.
            additional_ivs: Additional 1% IVS the run withheld, added to
                its competence year.

        Returns:
            A new state with ``run_id`` appended; it is validated again.
        """
        return replace(
            self,
            competence_runs=(*self.competence_runs, run_id),
            inps_bases=self._bases_with(
                self.inps_base(run_id.year).plus(
                    inps_base, run_id.month, additional_ivs
                )
            ),
            sickness_episodes=(
                self.sickness_episodes
                if sickness_episodes is None
                else sickness_episodes
            ),
        )

    def with_inps_base(self, base: InpsBaseYtd) -> EmploymentAccrualState:
        """Return the state with ``base`` in place of the base of its year.

        Returns:
            A new state; the runs and the sickness record are unchanged.
        """
        return replace(self, inps_bases=self._bases_with(base))

    def _bases_with(self, base: InpsBaseYtd) -> tuple[InpsBaseYtd, ...]:
        others = [b for b in self.inps_bases if b.year != base.year]
        return tuple(sorted((*others, base), key=lambda b: b.year))

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
    if run_id.kind is RunKind.ADJUSTMENT:
        return
    same_year = [r for r in closed if r.year == run_id.year]
    termination = next((r for r in same_year if r.kind is RunKind.TERMINATION), None)
    if termination is not None:
        msg = (
            f"run '{run_id}' cannot close: the termination run '{termination}' "
            "ended the employment this state belongs to, and only an "
            "adjustment run closes after it.  A rehire is a new employment: "
            "open its first run with PeriodState.zero() and the employment "
            "period of the rehire; the income and the days of the earlier "
            "employment are then not merged into its withholding"
        )
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
    blocking = []
    if run_id.kind is RunKind.REGULAR:
        blocking = [
            r for r in same_year if r.kind is RunKind.REGULAR and r.month > run_id.month
        ]
    if blocking:
        msg = (
            f"run '{run_id}' is out of order: run '{blocking[0]}' of competence "
            f"year {run_id.year} is already closed"
        )
        raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)


def _episodes(state: EmploymentAccrualState, path: str) -> tuple[SicknessEpisode, ...]:
    """Return the validated sickness episodes of ``state``.

    Returns:
        The episodes as a tuple.

    Raises:
        InvalidInputError: When an item is not a sickness episode, two share
            an id or they are out of start order.
    """
    episodes = tuple_of(
        state.sickness_episodes,
        path,
        items_of_type(SicknessEpisode, feature=_FEATURE),
        feature=_FEATURE,
    )
    ids = [e.episode_id for e in episodes]
    starts = [e.started_on for e in episodes]
    if len(set(ids)) != len(ids) or starts != sorted(starts):
        msg = f"sickness episodes must have distinct ids, in start order; got {ids}"
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    return episodes
