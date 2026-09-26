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

from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
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
        closed_run_ids: Frozen set of ``run_id`` strings for every run
            already closed this tax year.  Prevents reprocessing the same
            run.
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
        work_time_regime: YTD usage of the annual cap of the night, holiday
            and shift supplement substitute tax (L. 199/2025 art. 1
            cc. 10-11).
    """

    tax_year: int | None = None
    regular_periods_closed: int = 0
    tax_withholding_periods_closed: int = 0
    withholding_slots: int | None = None
    closed_run_ids: frozenset[str] = field(default_factory=frozenset)
    earnings: EarningsYtd = field(default_factory=EarningsYtd)
    fringe: FringeYtd = field(default_factory=FringeYtd)
    tax: TaxYtd = field(default_factory=TaxYtd)
    trattamento: TrattamentoAccount = field(default_factory=TrattamentoAccount)
    somma_esente: SommaEsenteAccount = field(default_factory=SommaEsenteAccount)
    work_time_regime: RegimeCapAccount = field(default_factory=RegimeCapAccount)

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
