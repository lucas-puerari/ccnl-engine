"""Internal-only composite scenario type used by the pipeline.

:class:`_InternalScenario` is the private service-layer equivalent of the
removed public ``PayrollScenario``.  It merges :class:`AnnualEstimateInput`
structural fields with period-specific events from
:class:`~ccnl_engine.engine.payroll.domain.period_input.PeriodPayrollInput`
and is constructed exclusively by
:func:`~ccnl_engine.engine.payroll.service.pipeline._annual_to_scenario`.

Callers outside the service layer must use
:func:`~ccnl_engine.engine.payroll.service.orchestrator.estimate_annual` or
:func:`~ccnl_engine.engine.payroll.service.orchestrator.estimate_period_effects`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import BilateralFundInput
from ccnl_engine.engine.payroll.domain.employee import Employee
from ccnl_engine.engine.payroll.domain.employment import Employment
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.domain.tax_basis import AnnualizedAssumption, TaxPeriod
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)

__all__ = ["_InternalScenario"]


def _check_non_negative(name: str, value: Decimal | None) -> None:
    if value is not None and value < _ZERO:
        msg = f"{name} must be >= 0, got {value}"
        raise ValueError(msg)


class _InternalScenario(BaseModel):
    """Private composite scenario used by the computation pipeline.

    Built from :class:`AnnualEstimateInput` plus optional period events and
    override amounts by
    :func:`~ccnl_engine.engine.payroll.service.pipeline._annual_to_scenario`.
    Not part of the public API.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    employee: Employee
    employment: Employment
    tax_basis: Annotated[
        AnnualizedAssumption | TaxPeriod,
        Field(discriminator="type"),
    ] = AnnualizedAssumption()
    time_supplements: OvertimeHours | None = None
    absence_days: AbsenceDays | None = None
    leave_input: LeaveInput | None = None
    sick_input: SickInput | None = None
    fringe_benefit_input: FringeBenefitInput | None = None
    welfare_input: WelfareInput | None = None
    bonus_input: BonusInput | None = None
    family: FamilyComposition | None = None
    art15_deductions: Art15Deductions | None = None
    bilateral_funds: tuple[BilateralFundInput, ...] = ()
    extra_monthly_payments: int = Field(default=0, ge=0, le=2)
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
    def _validate_non_negative(self) -> _InternalScenario:
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
