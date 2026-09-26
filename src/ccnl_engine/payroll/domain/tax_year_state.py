"""Year-to-date state of one tax year: counters and YTD accounts.

Everything here belongs to a single tax year and restarts from zero when
the next tax year opens
(:func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`).
Obligations that survive the year change live in
:class:`~ccnl_engine.payroll.domain.obligations.EmploymentObligations`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import final

from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)

__all__ = ["TaxYearState"]

_MIN_TAX_YEAR = 2020
_MAX_REGULAR_PERIODS = 12
_MAX_WITHHOLDING_PERIODS = 14


@final
@dataclass(frozen=True)
class TaxYearState:
    """Counters and YTD accounts of one tax year.

    Attributes:
        tax_year: Tax year the counters and accounts belong to.  ``None`` on
            a manually built state not yet bound to a year; every state
            produced by a run carries it.
        regular_periods_closed: Number of regular (``run_kind="regular"``)
            payroll periods already closed this tax year.  Not used for the
            extra-month ratei, which are counted from the employment dates
            (:class:`~ccnl_engine.payroll.domain.accrual.ExtraMonthAccrual`).
        tax_withholding_periods_closed: Number of periods that have consumed
            an IRPEF withholding slot (regular + thirteenth + fourteenth;
            not adjustment).  Used for the conguaglio divisor.
        withholding_slots: Number of withholding slots of the schedule the
            last run was computed on, or ``None`` before the first run.  The
            tax year is complete when ``tax_withholding_periods_closed``
            reaches it.
        closed_run_ids: Identifiers of the runs already closed this tax
            year, in closing order.  Each run closes once; no run is of a
            year after ``tax_year``; the runs of ``tax_year`` itself close in
            payment order (month, then regular before extra months before
            termination), adjustment runs excepted.  A run of an earlier
            year paid late (TUIR art. 51 c. 1) is not ordered.  Integrations
            that do not keep run ids may leave it empty; otherwise it holds
            at most as many regular and slot-consuming runs as the
            counters.
        earnings: Running totals for earned income and INPS contribution
            bases (gross, taxable, INPS base, employee INPS).
        fringe: Running totals for fringe benefits and PdR (value, taxed
            base, PdR eligible amount).
        tax: Running totals for tax withheld this year (IRPEF, surtax).
        trattamento: YTD credit account for trattamento integrativo of this
            tax year.  Installments of a recovery carried from an earlier
            year do not enter it.
        somma_esente: YTD credit account for the somma esente bonus
            (L. 207/2024).
        ulteriore_detrazione: YTD account of the ulteriore detrazione
            (L. 207/2024 art. 1 c. 6) recognized by the withholding.
        work_time_regime: YTD usage of the annual cap of the night, holiday
            and shift supplement substitute tax (L. 199/2025 art. 1
            cc. 10-11).
        shortfall: IRPEF and surtax due on earlier runs and not yet
            withheld because the pay left did not cover them.
    """

    tax_year: int | None = None
    regular_periods_closed: int = 0
    tax_withholding_periods_closed: int = 0
    withholding_slots: int | None = None
    closed_run_ids: tuple[PayrollRunId, ...] = ()
    earnings: EarningsYtd = field(default_factory=EarningsYtd)
    fringe: FringeYtd = field(default_factory=FringeYtd)
    tax: TaxYtd = field(default_factory=TaxYtd)
    trattamento: TrattamentoAccount = field(default_factory=TrattamentoAccount)
    somma_esente: SommaEsenteAccount = field(default_factory=SommaEsenteAccount)
    ulteriore_detrazione: UlterioreDetrazioneAccount = field(
        default_factory=UlterioreDetrazioneAccount
    )
    work_time_regime: RegimeCapAccount = field(default_factory=RegimeCapAccount)
    shortfall: WithholdingShortfall = field(default_factory=WithholdingShortfall)

    def __post_init__(self) -> None:
        """Validate structural invariants on construction.

        Raises:
            ValueError: When any field violates a range or ordering constraint.
        """
        if self.tax_year is not None and self.tax_year < _MIN_TAX_YEAR:
            msg = f"tax_year must be >= {_MIN_TAX_YEAR}; got {self.tax_year}"
            raise ValueError(msg)
        if not 0 <= self.regular_periods_closed <= _MAX_REGULAR_PERIODS:
            msg = (
                f"regular_periods_closed must be in [0, {_MAX_REGULAR_PERIODS}]; "
                f"got {self.regular_periods_closed}"
            )
            raise ValueError(msg)
        if self.tax_withholding_periods_closed < self.regular_periods_closed:
            msg = (
                f"tax_withholding_periods_closed "
                f"({self.tax_withholding_periods_closed}) "
                f"must be >= regular_periods_closed "
                f"({self.regular_periods_closed})"
            )
            raise ValueError(msg)
        if self.tax_withholding_periods_closed > _MAX_WITHHOLDING_PERIODS:
            msg = (
                f"tax_withholding_periods_closed must be <= "
                f"{_MAX_WITHHOLDING_PERIODS}; "
                f"got {self.tax_withholding_periods_closed}"
            )
            raise ValueError(msg)
        if self.withholding_slots is not None and self.withholding_slots < 1:
            msg = f"withholding_slots must be >= 1; got {self.withholding_slots}"
            raise ValueError(msg)
        self._check_closed_runs()

    def _check_closed_runs(self) -> None:
        """Validate :attr:`closed_run_ids` against the tax year and counters.

        Raises:
            ValueError: When the ids are not bound to a tax year, break the
                closing rules of :attr:`closed_run_ids` or outnumber the
                counters.
        """
        ids = self.closed_run_ids
        if not ids:
            return
        if self.tax_year is None:
            msg = "closed_run_ids requires a tax_year"
            raise ValueError(msg)
        seen: list[PayrollRunId] = []
        for run_id in ids:
            _check_next_run(tuple(seen), run_id, self.tax_year)
            seen.append(run_id)
        regular = sum(1 for r in ids if r.kind is RunKind.REGULAR)
        slots = sum(1 for r in ids if r.kind.consumes_withholding_slot)
        if regular > self.regular_periods_closed:
            msg = (
                f"closed_run_ids holds {regular} regular runs but "
                f"regular_periods_closed is {self.regular_periods_closed}"
            )
            raise ValueError(msg)
        if slots > self.tax_withholding_periods_closed:
            msg = (
                f"closed_run_ids holds {slots} slot-consuming runs but "
                f"tax_withholding_periods_closed is "
                f"{self.tax_withholding_periods_closed}"
            )
            raise ValueError(msg)

    def check_next_run(self, run_id: PayrollRunId) -> None:
        """Check that ``run_id`` can close next in this tax year.

        A run already closed, of a year after :attr:`tax_year`, or before a
        run of the tax year already closed raises ``ValueError``.
        """
        _check_next_run(self.closed_run_ids, run_id, self.tax_year)

    @property
    def is_complete(self) -> bool:
        """Whether every withholding slot of the year has been closed.

        Returns:
            ``True`` when a run has recorded ``withholding_slots`` and
            ``tax_withholding_periods_closed`` has reached it.
        """
        return (
            self.withholding_slots is not None
            and self.tax_withholding_periods_closed >= self.withholding_slots
        )


def _check_next_run(
    closed: tuple[PayrollRunId, ...], run_id: PayrollRunId, tax_year: int | None
) -> None:
    """Check that ``run_id`` can close after the runs ``closed``.

    Raises:
        ValueError: When ``run_id`` is in ``closed``, is of a year after
            ``tax_year``, or is a run of ``tax_year`` other than an
            adjustment that precedes a run of ``tax_year`` in ``closed``.
    """
    if run_id in closed:
        msg = f"Run '{run_id}' was already processed in this payroll year"
        raise ValueError(msg)
    if tax_year is None:
        return
    if run_id.year > tax_year:
        msg = f"run '{run_id}' is of a year after the tax year {tax_year}"
        raise ValueError(msg)
    if run_id.year < tax_year or run_id.kind is RunKind.ADJUSTMENT:
        return
    later = [
        r
        for r in closed
        if r.year == tax_year
        and r.kind is not RunKind.ADJUSTMENT
        and r.order_key > run_id.order_key
    ]
    if later:
        msg = (
            f"run '{run_id}' is out of order: run '{later[0]}' of tax year "
            f"{tax_year} is already closed"
        )
        raise ValueError(msg)
