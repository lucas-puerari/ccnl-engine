"""PayrollScenario and re-exports of split domain types.

Re-exports all public names from the split modules for backwards compatibility.

The two root entities:

- :class:`Employee` — who the worker is: classification level, seniority,
  working hours, fiscal residency, individual salary agreements.
- :class:`Employment` — the employment relationship: which CCNL applies,
  what contract type, who the employer is, and the reference date.

These compose into :class:`PayrollScenario`, the single argument to
:func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`.

Helper sub-objects:

- :class:`Jurisdiction` — region and municipality codes for surtax.
- :class:`Agreement` — individual RAL override or ad-personam supplement.
- :class:`Employer` — employer headcount and second-level allowances.
- :class:`AnnualizedAssumption` — full-year fiscal assumption for estimates.
- :class:`TaxPeriod` — actual work-period data for period payroll pro-rata.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.payroll.domain.annual_input import (
    AnnualEstimateInput as AnnualEstimateInput,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import BilateralFundInput
from ccnl_engine.engine.payroll.domain.employee import (
    Agreement as Agreement,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.employee import (
    Employee as Employee,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.employee import (
    Jurisdiction as Jurisdiction,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.employer import (
    Employer as Employer,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.employment import (
    Employment as Employment,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.period_input import (
    PeriodPayrollInput as PeriodPayrollInput,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.domain.tax_basis import (
    AnnualizedAssumption as AnnualizedAssumption,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.tax_basis import (
    TaxPeriod as TaxPeriod,  # noqa: PLC0414
)
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)


def _check_optional_non_negative(name: str, value: Decimal | None) -> None:
    if value is not None and value < _ZERO:
        msg = f"{name} must be >= 0, got {value}"
        raise ValueError(msg)


class PayrollScenario(BaseModel):
    """A complete payroll computation scenario.

    Composes the worker (:class:`Employee`) and the employment relationship
    (:class:`Employment`) into a single object. Pass it to
    :func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`::

        from datetime import date
        from decimal import Decimal

        result = compute(PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        ))

    Attributes:
        employee: Worker-side inputs.
        employment: Employment relationship inputs.
        time_supplements: Optional Layer 3 supplement hours for the pay
            period (overtime, night, holiday). ``None`` when not requested.
        absence_days: Optional Layer 3 absence data for the pay period
            (unpaid days absent). ``None`` when not requested.
        leave_input: Optional Layer 3 leave data for the pay period
            (ferie / permessi taken). ``None`` when not requested.
        sick_input: Optional Layer 3 sick leave data for the pay period
            (malattia ordinaria). ``None`` when not requested.
        fringe_benefit_input: Optional fringe-benefit data for the fiscal
            year (Art. 51 c. 3 TUIR). ``None`` when not requested.
        welfare_input: Optional welfare data for the fiscal year
            (Art. 51 c. 2 TUIR). ``None`` when not requested.
        bonus_input: Optional bonus / PdR data for the fiscal year.
            ``None`` when not requested.
        family: Optional family composition for Art. 12 TUIR deductions.
            When provided, the engine computes family deductions and
            subtracts them from ``irpef_net`` (reducing ``net_annual``).
            ``None`` means no family deductions are applied and
            ``FiscalSimplification.NO_DETRAZIONI_FAMILIARI`` is reported.
        art15_deductions: Optional Art. 15 TUIR oneri detraibili declared
            by the worker.  When provided, the engine computes the tax
            credit (19 % on eligible expenditure up to the statutory
            ceiling) and subtracts it from ``irpef_net`` (reducing
            ``net_annual``).  ``None`` means no mortgage deductions are
            applied and
            ``FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE`` is
            reported.
            ``FiscalSimplification.PARTIAL_DETRAZIONI_ART15`` is always
            reported: only mortgage interest is modelled.
            Art. 1 c. 3-4 L. 199/2025 sterilizzazione applies to Art. 15
            TUIR oneri detraibili al 19 % (lett. a, b, d, e; not lett. c
            spese sanitarie): for reddito complessivo > EUR 200 000 the
            credit is reduced by EUR 440. The resulting clawback is
            reported in
            ``AnnualEstimate.sterilizzazione_clawback_annual``.
        bilateral_funds: Scenario-level bilateral fund contributions (fondi
            bilaterali). Each entry is either a fixed monthly amount
            (:class:`~ccnl_engine.engine.payroll.domain.bilateral_funds\
.FlatMonthlyFund`) or a rate applied to an annual base
            (:class:`~ccnl_engine.engine.payroll.domain.bilateral_funds\
.RateFund`). The employee portion reduces ``net_annual``; the employer
            portion enters ``employer_cost_annual``. Both reductions are
            post-tax only — the engine does not model any pre-tax
            deductibility of the employee contribution.
            ``FiscalSimplification.NO_BILATERAL_FUNDS`` is reported when
            the tuple is empty.
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
    def _check_prior_irpef(self) -> PayrollScenario:
        _check_optional_non_negative(
            "prior_period_irpef_withheld", self.prior_period_irpef_withheld
        )
        _check_optional_non_negative(
            "maternity_inps_indemnity_annual", self.maternity_inps_indemnity_annual
        )
        _check_optional_non_negative(
            "workplace_injury_inail_indemnity_annual",
            self.workplace_injury_inail_indemnity_annual,
        )
        _check_optional_non_negative(
            "termination_residual_leave_payout_annual",
            self.termination_residual_leave_payout_annual,
        )
        _check_optional_non_negative(
            "termination_tfr_liquidation_annual",
            self.termination_tfr_liquidation_annual,
        )
        _check_optional_non_negative(
            "contract_renewal_arrears_annual", self.contract_renewal_arrears_annual
        )
        _check_optional_non_negative("una_tantum_annual", self.una_tantum_annual)
        _check_optional_non_negative(
            "personal_withholdings_annual", self.personal_withholdings_annual
        )
        _check_optional_non_negative(
            "additional_irpef_base_annual", self.additional_irpef_base_annual
        )
        _check_optional_non_negative(
            "health_fund_employee_annual", self.health_fund_employee_annual
        )
        _check_optional_non_negative(
            "health_fund_employer_annual", self.health_fund_employer_annual
        )
        _check_optional_non_negative(
            "territorial_supplement_annual", self.territorial_supplement_annual
        )
        _check_optional_non_negative(
            "company_supplement_annual", self.company_supplement_annual
        )
        return self
