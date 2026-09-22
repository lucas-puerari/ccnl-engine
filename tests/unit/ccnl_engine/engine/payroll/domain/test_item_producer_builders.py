"""Unit tests for _build_gross_items() and _build_fiscal_items()."""

from __future__ import annotations

import dataclasses
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.item_producer_fiscal import _build_fiscal_items
from ccnl_engine.engine.payroll.domain.item_producer_gross import _build_gross_items
from ccnl_engine.engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
    ContributionTreatment,
    CostTreatment,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    SeniorityEarning,
    TaxTreatment,
    TfrAccrualItem,
    TfrSettlementItem,
    TfrTreatment,
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


def _make_pipeline_objects(
    *,
    level_code: str = "4",
    seniority_count: int | None = None,
    period_input: PeriodPayrollInput | None = None,
) -> tuple[GrossPay, WorkRulesPay, FiscalPay]:
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

    def test_tfr_settlement_item_produced_from_termination(self) -> None:
        """Non-zero termination_tfr_liquidation_annual produces a TfrSettlementItem."""
        _, _, fiscal = _make_pipeline_objects()
        fiscal_with_settlement = dataclasses.replace(
            fiscal, termination_tfr_liquidation_annual=Decimal("5000.00")
        )
        items = _build_fiscal_items(
            fiscal_with_settlement, _PERIOD, _PAYMENT, _YYMM, _AS_OF
        )
        settlement = next((i for i in items if isinstance(i, TfrSettlementItem)), None)
        assert settlement is not None
        assert settlement.amount == Decimal("5000.00")

    def test_tfr_settlement_zero_produces_no_item(self) -> None:
        """Zero termination_tfr_liquidation_annual produces no TfrSettlementItem."""
        _, _, fiscal = _make_pipeline_objects()
        fiscal_zero = dataclasses.replace(
            fiscal, termination_tfr_liquidation_annual=_ZERO
        )
        items = _build_fiscal_items(fiscal_zero, _PERIOD, _PAYMENT, _YYMM, _AS_OF)
        assert not any(isinstance(i, TfrSettlementItem) for i in items)

    def test_tfr_settlement_treatment_axes(self) -> None:
        """TfrSettlementItem has SEPARATE/EXCLUDED/SPECIAL/EMPLOYEE_CASH treatment."""
        _, _, fiscal = _make_pipeline_objects()
        fiscal_with_settlement = dataclasses.replace(
            fiscal, termination_tfr_liquidation_annual=Decimal("5000.00")
        )
        items = _build_fiscal_items(
            fiscal_with_settlement, _PERIOD, _PAYMENT, _YYMM, _AS_OF
        )
        settlement = next(i for i in items if isinstance(i, TfrSettlementItem))
        dec = settlement.policy_decision
        assert dec is not None
        assert dec.tax_treatment == TaxTreatment.SEPARATE
        assert dec.contribution_treatment == ContributionTreatment.EXCLUDED
        assert dec.tfr_treatment == TfrTreatment.SPECIAL
        assert dec.cost_treatment == CostTreatment.EMPLOYEE_CASH

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
