"""Period-specific payroll input: PeriodPayrollInput."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.domain.tax_basis import TaxPeriod


class PeriodPayrollInput(BaseModel):
    """Period-specific payroll events for a single pay period.

    Passed to :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` alongside an :class:`AnnualEstimateInput` to supply
    the month's variable events (overtime, absences, sick leave, benefits).

    All fields are optional — a ``PeriodPayrollInput()`` with no arguments represents
    a standard month with no special events.

    Attributes:
        tax_period: Work-period data for fiscal pro-rata.  Required when
            calling :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects`; the function raises
            :exc:`~ccnl_engine.engine.errors.InvalidInputError` when absent.
        time_supplements: Overtime, night, and holiday hours for the period.
            ``None`` means no supplement computation.
        absence_days: Unpaid absence days in the period. ``None`` means none.
        leave_input: Ferie/permessi days taken in the period. ``None`` means
            no leave tracking.
        sick_input: Sick-leave days in the period. ``None`` means no sickness.
        fringe_benefit_input: Annual fringe-benefit amount (Art. 51 c. 3
            TUIR). Reported per-period but compared against the annual
            threshold. ``None`` means no fringe computation.
        welfare_input: Annual welfare amount (Art. 51 c. 2 TUIR). ``None``
            means no welfare.
        bonus_input: Annual bonus / PdR data. ``None`` means no bonus.
        extra_monthly_payments: Number of additional monthly payments
            (mensilità aggiuntive) falling in this period.  Use ``1`` for a
            period that includes the tredicesima or the quattordicesima, and
            ``2`` when both fall in the same period.  Defaults to ``0`` for a
            standard month.  The caller is responsible for distributing the
            bonus months correctly across the twelve periods of the year.
        is_addizionali_settlement: When ``True``, this period is the addizionali
            settlement (saldo dicembre).  The engine withholds the remaining
            balance: ``annual_addizionale - addizionale_withheld_ytd`` from the
            opening :class:`~ccnl_engine.engine.payroll.domain.payroll_state\
.PayrollState`.  For standard months the addizionale is divided evenly
            over eleven installments.  Defaults to ``False``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tax_period: TaxPeriod | None = None
    time_supplements: OvertimeHours | None = None
    absence_days: AbsenceDays | None = None
    leave_input: LeaveInput | None = None
    sick_input: SickInput | None = None
    fringe_benefit_input: FringeBenefitInput | None = None
    welfare_input: WelfareInput | None = None
    bonus_input: BonusInput | None = None
    extra_monthly_payments: int = Field(default=0, ge=0, le=2)
    is_addizionali_settlement: bool = False
