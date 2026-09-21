"""Typed YTD state for the period-first payroll engine.

``PayrollState`` is the single source of truth for all year-to-date
accumulators.  It groups them into three typed sub-states (fiscal,
contributive, leave) plus audit metadata, and is advanced by the pure
:func:`~ccnl_engine.payroll.application.close_period.close` function.

Design notes:
- All sub-states are frozen dataclasses.
- ``revision_id`` is deterministic: ``"ytd-{tax_year}-p{periods_closed:02d}"``.
- ``source_period_ids`` is an append-only tuple; each ``close()`` call appends
  the just-closed ``PeriodId``.
- Monotonicity is NOT asserted globally.  Individual normative guarantees are
  tested at the field level where the law requires it (e.g. ``irpef_withheld``
  must not decrease within a tax year absent a correction).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId

_ZERO = Decimal(0)


@dataclass(frozen=True)
class FiscalState:
    """Fiscal year-to-date accumulators for IRPEF and related credits.

    Attributes:
        taxable_income_ytd: Imponibile fiscale accrued YTD.
        irpef_gross_ytd: IRPEF lorda (before deductions) accrued YTD.
        irpef_withheld_ytd: Net IRPEF withheld YTD (after credits).
        work_income_deduction_ytd: Detrazione per redditi di lavoro used YTD.
        fam_deductions_ytd: Family deductions (spouse, children) used YTD.
        art15_deductions_ytd: Art. 15 TUIR additional deductions used YTD.
        trattamento_integrativo_ytd: Tax credit (Art. 1 D.L. 3/2020) YTD.
        addizionale_regionale_ytd: Regional surtax withheld YTD.
        addizionale_comunale_ytd: Municipal surtax withheld YTD.
    """

    taxable_income_ytd: Decimal
    irpef_gross_ytd: Decimal
    irpef_withheld_ytd: Decimal
    work_income_deduction_ytd: Decimal
    fam_deductions_ytd: Decimal
    art15_deductions_ytd: Decimal
    trattamento_integrativo_ytd: Decimal
    addizionale_regionale_ytd: Decimal
    addizionale_comunale_ytd: Decimal

    @classmethod
    def zero(cls) -> FiscalState:
        """Return a zero-valued FiscalState for the start of a tax year.

        Returns:
            A :class:`FiscalState` with every field set to zero.
        """
        return cls(
            taxable_income_ytd=_ZERO,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_ZERO,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
        )


@dataclass(frozen=True)
class ContributiveState:
    """Contributive year-to-date accumulators for INPS, INAIL, and TFR.

    Attributes:
        gross_ytd: Total gross earnings posted to CASH_EARNINGS ledger YTD.
        inps_employee_ytd: Employee INPS contributions withheld YTD.
        inps_employer_ytd: Employer INPS contributions accrued YTD.
        inail_employer_ytd: Employer INAIL contributions accrued YTD.
        tfr_ytd: TFR quota accrued YTD (posted to TFR_ACCRUAL ledger).
    """

    gross_ytd: Decimal
    inps_employee_ytd: Decimal
    inps_employer_ytd: Decimal
    inail_employer_ytd: Decimal
    tfr_ytd: Decimal

    @classmethod
    def zero(cls) -> ContributiveState:
        """Return a zero-valued ContributiveState for the start of a tax year.

        Returns:
            A :class:`ContributiveState` with every field set to zero.
        """
        return cls(
            gross_ytd=_ZERO,
            inps_employee_ytd=_ZERO,
            inps_employer_ytd=_ZERO,
            inail_employer_ytd=_ZERO,
            tfr_ytd=_ZERO,
        )


@dataclass(frozen=True)
class LeaveState:
    """Leave and sickness year-to-date counters.

    Attributes:
        leave_accrued_days_ytd: Leave days accrued YTD.
        leave_taken_days_ytd: Leave days taken YTD.
        sick_days_ytd: Calendar days of sickness absence YTD.
    """

    leave_accrued_days_ytd: Decimal
    leave_taken_days_ytd: Decimal
    sick_days_ytd: Decimal

    @classmethod
    def zero(cls) -> LeaveState:
        """Return a zero-valued LeaveState for the start of a tax year.

        Returns:
            A :class:`LeaveState` with every field set to zero.
        """
        return cls(
            leave_accrued_days_ytd=_ZERO,
            leave_taken_days_ytd=_ZERO,
            sick_days_ytd=_ZERO,
        )


@dataclass(frozen=True)
class PayrollState:
    """Single YTD-state container for the period-first payroll engine.

    Groups all year-to-date accumulators into typed sub-states and carries
    audit metadata.  Advance with
    :func:`~ccnl_engine.payroll.application.close_period.close`.

    Attributes:
        tax_year: The IRPEF tax year this state belongs to.
        periods_closed: Number of payroll periods already closed this year.
        revision_id: Deterministic identifier; ``"ytd-{year}-p{n:02d}"``.
        fiscal: Fiscal accumulators (IRPEF, surtax, credits).
        contributive: Contributive accumulators (INPS, INAIL, TFR, gross).
        leave: Leave and sickness day counters.
        source_period_ids: Ordered tuple of :class:`PeriodId` values for every
            period that has been accumulated into this state.
    """

    tax_year: int
    periods_closed: int
    revision_id: str
    fiscal: FiscalState
    contributive: ContributiveState
    leave: LeaveState
    source_period_ids: tuple[PeriodId, ...]

    @classmethod
    def zero(cls, tax_year: int) -> PayrollState:
        """Return the opening state for January of ``tax_year``.

        Returns:
            A :class:`PayrollState` with all accumulators at zero, no closed
            periods, and an empty ``source_period_ids`` tuple.
        """
        return cls(
            tax_year=tax_year,
            periods_closed=0,
            revision_id=f"ytd-{tax_year}-p00",
            fiscal=FiscalState.zero(),
            contributive=ContributiveState.zero(),
            leave=LeaveState.zero(),
            source_period_ids=(),
        )
