"""All PayItem variants and the discriminated-union PayItem type."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.pay_item.selection.policies import CompetencePeriod, PolicyDecision
from ccnl_engine.pay_item.voce.models import VoceView

__all__ = [
    "AbsenceDeduction",
    "AbsenceIntegrationItem",
    "BaseSalaryEarning",
    "BonusEarning",
    "ContractRenewalArrears",
    "EmployeeWithholdingItem",
    "EmployerContributionItem",
    "ExtraMonthEarning",
    "FixedAllowanceEarning",
    "FringeBenefitItem",
    "HourlyPercentageEarning",
    "LeaveSettlementItem",
    "MaternityItem",
    "NightHolidayShiftEarning",
    "OneOffEarning",
    "OvertimeEarning",
    "PayItem",
    "ProductivityBonusEarning",
    "PublicTfrReduction",
    "RaccordoElementEarning",
    "SeniorityEarning",
    "SicknessInpsItem",
    "SicknessItem",
    "TaxCreditItem",
    "TaxRefundItem",
    "TerminationItem",
    "TfrAccrualItem",
    "TfrSettlementItem",
    "WelfareItem",
    "WorkInjuryItem",
]


class _PayItemBase(VoceView, BaseModel):
    """Common fields shared by all PayItem variants, with their voce."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    competence_period: CompetencePeriod
    payment_date: date
    quantity: Decimal = Field(ge=Decimal(0))
    amount: Decimal
    source: str = ""
    attributes: tuple[tuple[str, str], ...] = ()
    policy_decision: PolicyDecision | None = None


class BaseSalaryEarning(_PayItemBase):
    """Monthly base salary at the contracted CCNL table rate."""

    kind: Literal["base_salary_earning"] = "base_salary_earning"


class FixedAllowanceEarning(_PayItemBase):
    """Fixed monthly allowance (indennità fissa) from the CCNL."""

    kind: Literal["fixed_allowance_earning"] = "fixed_allowance_earning"
    allowance_code: str = ""


class SeniorityEarning(_PayItemBase):
    """Seniority increment (scatto di anzianità)."""

    kind: Literal["seniority_earning"] = "seniority_earning"
    seniority_count: int = 0


class OvertimeEarning(_PayItemBase):
    """Overtime supplement (straordinario / supplementare)."""

    kind: Literal["overtime_earning"] = "overtime_earning"
    hours: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class NightHolidayShiftEarning(_PayItemBase):
    """Night, holiday or shift supplement."""

    kind: Literal["night_holiday_shift_earning"] = "night_holiday_shift_earning"
    hours: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class BonusEarning(_PayItemBase):
    """One-time bonus payment (una tantum, gratifica, ecc.)."""

    kind: Literal["bonus_earning"] = "bonus_earning"


class ProductivityBonusEarning(_PayItemBase):
    """Productivity bonus (PdR — premio di risultato)."""

    kind: Literal["productivity_bonus_earning"] = "productivity_bonus_earning"


class ContractRenewalArrears(_PayItemBase):
    """Arrears from a CCNL contract renewal (arretrati contrattuali)."""

    kind: Literal["contract_renewal_arrears"] = "contract_renewal_arrears"


class OneOffEarning(_PayItemBase):
    """Any one-off payment not covered by a more specific variant."""

    kind: Literal["one_off_earning"] = "one_off_earning"


class ExtraMonthEarning(_PayItemBase):
    """Extra-month contractual payment: tredicesima (13) or quattordicesima (14)."""

    kind: Literal["extra_month_earning"] = "extra_month_earning"
    month_number: int = Field(ge=13, le=14)


class RaccordoElementEarning(_PayItemBase):
    """Elemento di Raccordo Contrattuale paid with the tredicesima."""

    kind: Literal["raccordo_element_earning"] = "raccordo_element_earning"


class HourlyPercentageEarning(_PayItemBase):
    """Percentage of the hourly elements on the ordinary hours worked.

    The riposi annui paid with the pay, or the ferie and gratifica
    natalizia the employer accrues with the Cassa Edile (CCNL edilizia,
    Art. 5 and 18): a gross earning of the worker either way.
    """

    kind: Literal["hourly_percentage_earning"] = "hourly_percentage_earning"


class PublicTfrReduction(_PayItemBase):
    """Reduction of the gross of a public employee under the TFR at INPS.

    DPCM 20 dicembre 1999 art. 1 c. 3: the gross is reduced by the 2.50%
    contribution the worker no longer pays; a negative amount.
    """

    kind: Literal["public_tfr_reduction"] = "public_tfr_reduction"


class FringeBenefitItem(_PayItemBase):
    """Non-cash fringe benefit (auto aziendale, polizza, ecc.).

    Attributes:
        threshold_annual: Annual exemption threshold applied to the worker
            (L. 207/2024 art. 1 c. 390: 1,000 EUR, 2,000 EUR with a
            declared fiscally dependent child).
        ytd_total: Fringe value of the tax year including this benefit.
        taxable_amount: Amount this benefit makes taxable for IRPEF and
            INPS.  Zero while ``ytd_total`` stays within the threshold.  On
            the benefit that crosses it the earlier exempt amounts of the
            year become taxable too, so it can exceed ``amount``.
    """

    kind: Literal["fringe_benefit_item"] = "fringe_benefit_item"
    threshold_annual: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    ytd_total: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    taxable_amount: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class StandbyEarning(_PayItemBase):
    """Standby pay (indennità di reperibilità) at the CCNL rates."""

    kind: Literal["standby_earning"] = "standby_earning"


class TravelAllowanceItem(_PayItemBase):
    """Travel allowance (indennità di trasferta), paid in cash.

    Attributes:
        exempt_amount: Part left out of the IRPEF and INPS bases (art. 51
            c. 5 TUIR): the days times the daily amount up to the cap.
        taxable_amount: Part above the cap, income for IRPEF and INPS.
    """

    kind: Literal["travel_allowance_item"] = "travel_allowance_item"
    exempt_amount: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    taxable_amount: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class WelfareItem(_PayItemBase):
    """Welfare / flexible benefit (buoni pasto, rimborsi welfare)."""

    kind: Literal["welfare_item"] = "welfare_item"


class AbsenceDeduction(_PayItemBase):
    """Deduction for unpaid absence days."""

    kind: Literal["absence_deduction"] = "absence_deduction"
    absence_days: Decimal = Field(ge=Decimal(0))


class LeaveSettlementItem(_PayItemBase):
    """Settlement or accrual of paid leave (ferie / permessi)."""

    kind: Literal["leave_settlement_item"] = "leave_settlement_item"


class SicknessItem(_PayItemBase):
    """Sick-pay integration or deduction (malattia)."""

    kind: Literal["sickness_item"] = "sickness_item"
    sick_days: Decimal = Field(ge=Decimal(0))


class SicknessInpsItem(_PayItemBase):
    """INPS sickness indemnity the employer advances (indennità di malattia)."""

    kind: Literal["sickness_inps_item"] = "sickness_inps_item"
    sick_days: Decimal = Field(ge=Decimal(0))


class MaternityItem(_PayItemBase):
    """Maternity leave indemnity (maternità INPS)."""

    kind: Literal["maternity_item"] = "maternity_item"
    absence_days: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class WorkInjuryItem(_PayItemBase):
    """Work-injury indemnity (infortunio INAIL)."""

    kind: Literal["work_injury_item"] = "work_injury_item"
    absence_days: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class AbsenceIntegrationItem(_PayItemBase):
    """Employer pay of an insured absence: the CCNL top-up, the waiting period."""

    kind: Literal["absence_integration_item"] = "absence_integration_item"
    absence_days: Decimal = Field(default=Decimal(0), ge=Decimal(0))


class EmployeeWithholdingItem(_PayItemBase):
    """Employee withholding (ritenuta personale a carico dipendente)."""

    kind: Literal["employee_withholding_item"] = "employee_withholding_item"


class EmployerContributionItem(_PayItemBase):
    """Employer social contribution entry (INPS, INAIL, fund)."""

    kind: Literal["employer_contribution_item"] = "employer_contribution_item"


class TerminationItem(_PayItemBase):
    """Termination payment (indennità di mancato preavviso, ecc.)."""

    kind: Literal["termination_item"] = "termination_item"


class TfrAccrualItem(_PayItemBase):
    """TFR accrual for the period (quota TFR maturata)."""

    kind: Literal["tfr_accrual_item"] = "tfr_accrual_item"


class TfrSettlementItem(_PayItemBase):
    """TFR settlement on contract end (liquidazione TFR)."""

    kind: Literal["tfr_settlement_item"] = "tfr_settlement_item"


class TaxCreditItem(_PayItemBase):
    """Tax credit applied to IRPEF (detrazione lavoro, familiare, ecc.)."""

    kind: Literal["tax_credit_item"] = "tax_credit_item"


class TaxRefundItem(_PayItemBase):
    """Tax returned to the worker by the conguaglio: IRPEF or surtax."""

    kind: Literal["tax_refund_item"] = "tax_refund_item"


PayItem = Annotated[
    BaseSalaryEarning
    | FixedAllowanceEarning
    | SeniorityEarning
    | OvertimeEarning
    | NightHolidayShiftEarning
    | BonusEarning
    | ProductivityBonusEarning
    | ContractRenewalArrears
    | OneOffEarning
    | ExtraMonthEarning
    | RaccordoElementEarning
    | HourlyPercentageEarning
    | PublicTfrReduction
    | FringeBenefitItem
    | StandbyEarning
    | TravelAllowanceItem
    | WelfareItem
    | AbsenceDeduction
    | LeaveSettlementItem
    | SicknessItem
    | SicknessInpsItem
    | MaternityItem
    | WorkInjuryItem
    | AbsenceIntegrationItem
    | EmployeeWithholdingItem
    | EmployerContributionItem
    | TerminationItem
    | TfrAccrualItem
    | TfrSettlementItem
    | TaxCreditItem
    | TaxRefundItem,
    Field(discriminator="kind"),
]
"""Discriminated union of all supported pay-item variants."""
