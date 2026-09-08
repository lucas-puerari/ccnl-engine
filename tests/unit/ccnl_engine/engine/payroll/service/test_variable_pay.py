"""Unit tests for the variable-pay service (fringe benefits, welfare, PdR)."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.payroll.domain.supplements import (
    BonusInput,
    FringeBenefitInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.service.variable_pay import (
    compute_bonus,
    compute_fringe_benefit,
    compute_welfare,
)
from ccnl_engine.engine.tax.domain.variable_pay import FringeBenefitRules, PdRRules

_ZERO = Decimal(0)
_D = Decimal


def _standard_fb_rules() -> FringeBenefitRules:
    """2026 fringe-benefit thresholds: €1.000 standard, €2.000 with children.

    Returns:
        A :class:`FringeBenefitRules` with the 2026 statutory thresholds.
    """
    return FringeBenefitRules(
        threshold_standard=_D("1000.00"),
        threshold_with_children=_D("2000.00"),
    )


def _standard_pdr_rules() -> PdRRules:
    """2026 PdR parameters: max €3.000, 10% flat tax, ceiling €80.000.

    Returns:
        A :class:`PdRRules` with the 2026 statutory PdR parameters.
    """
    return PdRRules(
        max_amount=_D("3000.00"),
        flat_tax_rate=_D("0.10"),
        income_ceiling=_D("80000.00"),
    )


class TestComputeFringeBenefit:
    """compute_fringe_benefit threshold logic."""

    def test_below_standard_threshold(self) -> None:
        """Amount below €1.000 threshold: taxable_annual is zero."""
        fb_annual, threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_D("800")),
            _standard_fb_rules(),
        )
        assert fb_annual == _D("800")
        assert threshold == _D("1000.00")
        assert taxable == _ZERO

    def test_above_standard_threshold(self) -> None:
        """Amount above €1.000 threshold: excess is taxable."""
        fb_annual, threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_D("1400")),
            _standard_fb_rules(),
        )
        assert fb_annual == _D("1400")
        assert threshold == _D("1000.00")
        assert taxable == _D("400.00")

    def test_exactly_at_standard_threshold(self) -> None:
        """Amount equal to threshold: taxable is zero."""
        _fb_annual, _threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_D("1000")),
            _standard_fb_rules(),
        )
        assert taxable == _ZERO

    def test_with_dependent_children_threshold(self) -> None:
        """With children flag: €2.000 threshold applies."""
        fb_annual, threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_D("1800"), has_dependent_children=True),
            _standard_fb_rules(),
        )
        assert fb_annual == _D("1800")
        assert threshold == _D("2000.00")
        assert taxable == _ZERO

    def test_with_children_above_threshold(self) -> None:
        """Amount above €2.000 threshold with children: excess is taxable."""
        _, threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_D("2500"), has_dependent_children=True),
            _standard_fb_rules(),
        )
        assert threshold == _D("2000.00")
        assert taxable == _D("500.00")

    def test_zero_amount(self) -> None:
        """Zero amount: all outputs are zero."""
        fb_annual, threshold, taxable = compute_fringe_benefit(
            FringeBenefitInput(annual_amount=_ZERO),
            _standard_fb_rules(),
        )
        assert fb_annual == _ZERO
        assert threshold == _D("1000.00")
        assert taxable == _ZERO


class TestComputeWelfare:
    """compute_welfare echoes the input amount unchanged."""

    def test_echoes_amount(self) -> None:
        """Welfare amount is echoed as-is."""
        result = compute_welfare(WelfareInput(annual_amount=_D("600")))
        assert result == _D("600")

    def test_zero_amount(self) -> None:
        """Zero welfare amount echoes zero."""
        result = compute_welfare(WelfareInput(annual_amount=_ZERO))
        assert result == _ZERO


class TestComputeBonus:
    """compute_bonus PdR flat tax and ordinary taxable amount logic."""

    def test_zero_bonus_returns_all_zero(self) -> None:
        """Zero bonus: all outputs are zero regardless of PdR eligibility."""
        warnings: list[str] = []
        annual, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_ZERO, eligible_for_pdr=True),
            _standard_pdr_rules(),
            gross_annual=_D("30000"),
            l3_warnings=warnings,
        )
        assert annual == _ZERO
        assert flat_tax == _ZERO
        assert ordinary == _ZERO
        assert warnings == []

    def test_not_pdr_eligible_all_ordinary(self) -> None:
        """Not PdR-eligible: entire bonus is ordinarily taxable."""
        warnings: list[str] = []
        annual, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_D("2000"), eligible_for_pdr=False),
            _standard_pdr_rules(),
            gross_annual=_D("30000"),
            l3_warnings=warnings,
        )
        assert annual == _D("2000")
        assert flat_tax == _ZERO
        assert ordinary == _D("2000")
        assert warnings == []

    def test_pdr_eligible_below_ceiling_below_max(self) -> None:
        """PdR eligible, income within ceiling, bonus within max amount.

        bonus=2000, flat_tax=2000*0.10=200, ordinary=0.
        """
        warnings: list[str] = []
        annual, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_D("2000"), eligible_for_pdr=True),
            _standard_pdr_rules(),
            gross_annual=_D("50000"),
            l3_warnings=warnings,
        )
        assert annual == _D("2000")
        assert flat_tax == _D("200.00")
        assert ordinary == _ZERO
        assert warnings == []

    def test_pdr_eligible_bonus_exceeds_max(self) -> None:
        """PdR eligible, bonus above €3.000 cap: excess is ordinarily taxable.

        bonus=4000, pdr_base=3000, flat_tax=300, ordinary=1000.
        """
        warnings: list[str] = []
        annual, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_D("4000"), eligible_for_pdr=True),
            _standard_pdr_rules(),
            gross_annual=_D("50000"),
            l3_warnings=warnings,
        )
        assert annual == _D("4000")
        assert flat_tax == _D("300.00")
        assert ordinary == _D("1000.00")
        assert warnings == []

    def test_pdr_eligible_income_above_ceiling_emits_warning(self) -> None:
        """PdR eligible but income > €80.000: warning emitted, all ordinary."""
        warnings: list[str] = []
        annual, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_D("2000"), eligible_for_pdr=True),
            _standard_pdr_rules(),
            gross_annual=_D("90000"),
            l3_warnings=warnings,
        )
        assert annual == _D("2000")
        assert flat_tax == _ZERO
        assert ordinary == _D("2000")
        assert len(warnings) == 1
        assert "income ceiling" in warnings[0]

    def test_pdr_eligible_income_exactly_at_ceiling(self) -> None:
        """Income exactly at €80.000 ceiling: PdR regime applies (not exceeded)."""
        warnings: list[str] = []
        _, flat_tax, ordinary = compute_bonus(
            BonusInput(annual_amount=_D("1000"), eligible_for_pdr=True),
            _standard_pdr_rules(),
            gross_annual=_D("80000"),
            l3_warnings=warnings,
        )
        assert flat_tax == _D("100.00")
        assert ordinary == _ZERO
        assert warnings == []
