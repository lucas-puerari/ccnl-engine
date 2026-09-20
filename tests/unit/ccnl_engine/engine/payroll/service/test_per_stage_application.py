"""Per-stage application tests for the payroll computation pipeline.

Each test class exercises exactly one pipeline transition independently,
verifying only the input/output contract of that stage without end-to-end
coupling to the full orchestrator.

Stages:
  1. contract → fixed components  (compute_gross)
  2. events   → period earnings   (compute_work_rules)
  3. earnings → contributive bases (_inps_contributions)
  4. bases    → contributions     (_employer_funds, _compute_bilateral_funds)
  5. taxable  → taxes/deductions  (irpef chain, fiscal_deductions)
  6. sections → final result      (compute_fiscal net identity)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
from ccnl_engine.engine.payroll.domain.bilateral_funds import FlatMonthlyFund, RateFund
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Employee,
    Employer,
    Employment,
)
from ccnl_engine.engine.payroll.domain.supplements import FringeBenefitInput
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.contributions import inps_contribution
from ccnl_engine.engine.payroll.service.fiscal import compute_fiscal
from ccnl_engine.engine.payroll.service.fiscal_contributions import (
    _compute_bilateral_funds,
    _employer_funds,
    _inps_contributions,
)
from ccnl_engine.engine.payroll.service.gross import compute_gross
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.work_rules import compute_work_rules
from tests.helpers import make_minimal_ccnl, make_year_rules

_ZERO = Decimal(0)
_DATE = date(2026, 6, 1)
_CCNL_FILENAME = "test.json"
_PERMANENT = Permanent()


def _scenario(
    level_code: str = "4",
    contract: Permanent | FixedTerm | Apprentice = _PERMANENT,
    part_time_ratio: Decimal = Decimal(1),
    fringe_benefit_input: FringeBenefitInput | None = None,
) -> _InternalScenario:
    """Build a minimal _InternalScenario with test defaults.

    Returns:
        An _InternalScenario for use in stage-level tests.
    """
    return _InternalScenario(
        employee=Employee(
            level_code=level_code,
            part_time_ratio=part_time_ratio,
        ),
        employment=Employment(
            ccnl=_CCNL_FILENAME,
            contract=contract,
            employer=Employer(num_employees=50),
            as_of=_DATE,
        ),
        fringe_benefit_input=fringe_benefit_input,
    )


# ---------------------------------------------------------------------------
# Stage 1: contract → fixed components (compute_gross)
# ---------------------------------------------------------------------------


class TestStageGross:
    """compute_gross: contract + scenario → GrossPay output contract."""

    def test_base_salary_yields_expected_gross_monthly(self) -> None:
        """Level-4 salary 1000 with no seniority → gross_monthly=1000."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.gross_monthly == Decimal("1000.00")

    def test_gross_annual_equals_monthly_times_additional_months(self) -> None:
        """gross_annual = gross_monthly * additional_months (12 in test CCNL)."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.gross_annual == money(
            gross.gross_monthly * gross.additional_months
        )

    def test_part_time_50_scales_gross_monthly(self) -> None:
        """50% part-time worker: gross_monthly = full-time * 0.5."""
        ccnl = make_minimal_ccnl()
        full_gross = compute_gross(_scenario(level_code="4"), ccnl)
        pt_gross = compute_gross(
            _scenario(level_code="4", part_time_ratio=Decimal("0.5")), ccnl
        )
        assert pt_gross.gross_monthly == money(
            full_gross.gross_monthly * Decimal("0.5")
        )

    def test_part_time_50_scales_gross_annual(self) -> None:
        """50% part-time worker: gross_annual = full-time * 0.5."""
        ccnl = make_minimal_ccnl()
        full_gross = compute_gross(_scenario(level_code="4"), ccnl)
        pt_gross = compute_gross(
            _scenario(level_code="4", part_time_ratio=Decimal("0.5")), ccnl
        )
        assert pt_gross.gross_annual == money(full_gross.gross_annual * Decimal("0.5"))

    def test_contribution_base_does_not_exceed_gross_annual(self) -> None:
        """contribution_base <= gross_annual (no exclusions in test CCNL)."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.contribution_base <= gross.gross_annual

    def test_tfr_base_does_not_exceed_gross_annual(self) -> None:
        """tfr_base <= gross_annual (no exclusions in test CCNL)."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.tfr_base <= gross.gross_annual

    def test_lower_level_yields_lower_gross(self) -> None:
        """Level 2 (salary 600) gross < Level 4 (salary 1000) gross."""
        ccnl = make_minimal_ccnl()
        gross_l2 = compute_gross(_scenario(level_code="2"), ccnl)
        gross_l4 = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross_l2.gross_monthly < gross_l4.gross_monthly

    def test_hourly_divisor_is_positive(self) -> None:
        """hourly_divisor > 0 (168 in test CCNL)."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.hourly_divisor > _ZERO

    def test_additional_months_is_twelve(self) -> None:
        """Test CCNL has additional_months=12; gross propagates it."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(level_code="4"), ccnl)
        assert gross.additional_months == Decimal(12)


# ---------------------------------------------------------------------------
# Stage 2: events → period earnings (compute_work_rules)
# ---------------------------------------------------------------------------


class TestStageWorkRules:
    """compute_work_rules: scenario events → WorkRulesPay output contract."""

    def test_no_events_yields_zero_fringe_taxable(self) -> None:
        """No fringe_benefit_input → fringe_benefit_taxable_annual=0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.fringe_benefit_taxable_annual == _ZERO

    def test_no_events_yields_zero_bonus_taxable(self) -> None:
        """No bonus_input → bonus_ordinary_taxable_annual=0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.bonus_ordinary_taxable_annual == _ZERO

    def test_no_events_yields_zero_overtime(self) -> None:
        """No time_supplements → overtime_supp=0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.overtime_supp == _ZERO

    def test_no_events_yields_zero_absence_deduction(self) -> None:
        """No absence_days → absence_deduction_monthly=0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.absence_deduction_monthly == _ZERO

    def test_effective_gross_monthly_equals_gross_when_no_absence(self) -> None:
        """No absences: effective_gross_monthly = gross_monthly."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.effective_gross_monthly == gross.gross_monthly

    def test_fringe_above_threshold_enters_taxable_base(self) -> None:
        """Fringe > 1000 EUR threshold → fringe_benefit_taxable_annual > 0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario(
            fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal("2000.00"))
        )
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.fringe_benefit_taxable_annual > _ZERO

    def test_fringe_below_threshold_is_not_taxable(self) -> None:
        """Fringe <= 1000 EUR threshold → fringe_benefit_taxable_annual=0."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario(
            fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal("500.00"))
        )
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.fringe_benefit_taxable_annual == _ZERO

    def test_hourly_rate_derived_from_gross_and_divisor(self) -> None:
        """hourly_rate = money(gross_monthly / hourly_divisor)."""
        ccnl = make_minimal_ccnl()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        assert wr.hourly_rate == money(gross.gross_monthly / gross.hourly_divisor)


# ---------------------------------------------------------------------------
# Stage 3: earnings → contributive bases (_inps_contributions)
# ---------------------------------------------------------------------------


class TestStageInpsContributions:
    """_inps_contributions: contribution_base → (employee, employer, additional)."""

    def test_employee_is_positive_for_standard_base(self) -> None:
        """Employee INPS contribution > 0 for a non-zero base."""
        rules = make_year_rules()
        emp, _er, _add = _inps_contributions(
            rules,
            Permanent(),
            Decimal("1000.00"),
            Decimal("12000.00"),
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        assert emp > _ZERO

    def test_employer_is_positive_for_standard_base(self) -> None:
        """Employer INPS contribution > 0 for a non-zero base."""
        rules = make_year_rules()
        _emp, er, _add = _inps_contributions(
            rules,
            Permanent(),
            Decimal("1000.00"),
            Decimal("12000.00"),
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        assert er > _ZERO

    def test_employer_rate_exceeds_employee_rate(self) -> None:
        """Employer contribution > employee contribution (employer pays more)."""
        rules = make_year_rules()
        emp, er, _add = _inps_contributions(
            rules,
            Permanent(),
            Decimal("1000.00"),
            Decimal("12000.00"),
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        assert er > emp

    def test_fixed_term_employer_exceeds_permanent_employer(self) -> None:
        """Fixed-term employer INPS > permanent employer INPS (NASpI addizionale)."""
        rules = make_year_rules()
        base = Decimal("12000.00")
        gross_monthly = Decimal("1000.00")
        _emp_p, er_perm, _ = _inps_contributions(
            rules,
            Permanent(),
            gross_monthly,
            base,
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        _emp_ft, er_ft, _ = _inps_contributions(
            rules,
            FixedTerm(),
            gross_monthly,
            base,
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        assert er_ft > er_perm

    def test_zero_base_yields_zero_contributions(self) -> None:
        """Zero contribution_base → all three contributions are zero."""
        rules = make_year_rules()
        emp, er, add = _inps_contributions(
            rules,
            Permanent(),
            _ZERO,
            _ZERO,
            None,
            weekly_hours=None,
            ivs_ceiling_applies=False,
        )
        assert emp == er == add == _ZERO

    def test_inps_contribution_ceiling_caps_ivs_portion(self) -> None:
        """With IVS ceiling, inps_contribution caps the IVS portion of the base."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": "120000.00",
            },
            apprentice={
                "employee_rate": "0.0584",
                "employee_ivs_rate": "0.0584",
                "employer_rate_months_0_11": "0.0311",
                "employer_ivs_rate_months_0_11": "0.0150",
                "employer_rate_months_12_23": "0.0461",
                "employer_ivs_rate_months_12_23": "0.0300",
                "employer_rate_after": "0.1161",
                "employer_ivs_rate_after": "0.1000",
            },
        )
        # Base below ceiling: same result regardless of ivs_ceiling_applies
        base_below = Decimal("50000.00")
        r_uncapped = inps_contribution(
            base_below,
            rules.inps.employee_rate,  # type: ignore[union-attr]
            rules.inps.employee_ivs_rate,  # type: ignore[union-attr]
            rules,
            ivs_ceiling_applies=False,
        )
        r_capped = inps_contribution(
            base_below,
            rules.inps.employee_rate,  # type: ignore[union-attr]
            rules.inps.employee_ivs_rate,  # type: ignore[union-attr]
            rules,
            ivs_ceiling_applies=True,
        )
        assert r_uncapped == r_capped

        # Base above ceiling: capped result < uncapped
        base_above = Decimal("200000.00")
        r_uncapped_above = inps_contribution(
            base_above,
            rules.inps.employee_rate,  # type: ignore[union-attr]
            rules.inps.employee_ivs_rate,  # type: ignore[union-attr]
            rules,
            ivs_ceiling_applies=False,
        )
        r_capped_above = inps_contribution(
            base_above,
            rules.inps.employee_rate,  # type: ignore[union-attr]
            rules.inps.employee_ivs_rate,  # type: ignore[union-attr]
            rules,
            ivs_ceiling_applies=True,
        )
        assert r_capped_above < r_uncapped_above


# ---------------------------------------------------------------------------
# Stage 4: bases → contributions (_employer_funds, _compute_bilateral_funds)
# ---------------------------------------------------------------------------


class TestStageEmployerFunds:
    """_employer_funds: no employer funds in test CCNL → zero."""

    def test_no_employer_funds_yields_zero(self) -> None:
        """Test CCNL has no employer_funds → _employer_funds returns 0."""
        ccnl = make_minimal_ccnl()
        result = _employer_funds(ccnl, None, Decimal("12000.00"), _DATE)
        assert result == _ZERO


class TestStageBilateralFunds:
    """_compute_bilateral_funds: flat/rate fund accounting."""

    def test_empty_funds_yields_zero_employee_and_employer(self) -> None:
        """No bilateral funds → (0, 0)."""
        emp, er = _compute_bilateral_funds((), Decimal("12000.00"), Decimal("12000.00"))
        assert emp == _ZERO
        assert er == _ZERO

    def test_flat_monthly_fund_annualises_correctly(self) -> None:
        """FlatMonthlyFund(employee=10, employer=20) → (120, 240) annual."""
        fund = FlatMonthlyFund(
            employee_monthly=Decimal("10.00"),
            employer_monthly=Decimal("20.00"),
        )
        emp, er = _compute_bilateral_funds(
            (fund,), Decimal("12000.00"), Decimal("12000.00")
        )
        assert emp == Decimal("120.00")
        assert er == Decimal("240.00")

    def test_rate_fund_on_gross_annual_base(self) -> None:
        """RateFund(base=gross, emp_rate=0.01, er_rate=0.02) on 12000 → (120, 240)."""
        fund = RateFund(
            base="gross_annual",
            employee_rate=Decimal("0.01"),
            employer_rate=Decimal("0.02"),
        )
        emp, er = _compute_bilateral_funds(
            (fund,), Decimal("11000.00"), Decimal("12000.00")
        )
        assert emp == Decimal("120.00")
        assert er == Decimal("240.00")

    def test_employee_and_employer_fund_amounts_are_independent(self) -> None:
        """Employee and employer amounts are computed independently (not linked)."""
        fund = FlatMonthlyFund(
            employee_monthly=Decimal("5.00"),
            employer_monthly=Decimal("50.00"),
        )
        emp, er = _compute_bilateral_funds(
            (fund,), Decimal("12000.00"), Decimal("12000.00")
        )
        assert emp == Decimal("60.00")
        assert er == Decimal("600.00")


# ---------------------------------------------------------------------------
# Stage 5: taxable → taxes/deductions (irpef chain)
# ---------------------------------------------------------------------------


class TestStageTaxes:
    """irpef chain: taxable_income → irpef_gross → net taxes after deductions."""

    def test_irpef_gross_increases_with_taxable_income(self) -> None:
        """irpef_gross(30000) > irpef_gross(20000): higher income means higher tax."""
        rules = make_year_rules()
        assert _irpef.irpef_gross(Decimal(30000), rules) > _irpef.irpef_gross(
            Decimal(20000), rules
        )

    def test_work_deduction_reduces_irpef_below_gross(self) -> None:
        """irpef_gross - work_income_deduction < irpef_gross for typical incomes."""
        rules = make_year_rules()
        rc = Decimal(25000)
        gross = _irpef.irpef_gross(rc, rules)
        ded = _irpef.work_income_deduction(rc)
        assert ded > _ZERO
        assert gross - ded < gross

    def test_zero_taxable_income_yields_zero_irpef(self) -> None:
        """irpef_gross(0) = 0."""
        rules = make_year_rules()
        assert _irpef.irpef_gross(_ZERO, rules) == _ZERO

    def test_irpef_net_cannot_be_negative(self) -> None:
        """irpef_net >= 0: deductions cannot produce a negative tax liability."""
        rules = make_year_rules()
        # Very low income where deduction exceeds gross tax
        rc = Decimal("5000.00")
        gross = _irpef.irpef_gross(rc, rules)
        ded = _irpef.work_income_deduction(rc)
        net = max(_ZERO, gross - ded)
        assert net >= _ZERO


# ---------------------------------------------------------------------------
# Stage 6: sections → final result (compute_fiscal net identity)
# ---------------------------------------------------------------------------


class TestStageFiscalNetIdentity:
    """compute_fiscal: net_annual satisfies the accounting identity."""

    @pytest.fixture
    def fiscal_result(self) -> object:
        """Build a minimal FiscalPay via compute_fiscal.

        Returns:
            A FiscalPay instance for a permanent, standard scenario.
        """
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        scenario = _scenario()
        gross = compute_gross(scenario, ccnl)
        wr = compute_work_rules(scenario, ccnl, gross, year=2026)
        return compute_fiscal(scenario, ccnl, rules, None, gross, 2026, wr)

    def test_net_annual_is_positive(self, fiscal_result: object) -> None:
        """net_annual > 0 for a standard scenario."""
        assert fiscal_result.net_annual > _ZERO  # type: ignore[attr-defined]

    def test_net_monthly_equals_annual_divided_by_additional_months(
        self, fiscal_result: object
    ) -> None:
        """net_monthly = money(net_annual / additional_months) for 12-month CCNL."""
        assert fiscal_result.net_monthly == money(  # type: ignore[attr-defined]
            fiscal_result.net_annual / Decimal(12)  # type: ignore[attr-defined]
        )

    def test_employer_cost_exceeds_gross_annual(self, fiscal_result: object) -> None:
        """employer_cost_annual > gross_annual: employer also pays INPS and TFR."""
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(), ccnl)
        assert (
            fiscal_result.employer_cost_annual  # type: ignore[attr-defined]
            > gross.gross_annual
        )

    def test_net_annual_accounting_identity(self, fiscal_result: object) -> None:
        """Net = gross - inps_emp - irpef_net - addizionali + ti + somma_esente."""
        fp = fiscal_result
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(), ccnl)
        recomputed = money(
            gross.gross_annual
            - fp.inps_employee_annual  # type: ignore[attr-defined]
            - fp.irpef_net  # type: ignore[attr-defined]
            - fp.addizionale_regionale  # type: ignore[attr-defined]
            - fp.addizionale_comunale  # type: ignore[attr-defined]
            + fp.trattamento_integrativo  # type: ignore[attr-defined]
            + fp.somma_esente  # type: ignore[attr-defined]
        )
        assert fp.net_annual == recomputed  # type: ignore[attr-defined]

    def test_employer_cost_identity(self, fiscal_result: object) -> None:
        """Employer cost = gross + inps_employer + employer_funds + tfr + bilateral."""
        fp = fiscal_result
        ccnl = make_minimal_ccnl()
        gross = compute_gross(_scenario(), ccnl)
        expected = money(
            gross.gross_annual
            + fp.inps_employer_annual  # type: ignore[attr-defined]
            + fp.employer_funds_annual  # type: ignore[attr-defined]
            + fp.bilateral_employer_annual  # type: ignore[attr-defined]
            + fp.tfr_annual  # type: ignore[attr-defined]
        )
        assert fp.employer_cost_annual == expected  # type: ignore[attr-defined]

    def test_irpef_gross_not_negative(self, fiscal_result: object) -> None:
        """irpef_gross >= 0 in all scenarios."""
        assert (
            fiscal_result.irpef_gross >= _ZERO  # type: ignore[attr-defined]
        )

    def test_inps_employee_not_negative(self, fiscal_result: object) -> None:
        """inps_employee_annual >= 0."""
        assert (
            fiscal_result.inps_employee_annual >= _ZERO  # type: ignore[attr-defined]
        )
