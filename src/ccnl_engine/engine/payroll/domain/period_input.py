"""Period-specific payroll input: PeriodPayrollInput."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)


def _check_non_negative(name: str, value: Decimal | None) -> None:
    if value is not None and value < _ZERO:
        msg = f"{name} must be >= 0, got {value}"
        raise ValueError(msg)


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
        prior_period_irpef_withheld: IRPEF already withheld in earlier periods
            of this fiscal year (YTD).  Used to compute the conguaglio.
            Must be >= 0. ``None`` means no prior withholding.
        maternity_inps_indemnity_annual: INPS maternity indemnity recovered
            from the employer's contribution liability.  Must be >= 0.
        workplace_injury_inail_indemnity_annual: INAIL workplace-injury
            indemnity recovered from the employer.  Must be >= 0.
        termination_residual_leave_payout_annual: Payout for residual leave at
            termination (treated as ordinary income).  Must be >= 0.
        termination_tfr_liquidation_annual: TFR liquidation at termination.
            Must be >= 0.
        contract_renewal_arrears_annual: Contract-renewal arrears (arretrati
            da rinnovo contrattuale).  Must be >= 0.
        una_tantum_annual: Una-tantum payment.  Must be >= 0.
        personal_withholdings_annual: Personal/voluntary withholdings applied
            by the employer (e.g. loan repayments).  Must be >= 0.
        additional_irpef_base_annual: Additional taxable income base subject to
            IRPEF (e.g. welfare taxable under Art. 51).  Must be >= 0.
        health_fund_employee_annual: Employee health-fund contribution.
            Must be >= 0.
        health_fund_employer_annual: Employer health-fund contribution.
            Must be >= 0.
        territorial_supplement_annual: Territorial supplement (superminimo
            territoriale).  Must be >= 0.
        company_supplement_annual: Company supplement (superminimo aziendale).
            Must be >= 0.
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
    prior_period_irpef_withheld: StrictDecimal | None = None
    maternity_inps_indemnity_annual: StrictDecimal | None = None
    workplace_injury_inail_indemnity_annual: StrictDecimal | None = None
    termination_residual_leave_payout_annual: StrictDecimal | None = None
    termination_tfr_liquidation_annual: StrictDecimal | None = None
    contract_renewal_arrears_annual: StrictDecimal | None = None
    una_tantum_annual: StrictDecimal | None = None
    personal_withholdings_annual: StrictDecimal | None = None
    additional_irpef_base_annual: StrictDecimal | None = None
    health_fund_employee_annual: StrictDecimal | None = None
    health_fund_employer_annual: StrictDecimal | None = None
    territorial_supplement_annual: StrictDecimal | None = None
    company_supplement_annual: StrictDecimal | None = None

    @model_validator(mode="after")
    def _validate_non_negative(self) -> PeriodPayrollInput:
        _check_non_negative(
            "prior_period_irpef_withheld", self.prior_period_irpef_withheld
        )
        _check_non_negative(
            "maternity_inps_indemnity_annual", self.maternity_inps_indemnity_annual
        )
        _check_non_negative(
            "workplace_injury_inail_indemnity_annual",
            self.workplace_injury_inail_indemnity_annual,
        )
        _check_non_negative(
            "termination_residual_leave_payout_annual",
            self.termination_residual_leave_payout_annual,
        )
        _check_non_negative(
            "termination_tfr_liquidation_annual",
            self.termination_tfr_liquidation_annual,
        )
        _check_non_negative(
            "contract_renewal_arrears_annual", self.contract_renewal_arrears_annual
        )
        _check_non_negative("una_tantum_annual", self.una_tantum_annual)
        _check_non_negative(
            "personal_withholdings_annual", self.personal_withholdings_annual
        )
        _check_non_negative(
            "additional_irpef_base_annual", self.additional_irpef_base_annual
        )
        _check_non_negative(
            "health_fund_employee_annual", self.health_fund_employee_annual
        )
        _check_non_negative(
            "health_fund_employer_annual", self.health_fund_employer_annual
        )
        _check_non_negative(
            "territorial_supplement_annual", self.territorial_supplement_annual
        )
        _check_non_negative("company_supplement_annual", self.company_supplement_annual)
        return self
