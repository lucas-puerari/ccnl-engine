"""Unit tests for the PayItem discriminated union and policy types."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ContractRenewalArrears,
    ContributionTreatment,
    CostTreatment,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    ExtraMonthEarning,
    FixedAllowanceEarning,
    FringeBenefitItem,
    LeaveSettlementItem,
    MaternityItem,
    NightHolidayShiftEarning,
    OneOffEarning,
    OvertimeEarning,
    PayItem,
    PayItemPolicy,
    PolicyDecision,
    ProductivityBonusEarning,
    SeniorityEarning,
    SicknessItem,
    TaxCreditItem,
    TaxRefundItem,
    TaxTreatment,
    TerminationItem,
    TfrAccrualItem,
    TfrSettlementItem,
    TfrTreatment,
    WelfareItem,
    WorkInjuryItem,
)

_PERIOD = CompetencePeriod(year=2026, month=6)
_DATE = date(2026, 6, 30)
_D = Decimal

_PAY_ITEM_ADAPTER: TypeAdapter[PayItem] = TypeAdapter(PayItem)

_DECISION = PolicyDecision(
    policy_id="p1",
    policy_version="1.0",
    effective_from=date(2026, 1, 1),
    effective_until=None,
    tax_treatment=TaxTreatment.ORDINARY,
    contribution_treatment=ContributionTreatment.INCLUDED,
    tfr_treatment=TfrTreatment.INCLUDED,
    cost_treatment=CostTreatment.EMPLOYEE_CASH,
    legal_basis="Art. 51 TUIR",
)


def _item(kind: str, **extra: object) -> dict[str, object]:
    return {
        "kind": kind,
        "item_id": f"test-{kind}",
        "competence_period": {"year": 2026, "month": 6},
        "payment_date": "2026-06-30",
        "quantity": "1",
        "amount": "1000.00",
        **extra,
    }


def _base(kind: str = "x") -> Any:  # noqa: ANN401
    return {
        "item_id": f"id-{kind}",
        "competence_period": _PERIOD,
        "payment_date": _DATE,
        "quantity": _D(1),
        "amount": _D("1000.00"),
    }


# All 24 kind strings — used by parametrize tests below.
_ALL_KINDS: list[tuple[str, dict[str, object]]] = [
    ("base_salary_earning", {}),
    ("fixed_allowance_earning", {}),
    ("seniority_earning", {}),
    ("overtime_earning", {}),
    ("night_holiday_shift_earning", {}),
    ("bonus_earning", {}),
    ("productivity_bonus_earning", {}),
    ("contract_renewal_arrears", {}),
    ("one_off_earning", {}),
    ("extra_month_earning", {"month_number": 13}),
    ("fringe_benefit_item", {}),
    ("welfare_item", {}),
    ("absence_deduction", {"absence_days": "0"}),
    ("leave_settlement_item", {}),
    ("sickness_item", {"sick_days": "1"}),
    ("maternity_item", {}),
    ("work_injury_item", {}),
    ("employee_withholding_item", {}),
    ("employer_contribution_item", {}),
    ("termination_item", {}),
    ("tfr_accrual_item", {}),
    ("tfr_settlement_item", {}),
    ("tax_credit_item", {}),
    ("tax_refund_item", {}),
]


class TestCompetencePeriod:
    """CompetencePeriod validation."""

    def test_valid(self) -> None:
        """Valid month and year constructs successfully."""
        p = CompetencePeriod(year=2026, month=6)
        assert p.year == 2026
        assert p.month == 6

    def test_month_zero_raises(self) -> None:
        """Month 0 is invalid."""
        with pytest.raises(ValidationError):
            CompetencePeriod(year=2026, month=0)

    def test_month_thirteen_raises(self) -> None:
        """Month 13 is invalid."""
        with pytest.raises(ValidationError):
            CompetencePeriod(year=2026, month=13)


class TestTreatmentEnums:
    """Treatment enum values resolve to their string representations."""

    def test_tax_treatment_string_values(self) -> None:
        """TaxTreatment StrEnum values match their string literals."""
        assert TaxTreatment.ORDINARY.value == "ordinary"
        assert TaxTreatment.EXEMPT.value == "exempt"
        assert TaxTreatment.SUBSTITUTE.value == "substitute"
        assert TaxTreatment.SEPARATE.value == "separate"
        assert TaxTreatment.NON_CASH_TAXABLE.value == "non_cash_taxable"

    def test_contribution_treatment_string_values(self) -> None:
        """ContributionTreatment StrEnum values match their string literals."""
        assert ContributionTreatment.INCLUDED.value == "included"
        assert ContributionTreatment.EXCLUDED.value == "excluded"
        assert ContributionTreatment.CAPPED.value == "capped"
        assert ContributionTreatment.SPECIAL_BASE.value == "special_base"

    def test_tfr_treatment_string_values(self) -> None:
        """TfrTreatment StrEnum values match their string literals."""
        assert TfrTreatment.INCLUDED.value == "included"
        assert TfrTreatment.EXCLUDED.value == "excluded"
        assert TfrTreatment.SPECIAL.value == "special"

    def test_cost_treatment_string_values(self) -> None:
        """CostTreatment StrEnum values match their string literals."""
        assert CostTreatment.EMPLOYEE_CASH.value == "employee_cash"
        assert CostTreatment.EMPLOYER_COST.value == "employer_cost"
        assert CostTreatment.THIRD_PARTY_CASH.value == "third_party_cash"
        assert CostTreatment.ACCRUAL_ONLY.value == "accrual_only"


class TestPolicyDecision:
    """PolicyDecision construction and defaults."""

    def test_basic_construction(self) -> None:
        """PolicyDecision constructs with required fields."""
        assert _DECISION.policy_id == "p1"
        assert _DECISION.tax_treatment == TaxTreatment.ORDINARY
        assert _DECISION.eligibility == "eligible"

    def test_defaults(self) -> None:
        """input_facts defaults to empty tuple; eligibility defaults to eligible."""
        assert _DECISION.input_facts == ()
        assert _DECISION.effective_until is None


class TestPayItemPolicy:
    """PayItemPolicy construction."""

    def test_basic_construction(self) -> None:
        """PayItemPolicy constructs with required fields."""
        policy = PayItemPolicy(
            policy_id="base_salary_policy",
            policy_version="2026.1",
            applies_to_kinds=("base_salary_earning",),
            effective_from=date(2026, 1, 1),
            effective_until=None,
            default_decision=_DECISION,
        )
        assert policy.policy_id == "base_salary_policy"
        assert "base_salary_earning" in policy.applies_to_kinds


class TestPayItemVariantsSpecific:
    """Variant-specific field tests for select PayItem subclasses."""

    def test_fixed_allowance_code(self) -> None:
        """FixedAllowanceEarning stores the allowance_code field."""
        item = FixedAllowanceEarning(**_base(), allowance_code="INDENNITA_X")
        assert item.allowance_code == "INDENNITA_X"

    def test_seniority_count(self) -> None:
        """SeniorityEarning stores the seniority_count field."""
        item = SeniorityEarning(**_base(), seniority_count=3)
        assert item.seniority_count == 3

    def test_fringe_benefit_fields(self) -> None:
        """FringeBenefitItem stores threshold and taxable_amount."""
        item = FringeBenefitItem(
            **_base(),
            threshold_annual=_D("258.23"),
            taxable_amount=_D("100.00"),
        )
        assert item.threshold_annual == _D("258.23")
        assert item.taxable_amount == _D("100.00")

    def test_absence_days(self) -> None:
        """AbsenceDeduction stores the absence_days field."""
        item = AbsenceDeduction(**_base(), absence_days=_D(2))
        assert item.absence_days == _D(2)

    def test_sickness_days(self) -> None:
        """SicknessItem stores the sick_days field."""
        item = SicknessItem(**_base(), sick_days=_D(3))
        assert item.sick_days == _D(3)

    def test_attributes_stored(self) -> None:
        """Attributes tuple is preserved on construction."""
        item = BaseSalaryEarning(
            **_base(), attributes=(("ccnl_level", "4"), ("contract", "permanent"))
        )
        assert ("ccnl_level", "4") in item.attributes

    def test_source_stored(self) -> None:
        """Source field is preserved."""
        item = OvertimeEarning(**_base(), source="gross_computation")
        assert item.source == "gross_computation"

    def test_item_is_frozen(self) -> None:
        """PayItem instances are immutable (frozen Pydantic model)."""
        item = BaseSalaryEarning(**_base())
        with pytest.raises(ValidationError):
            item.amount = _D("999")  # type: ignore[misc]

    def test_quantity_negative_raises(self) -> None:
        """Quantity cannot be negative."""
        with pytest.raises(ValidationError, match="quantity"):
            _PAY_ITEM_ADAPTER.validate_python(
                _item("base_salary_earning", quantity="-1")
            )


class TestPayItemDiscriminatedUnion:
    """PayItem discriminated union dispatches on 'kind'."""

    def test_dispatches_to_base_salary(self) -> None:
        """kind='base_salary_earning' produces BaseSalaryEarning."""
        result = _PAY_ITEM_ADAPTER.validate_python(_item("base_salary_earning"))
        assert isinstance(result, BaseSalaryEarning)

    def test_dispatches_to_absence_deduction(self) -> None:
        """kind='absence_deduction' produces AbsenceDeduction."""
        result = _PAY_ITEM_ADAPTER.validate_python(
            _item("absence_deduction", absence_days="2")
        )
        assert isinstance(result, AbsenceDeduction)

    def test_unknown_kind_raises(self) -> None:
        """An unknown kind raises a ValidationError."""
        with pytest.raises(ValidationError):
            _PAY_ITEM_ADAPTER.validate_python(_item("unknown_kind"))

    @pytest.mark.parametrize(("kind_str", "extra"), _ALL_KINDS)
    def test_all_24_kinds_parse(self, kind_str: str, extra: dict[str, object]) -> None:
        """Every one of the 24 documented kinds can be parsed through the union."""
        parsed = _PAY_ITEM_ADAPTER.validate_python(_item(kind_str, **extra))
        assert parsed.kind == kind_str

    def test_all_24_kinds_count(self) -> None:
        """_ALL_KINDS contains exactly 24 entries."""
        assert len(_ALL_KINDS) == 24


class TestPayItemSpecificConstruction:
    """Direct construction of each PayItem variant confirms kind field."""

    @pytest.mark.parametrize(
        ("variant", "kind_str"),
        [
            (BaseSalaryEarning(**_base()), "base_salary_earning"),
            (FixedAllowanceEarning(**_base()), "fixed_allowance_earning"),
            (SeniorityEarning(**_base()), "seniority_earning"),
            (OvertimeEarning(**_base()), "overtime_earning"),
            (NightHolidayShiftEarning(**_base()), "night_holiday_shift_earning"),
            (BonusEarning(**_base()), "bonus_earning"),
            (ProductivityBonusEarning(**_base()), "productivity_bonus_earning"),
            (ContractRenewalArrears(**_base()), "contract_renewal_arrears"),
            (OneOffEarning(**_base()), "one_off_earning"),
            (ExtraMonthEarning(**_base(), month_number=13), "extra_month_earning"),
            (FringeBenefitItem(**_base()), "fringe_benefit_item"),
            (WelfareItem(**_base()), "welfare_item"),
            (AbsenceDeduction(**_base(), absence_days=_D(0)), "absence_deduction"),
            (LeaveSettlementItem(**_base()), "leave_settlement_item"),
            (SicknessItem(**_base(), sick_days=_D(1)), "sickness_item"),
            (MaternityItem(**_base()), "maternity_item"),
            (WorkInjuryItem(**_base()), "work_injury_item"),
            (EmployeeWithholdingItem(**_base()), "employee_withholding_item"),
            (EmployerContributionItem(**_base()), "employer_contribution_item"),
            (TerminationItem(**_base()), "termination_item"),
            (TfrAccrualItem(**_base()), "tfr_accrual_item"),
            (TfrSettlementItem(**_base()), "tfr_settlement_item"),
            (TaxCreditItem(**_base()), "tax_credit_item"),
            (TaxRefundItem(**_base()), "tax_refund_item"),
        ],
    )
    def test_kind_field(self, variant: object, kind_str: str) -> None:
        """Each variant's kind field matches its expected string literal."""
        assert variant.kind == kind_str  # type: ignore[attr-defined]


class TestExtraMonthEarning:
    """ExtraMonthEarning stores month_number and validates its range."""

    def test_tredicesima(self) -> None:
        """month_number=13 is accepted (tredicesima)."""
        item = ExtraMonthEarning(**_base(), month_number=13)
        assert item.month_number == 13
        assert item.kind == "extra_month_earning"

    def test_quattordicesima(self) -> None:
        """month_number=14 is accepted (quattordicesima)."""
        item = ExtraMonthEarning(**_base(), month_number=14)
        assert item.month_number == 14

    def test_month_number_below_13_raises(self) -> None:
        """month_number=12 is rejected."""
        from pydantic import ValidationError  # noqa: PLC0415

        with pytest.raises(ValidationError):
            ExtraMonthEarning(**_base(), month_number=12)

    def test_month_number_above_14_raises(self) -> None:
        """month_number=15 is rejected."""
        from pydantic import ValidationError  # noqa: PLC0415

        with pytest.raises(ValidationError):
            ExtraMonthEarning(**_base(), month_number=15)

    def test_amount_stored(self) -> None:
        """Amount is stored as provided."""
        item = ExtraMonthEarning(**_base(), month_number=13)
        assert item.amount == _D("1000.00")
