"""Unit tests for item_producer and PayItemPolicy.resolve()."""

from __future__ import annotations

import dataclasses
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.item_producer import (
    POLICY_REGISTRY,
    _build_fiscal_items,
    _build_gross_items,
    _build_work_items,
    _resolve,
    build_pay_items,
)
from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ContributionTreatment,
    CostTreatment,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FringeBenefitItem,
    OvertimeEarning,
    PayItemPolicy,
    PolicyDecision,
    SeniorityEarning,
    TaxTreatment,
    TfrAccrualItem,
    TfrTreatment,
    WelfareItem,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay

_ZERO = Decimal(0)
_AS_OF = date(2026, 6, 1)
_PERIOD = CompetencePeriod(year=2026, month=6)
_PAYMENT = date(2026, 6, 30)
_YYMM = "2026_06"


def _zero_work(**overrides: object) -> WorkRulesPay:
    """Build a WorkRulesPay with all zero/false values and optional overrides.

    Returns:
        A :class:`WorkRulesPay` with all fields zeroed and overrides applied.
    """
    from ccnl_engine.engine.payroll.service.work_rules import (  # noqa: PLC0415
        WorkRulesPay,
    )

    base: dict[str, object] = {
        "base_monthly_full_time": _ZERO,
        "overtime_supp": _ZERO,
        "night_supp": _ZERO,
        "holiday_supp": _ZERO,
        "time_supplements_monthly": _ZERO,
        "time_supplements_annual_projection": _ZERO,
        "hourly_rate": _ZERO,
        "absence_deduction_monthly": _ZERO,
        "effective_gross_monthly": _ZERO,
        "leave_accrued_days_monthly": _ZERO,
        "leave_taken_days_monthly": _ZERO,
        "leave_balance_days": _ZERO,
        "sick_days_monthly": _ZERO,
        "sick_carenza_days_monthly": _ZERO,
        "sick_inps_indemnity_monthly": _ZERO,
        "sick_company_integration_monthly": _ZERO,
        "fringe_benefit_annual": _ZERO,
        "fringe_benefit_threshold_annual": _ZERO,
        "fringe_benefit_taxable_annual": _ZERO,
        "welfare_annual": _ZERO,
        "bonus_annual": _ZERO,
        "bonus_pdr_flat_tax_annual": _ZERO,
        "bonus_ordinary_taxable_annual": _ZERO,
        "bonus_pdr_missing_prior_year": False,
        "wr_overtime_supported": False,
        "wr_night_supported": False,
        "wr_holiday_supported": False,
        "wr_absence_present": False,
        "wr_leave_present": False,
        "wr_sickness_present": False,
        "supplement_trace": (),
        "warnings": (),
        "consumed_rulesets": {},
        "consumed_ruleset_ids": (),
        "consumed_verifications": {},
    }
    base.update(overrides)
    return WorkRulesPay(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Helpers: real pipeline objects for testing
# ---------------------------------------------------------------------------


def _make_pipeline_objects(
    *,
    level_code: str = "4",
    seniority_count: int | None = None,
    period_input: PeriodPayrollInput | None = None,
) -> tuple[GrossPay, WorkRulesPay, FiscalPay]:
    """Run the payroll pipeline and return (gross, work, fiscal).

    Returns:
        Tuple of (GrossPay, WorkRulesPay, FiscalPay) from the real pipeline.
    """
    from ccnl_engine.engine.payroll.service.fiscal import (  # noqa: PLC0415
        compute_fiscal,
    )
    from ccnl_engine.engine.payroll.service.gross import (  # noqa: PLC0415
        compute_gross,
    )
    from ccnl_engine.engine.payroll.service.pipeline import (  # noqa: PLC0415
        _annual_to_scenario,
    )
    from ccnl_engine.engine.payroll.service.work_rules import (  # noqa: PLC0415
        compute_work_rules,
    )
    from tests.unit.ccnl_engine.engine.payroll.service.builders import (  # noqa: PLC0415
        _RULES,
        _build_ccnl,
        _req,
    )

    req = _req(level_code=level_code, seniority_count=seniority_count)
    ccnl = _build_ccnl()
    scenario = _annual_to_scenario(req, period_input)
    gross = compute_gross(scenario, ccnl)
    work = compute_work_rules(scenario, ccnl, gross, 2026)
    fiscal = compute_fiscal(scenario, ccnl, _RULES, None, gross, 2026, work)
    return gross, work, fiscal


# ---------------------------------------------------------------------------
# PayItemPolicy.resolve() branches
# ---------------------------------------------------------------------------


class TestPayItemPolicyResolve:
    """PayItemPolicy.resolve() returns a PolicyDecision or None."""

    def _policy(
        self, kinds: tuple[str, ...], until: date | None = None
    ) -> PayItemPolicy:
        decision = PolicyDecision(
            policy_id="test",
            policy_version="1.0",
            effective_from=date(2020, 1, 1),
            effective_until=until,
            tax_treatment=TaxTreatment.ORDINARY,
            contribution_treatment=ContributionTreatment.INCLUDED,
            tfr_treatment=TfrTreatment.INCLUDED,
            cost_treatment=CostTreatment.EMPLOYEE_CASH,
            legal_basis="test",
        )
        return PayItemPolicy(
            policy_id="test",
            policy_version="1.0",
            applies_to_kinds=kinds,
            effective_from=date(2020, 1, 1),
            effective_until=until,
            default_decision=decision,
        )

    def test_kind_not_in_applies_to_returns_none(self) -> None:
        """Returns None when kind is not in applies_to_kinds."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("seniority_earning", date(2026, 6, 1))
        assert result is None

    def test_as_of_before_effective_from_returns_none(self) -> None:
        """Returns None when as_of is before effective_from."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("base_salary_earning", date(2019, 12, 31))
        assert result is None

    def test_as_of_after_effective_until_returns_none(self) -> None:
        """Returns None when as_of is after effective_until."""
        policy = self._policy(("base_salary_earning",), until=date(2025, 12, 31))
        result = policy.resolve("base_salary_earning", date(2026, 1, 1))
        assert result is None

    def test_valid_with_no_until_returns_decision(self) -> None:
        """Returns default_decision when effective_until is None and dates are valid."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None
        assert result.tax_treatment == TaxTreatment.ORDINARY

    def test_valid_within_period_returns_decision(self) -> None:
        """Returns default_decision when as_of is within the effective period."""
        policy = self._policy(("base_salary_earning",), until=date(2026, 12, 31))
        result = policy.resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None


# ---------------------------------------------------------------------------
# _resolve() — registry lookup
# ---------------------------------------------------------------------------


class TestResolveFunction:
    """_resolve() returns None for unknown kinds, PolicyDecision for known."""

    def test_unknown_kind_returns_none(self) -> None:
        """Returns None when kind is not in POLICY_REGISTRY."""
        result = _resolve("completely_unknown_kind", date(2026, 6, 1))
        assert result is None

    def test_known_kind_returns_decision(self) -> None:
        """Returns a PolicyDecision for a registered kind."""
        result = _resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None
        assert result.tax_treatment == TaxTreatment.ORDINARY

    def test_all_registered_kinds_resolve(self) -> None:
        """Every kind in POLICY_REGISTRY resolves to a decision."""
        for kind in POLICY_REGISTRY:
            assert _resolve(kind, date(2026, 6, 1)) is not None


# ---------------------------------------------------------------------------
# _build_gross_items() — per-component coverage
# ---------------------------------------------------------------------------


class TestBuildGrossItems:
    """_build_gross_items() produces items only for non-zero components."""

    def test_base_salary_zero_produces_no_item(self) -> None:
        """When chain.base is zero, no BaseSalaryEarning is produced."""
        from ccnl_engine.engine.payroll.service.types import (  # noqa: PLC0415
            MonthlyPayChain,
        )

        gross, _, _ = _make_pipeline_objects()
        zero_chain = MonthlyPayChain(base=_ZERO, seniority=_ZERO, allowances=())
        zero_gross = dataclasses.replace(gross, chain=zero_chain)
        items = _build_gross_items(zero_gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "base_salary_earning" not in kinds

    def test_base_salary_nonzero_produces_item(self) -> None:
        """When chain.base is non-zero, a BaseSalaryEarning is produced."""
        gross, _, _ = _make_pipeline_objects()
        items = _build_gross_items(gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "base_salary_earning" in kinds

    def test_seniority_zero_produces_no_item(self) -> None:
        """When chain.seniority is zero, no SeniorityEarning is produced."""
        gross, _, _ = _make_pipeline_objects()
        items = _build_gross_items(gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "seniority_earning" not in kinds

    def test_seniority_nonzero_produces_item(self) -> None:
        """When chain.seniority is non-zero, a SeniorityEarning is produced."""
        gross, _, _ = _make_pipeline_objects(seniority_count=3)
        items = _build_gross_items(gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "seniority_earning" in kinds

    def test_base_salary_item_has_policy_decision(self) -> None:
        """BaseSalaryEarning carries a PolicyDecision with ordinary tax treatment."""
        gross, _, _ = _make_pipeline_objects()
        items = _build_gross_items(gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        base_items = [i for i in items if isinstance(i, BaseSalaryEarning)]
        assert len(base_items) == 1
        assert base_items[0].policy_decision is not None
        assert base_items[0].policy_decision.tax_treatment == TaxTreatment.ORDINARY
        assert base_items[0].policy_decision.tfr_treatment == TfrTreatment.INCLUDED

    def test_seniority_item_treatment_axes(self) -> None:
        """SeniorityEarning has ORDINARY/INCLUDED/INCLUDED/EMPLOYEE_CASH treatment."""
        gross, _, _ = _make_pipeline_objects(seniority_count=3)
        items = _build_gross_items(gross, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        sen = next(i for i in items if isinstance(i, SeniorityEarning))
        dec = sen.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.ORDINARY
        assert dec.contribution_treatment == ContributionTreatment.INCLUDED
        assert dec.tfr_treatment == TfrTreatment.INCLUDED
        assert dec.cost_treatment == CostTreatment.EMPLOYEE_CASH


# ---------------------------------------------------------------------------
# _build_fiscal_items() — per-component coverage
# ---------------------------------------------------------------------------


class TestBuildFiscalItems:
    """_build_fiscal_items() produces items only for non-zero fiscal components."""

    def test_contract_renewal_arrears_nonzero_produces_item(self) -> None:
        """Non-zero contract_renewal_arrears_annual produces a ContractRenewalArrears.

        Ensures the fiscal branch for contract renewal arrears is covered.
        """
        _, _, fiscal = _make_pipeline_objects()
        nonzero_fiscal = dataclasses.replace(
            fiscal, contract_renewal_arrears_annual=Decimal("500.00")
        )
        items = _build_fiscal_items(nonzero_fiscal, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "contract_renewal_arrears" in kinds

    def test_tfr_zero_produces_no_item(self) -> None:
        """When tfr_annual is zero, no TfrAccrualItem is produced."""
        _, _, fiscal = _make_pipeline_objects()
        zero_tfr = dataclasses.replace(fiscal, tfr_annual=_ZERO)
        items = _build_fiscal_items(zero_tfr, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "tfr_accrual_item" not in kinds

    def test_inps_employee_zero_produces_no_item(self) -> None:
        """When inps_employee_annual is zero, no EmployeeWithholdingItem is produced."""
        _, _, fiscal = _make_pipeline_objects()
        zero_inps = dataclasses.replace(fiscal, inps_employee_annual=_ZERO)
        items = _build_fiscal_items(zero_inps, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        kinds = [i.kind for i in items]
        assert "employee_withholding_item" not in kinds

    def test_inps_employer_zero_produces_no_item(self) -> None:
        """When inps_employer_annual is zero, no INPS EmployerContributionItem emitted.

        Covers the zero-branch for INPS employer in _build_fiscal_items.
        """
        _, _, fiscal = _make_pipeline_objects()
        zero_inps_emp = dataclasses.replace(fiscal, inps_employer_annual=_ZERO)
        items = _build_fiscal_items(zero_inps_emp, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        inps_emp_items = [
            i
            for i in items
            if isinstance(i, EmployerContributionItem) and "inps_employer" in i.item_id
        ]
        assert len(inps_emp_items) == 0

    def test_tfr_item_treatment_axes(self) -> None:
        """TfrAccrualItem has SEPARATE/EXCLUDED/SPECIAL/ACCRUAL_ONLY treatment."""
        _, _, fiscal = _make_pipeline_objects()
        items = _build_fiscal_items(fiscal, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        tfr = next(i for i in items if isinstance(i, TfrAccrualItem))
        dec = tfr.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.SEPARATE
        assert dec.contribution_treatment == ContributionTreatment.EXCLUDED
        assert dec.tfr_treatment == TfrTreatment.SPECIAL
        assert dec.cost_treatment == CostTreatment.ACCRUAL_ONLY

    def test_employee_withholding_is_negative(self) -> None:
        """EmployeeWithholdingItem has a negative amount (deduction from net)."""
        _, _, fiscal = _make_pipeline_objects()
        items = _build_fiscal_items(fiscal, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        emp_wh = next(i for i in items if isinstance(i, EmployeeWithholdingItem))
        assert emp_wh.amount < _ZERO

    def test_employer_contribution_treatment_axes(self) -> None:
        """EmployerContributionItem has ORDINARY/EXCLUDED/EXCLUDED/EMPLOYER_COST."""
        _, _, fiscal = _make_pipeline_objects()
        items = _build_fiscal_items(fiscal, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        emp_c = next(i for i in items if isinstance(i, EmployerContributionItem))
        dec = emp_c.policy_decision
        assert dec is not None
        assert dec.contribution_treatment == ContributionTreatment.EXCLUDED
        assert dec.cost_treatment == CostTreatment.EMPLOYER_COST


# ---------------------------------------------------------------------------
# build_pay_items() — integration and treatment axes
# ---------------------------------------------------------------------------


class TestBuildPayItems:
    """build_pay_items() produces the expected set of items."""

    def test_default_scenario_has_base_salary(self) -> None:
        """Default scenario always yields a BaseSalaryEarning."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert any(isinstance(i, BaseSalaryEarning) for i in items)

    def test_default_scenario_has_tfr(self) -> None:
        """Default scenario always yields a TfrAccrualItem."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert any(isinstance(i, TfrAccrualItem) for i in items)

    def test_default_scenario_has_inps_employee(self) -> None:
        """Default scenario yields an EmployeeWithholdingItem (INPS employee)."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert any(isinstance(i, EmployeeWithholdingItem) for i in items)

    def test_default_scenario_has_inps_employer(self) -> None:
        """Default scenario yields an EmployerContributionItem (INPS employer)."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert any(isinstance(i, EmployerContributionItem) for i in items)

    def test_seniority_yields_seniority_item(self) -> None:
        """A scenario with seniority_count > 0 yields a SeniorityEarning."""
        gross, work, fiscal = _make_pipeline_objects(seniority_count=5)
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert any(isinstance(i, SeniorityEarning) for i in items)

    def test_overtime_yields_overtime_item(self) -> None:
        """A scenario with overtime yields an OvertimeEarning."""
        work = _zero_work(overtime_supp=Decimal("150.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        assert any(isinstance(i, OvertimeEarning) for i in items)

    def test_overtime_treatment_axes(self) -> None:
        """OvertimeEarning has ORDINARY/INCLUDED/EXCLUDED/EMPLOYEE_CASH treatment."""
        work = _zero_work(overtime_supp=Decimal("150.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        ot = next(i for i in items if isinstance(i, OvertimeEarning))
        dec = ot.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.ORDINARY
        assert dec.contribution_treatment == ContributionTreatment.INCLUDED
        assert dec.tfr_treatment == TfrTreatment.EXCLUDED
        assert dec.cost_treatment == CostTreatment.EMPLOYEE_CASH

    def test_absence_deduction_is_negative(self) -> None:
        """AbsenceDeduction has a negative amount."""
        work = _zero_work(absence_deduction_monthly=Decimal("200.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        abs_items = [i for i in items if isinstance(i, AbsenceDeduction)]
        assert len(abs_items) == 1
        assert abs_items[0].amount < _ZERO

    def test_bonus_yields_bonus_item(self) -> None:
        """A scenario with a bonus yields a BonusEarning."""
        work = _zero_work(bonus_annual=Decimal("2000.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        assert any(isinstance(i, BonusEarning) for i in items)

    def test_fringe_benefit_yields_fringe_item(self) -> None:
        """A scenario with fringe benefit yields a FringeBenefitItem."""
        work = _zero_work(fringe_benefit_taxable_annual=Decimal("600.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        assert any(isinstance(i, FringeBenefitItem) for i in items)

    def test_fringe_benefit_treatment_axes(self) -> None:
        """FringeBenefitItem has NON_CASH_TAXABLE/INCLUDED/EXCLUDED/EMPLOYER_COST."""
        work = _zero_work(fringe_benefit_taxable_annual=Decimal("600.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        fb = next(i for i in items if isinstance(i, FringeBenefitItem))
        dec = fb.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.NON_CASH_TAXABLE
        assert dec.contribution_treatment == ContributionTreatment.INCLUDED
        assert dec.tfr_treatment == TfrTreatment.EXCLUDED
        assert dec.cost_treatment == CostTreatment.EMPLOYER_COST

    def test_welfare_yields_welfare_item(self) -> None:
        """A scenario with welfare yields a WelfareItem."""
        work = _zero_work(welfare_annual=Decimal("500.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        assert any(isinstance(i, WelfareItem) for i in items)

    def test_welfare_treatment_axes(self) -> None:
        """WelfareItem has EXEMPT/EXCLUDED/EXCLUDED/EMPLOYER_COST treatment."""
        work = _zero_work(welfare_annual=Decimal("500.00"))
        items = _build_work_items(work, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        wf = next(i for i in items if isinstance(i, WelfareItem))
        dec = wf.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.EXEMPT
        assert dec.contribution_treatment == ContributionTreatment.EXCLUDED
        assert dec.cost_treatment == CostTreatment.EMPLOYER_COST

    def test_all_items_have_competence_period(self) -> None:
        """All produced items share the same competence period."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        for item in items:
            assert item.competence_period.year == _AS_OF.year
            assert item.competence_period.month == _AS_OF.month

    def test_payment_date_is_last_day_of_month(self) -> None:
        """Payment date is the last day of the competence month."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        for item in items:
            assert item.payment_date == date(2026, 6, 30)

    def test_returns_tuple(self) -> None:
        """build_pay_items() returns a tuple."""
        gross, work, fiscal = _make_pipeline_objects()
        items = build_pay_items(gross, work, fiscal, _AS_OF)
        assert isinstance(items, tuple)


# ---------------------------------------------------------------------------
# Calculation.pay_items — full pipeline integration
# ---------------------------------------------------------------------------


class TestCalculationPayItems:
    """Calculation.pay_items is populated by the pipeline."""

    def test_estimate_annual_populates_pay_items(self) -> None:
        """estimate_annual() produces a Calculation with non-empty pay_items."""
        from ccnl_engine.engine.payroll.domain.bundle import (  # noqa: PLC0415
            make_bundle,
        )
        from ccnl_engine.engine.payroll.service.orchestrator import (  # noqa: PLC0415
            estimate_annual,
        )
        from tests.unit.ccnl_engine.engine.payroll.service.builders import (  # noqa: PLC0415
            _RULES,
            _build_ccnl,
            _req,
        )

        bundle = make_bundle(_build_ccnl(), _RULES, None)
        calc = estimate_annual(_req(), bundle=bundle)
        assert len(calc.pay_items) > 0

    def test_pay_items_include_base_salary(self) -> None:
        """Calculation.pay_items always includes a BaseSalaryEarning."""
        from ccnl_engine.engine.payroll.domain.bundle import (  # noqa: PLC0415
            make_bundle,
        )
        from ccnl_engine.engine.payroll.service.orchestrator import (  # noqa: PLC0415
            estimate_annual,
        )
        from tests.unit.ccnl_engine.engine.payroll.service.builders import (  # noqa: PLC0415
            _RULES,
            _build_ccnl,
            _req,
        )

        bundle = make_bundle(_build_ccnl(), _RULES, None)
        calc = estimate_annual(_req(), bundle=bundle)
        assert any(isinstance(i, BaseSalaryEarning) for i in calc.pay_items)

    def test_pay_items_default_empty_tuple(self) -> None:
        """Calculation.pay_items defaults to an empty tuple when not set."""
        # Use Calculation.from_dict to create a calculation without pay_items
        from ccnl_engine.engine.payroll.domain.bundle import (  # noqa: PLC0415
            make_bundle,
        )
        from ccnl_engine.engine.payroll.domain.calculation import (  # noqa: PLC0415
            Calculation,
        )
        from ccnl_engine.engine.payroll.service.orchestrator import (  # noqa: PLC0415
            estimate_annual,
        )
        from tests.unit.ccnl_engine.engine.payroll.service.builders import (  # noqa: PLC0415
            _RULES,
            _build_ccnl,
            _req,
        )

        bundle = make_bundle(_build_ccnl(), _RULES, None)
        calc = estimate_annual(_req(), bundle=bundle)
        # Reconstruct from dict (serialisation omits pay_items → defaults to ())
        reconstructed = Calculation.from_dict(calc.to_dict())
        assert reconstructed.pay_items == ()
