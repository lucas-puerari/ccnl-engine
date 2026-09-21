"""Discriminated-union PayItem model and associated policy types.

Every pay item has a ``kind`` discriminator that identifies its variant.
Treatments (tax, contribution, TFR, cost) are described separately via
``PayItemPolicy`` and ``PolicyDecision`` so the nature of an item is
always decoupled from the rules that govern it.

Variants:
    BaseSalaryEarning, FixedAllowanceEarning, SeniorityEarning,
    OvertimeEarning, NightHolidayShiftEarning, BonusEarning,
    ProductivityBonusEarning, ContractRenewalArrears, OneOffEarning,
    FringeBenefitItem, WelfareItem, AbsenceDeduction, LeaveSettlementItem,
    SicknessItem, MaternityItem, WorkInjuryItem, EmployeeWithholdingItem,
    EmployerContributionItem, TerminationItem, TfrAccrualItem,
    TfrSettlementItem, TaxCreditItem, TaxRefundItem.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.payroll.domain.treatments import (
    ContributionTreatment,
    CostTreatment,
    TaxTreatment,
    TfrTreatment,
)

__all__ = [
    "CompetencePeriod",
    "ContributionTreatment",
    "CostTreatment",
    "PayItem",
    "PayItemPolicy",
    "PolicyDecision",
    "TaxTreatment",
    "TfrTreatment",
]


class CompetencePeriod(BaseModel):
    """The calendar month and year to which a pay item belongs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    month: int = Field(ge=1, le=12)


# ---------------------------------------------------------------------------
# PolicyDecision — explainable selection outcome
# ---------------------------------------------------------------------------


class PolicyDecision(BaseModel):
    """The outcome of applying a PayItemPolicy to one pay item.

    Captures which rules were selected, the legal basis, and the effective
    period so the result is auditable after the fact.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    policy_version: str
    effective_from: date
    effective_until: date | None
    tax_treatment: TaxTreatment
    contribution_treatment: ContributionTreatment
    tfr_treatment: TfrTreatment
    cost_treatment: CostTreatment
    legal_basis: str
    input_facts: tuple[str, ...] = ()
    eligibility: Literal["eligible", "not_eligible", "unknown"] = "eligible"


# ---------------------------------------------------------------------------
# PayItemPolicy — selects treatments for an item
# ---------------------------------------------------------------------------


class PayItemPolicy(BaseModel):
    """Binding from pay-item kind and context to a PolicyDecision.

    A policy is a static rule: given item kind, reference date, worker
    attributes and CCNL slug it returns the applicable PolicyDecision.
    The policy itself is immutable; different scenarios may resolve the
    same policy_id to different decisions (e.g. when thresholds change).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    policy_version: str
    applies_to_kinds: tuple[str, ...]
    effective_from: date
    effective_until: date | None
    default_decision: PolicyDecision

    def resolve(self, kind: str, as_of: date) -> PolicyDecision | None:
        """Return the PolicyDecision when *kind* and *as_of* are in scope.

        Returns:
            The :attr:`default_decision` when *kind* is in
            :attr:`applies_to_kinds` and *as_of* falls within the effective
            period; ``None`` otherwise.
        """
        if kind not in self.applies_to_kinds:
            return None
        if as_of < self.effective_from:
            return None
        if self.effective_until is not None and as_of > self.effective_until:
            return None
        return self.default_decision


# ---------------------------------------------------------------------------
# Shared base fields (not a Pydantic base — each variant is standalone)
# ---------------------------------------------------------------------------


class _PayItemBase(BaseModel):
    """Common fields shared by all PayItem variants."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    competence_period: CompetencePeriod
    payment_date: date
    quantity: Decimal = Field(ge=Decimal(0))
    amount: Decimal
    source: str = ""
    attributes: tuple[tuple[str, str], ...] = ()
    policy_decision: PolicyDecision | None = None


# ---------------------------------------------------------------------------
# 23 PayItem variants
# ---------------------------------------------------------------------------


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


class NightHolidayShiftEarning(_PayItemBase):
    """Night, holiday or shift supplement."""

    kind: Literal["night_holiday_shift_earning"] = "night_holiday_shift_earning"


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


class FringeBenefitItem(_PayItemBase):
    """Non-cash fringe benefit (auto aziendale, polizza, ecc.)."""

    kind: Literal["fringe_benefit_item"] = "fringe_benefit_item"
    threshold_annual: Decimal = Field(default=Decimal(0), ge=Decimal(0))
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


class MaternityItem(_PayItemBase):
    """Maternity leave indemnity (maternità INPS)."""

    kind: Literal["maternity_item"] = "maternity_item"


class WorkInjuryItem(_PayItemBase):
    """Work-injury indemnity (infortunio INAIL)."""

    kind: Literal["work_injury_item"] = "work_injury_item"


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
    """Conguaglio IRPEF credit returned to the worker."""

    kind: Literal["tax_refund_item"] = "tax_refund_item"


# ---------------------------------------------------------------------------
# Discriminated union
# ---------------------------------------------------------------------------

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
    | FringeBenefitItem
    | WelfareItem
    | AbsenceDeduction
    | LeaveSettlementItem
    | SicknessItem
    | MaternityItem
    | WorkInjuryItem
    | EmployeeWithholdingItem
    | EmployerContributionItem
    | TerminationItem
    | TfrAccrualItem
    | TfrSettlementItem
    | TaxCreditItem
    | TaxRefundItem,
    Field(discriminator="kind"),
]
"""Discriminated union of all supported pay-item variants.

Use this type annotation when a field or parameter accepts any pay item:

    items: tuple[PayItem, ...]
"""
