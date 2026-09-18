"""Tests for PayrollResult grouped property views."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    Permanent,
    estimate_annual,
)
from ccnl_engine.engine.payroll.domain.payroll_result import (
    PayrollEmployer,
    PayrollPay,
    PayrollQuality,
    PayrollResult,
    PayrollTax,
)


@pytest.fixture(scope="module")
def result() -> PayrollResult:
    """Return a PayrollResult for CCNL Commercio level 4, 2026, full-time.

    Returns:
        A :class:`PayrollResult` for testing the grouped property views.
    """
    return estimate_annual(
        AnnualPayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="commercio-confcommercio.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )
    ).result


class TestPayrollPay:
    """PayrollResult.pay returns a PayrollPay with employee pay amounts."""

    def test_type(self, result: PayrollResult) -> None:
        """``result.pay`` is a :class:`PayrollPay` instance."""
        assert isinstance(result.pay, PayrollPay)

    def test_gross_annual(self, result: PayrollResult) -> None:
        """``pay.gross_annual`` matches the parent result."""
        assert result.pay.gross_annual == result.gross_annual

    def test_net_annual(self, result: PayrollResult) -> None:
        """``pay.net_annual`` matches the parent result."""
        assert result.pay.net_annual == result.net_annual

    def test_net_monthly(self, result: PayrollResult) -> None:
        """``pay.net_monthly`` matches the parent result."""
        assert result.pay.net_monthly == result.net_monthly

    def test_seniority_count(self, result: PayrollResult) -> None:
        """``pay.seniority_count`` matches the parent result."""
        assert result.pay.seniority_count == result.seniority_count

    def test_inps_employee_annual(self, result: PayrollResult) -> None:
        """``pay.inps_employee_annual`` matches the parent result."""
        assert result.pay.inps_employee_annual == result.inps_employee_annual

    def test_l3_defaults_zero(self, result: PayrollResult) -> None:
        """L3 fields default to zero when not computed."""
        assert result.pay.absence_deduction_monthly == Decimal(0)
        assert result.pay.welfare_annual == Decimal(0)

    def test_frozen(self, result: PayrollResult) -> None:
        """``PayrollPay`` is immutable."""
        p = result.pay
        with pytest.raises(Exception, match="cannot assign"):
            p.net_annual = Decimal(0)  # type: ignore[misc]


class TestPayrollTax:
    """PayrollResult.tax returns a PayrollTax with IRPEF and deduction fields."""

    def test_type(self, result: PayrollResult) -> None:
        """``result.tax`` is a :class:`PayrollTax` instance."""
        assert isinstance(result.tax, PayrollTax)

    def test_taxable_income(self, result: PayrollResult) -> None:
        """``tax.taxable_income`` matches the parent result."""
        assert result.tax.taxable_income == result.taxable_income

    def test_irpef_net(self, result: PayrollResult) -> None:
        """``tax.irpef_net`` matches the parent result."""
        assert result.tax.irpef_net == result.irpef_net

    def test_fiscal_simplifications(self, result: PayrollResult) -> None:
        """``tax.fiscal_simplifications`` matches the parent result."""
        assert result.tax.fiscal_simplifications == result.fiscal_simplifications

    def test_employer_withholds_irpef(self, result: PayrollResult) -> None:
        """``tax.employer_withholds_irpef`` is ``True`` for standard contracts."""
        assert result.tax.employer_withholds_irpef is True

    def test_frozen(self, result: PayrollResult) -> None:
        """``PayrollTax`` is immutable."""
        t = result.tax
        with pytest.raises(Exception, match="cannot assign"):
            t.irpef_net = Decimal(0)  # type: ignore[misc]


class TestPayrollEmployer:
    """PayrollResult.employer returns a PayrollEmployer with employer costs."""

    def test_type(self, result: PayrollResult) -> None:
        """``result.employer`` is a :class:`PayrollEmployer` instance."""
        assert isinstance(result.employer, PayrollEmployer)

    def test_employer_cost_annual(self, result: PayrollResult) -> None:
        """``employer.employer_cost_annual`` matches the parent result."""
        assert result.employer.employer_cost_annual == result.employer_cost_annual

    def test_tfr_annual(self, result: PayrollResult) -> None:
        """``employer.tfr_annual`` matches the parent result."""
        assert result.employer.tfr_annual == result.tfr_annual

    def test_inps_employer_annual(self, result: PayrollResult) -> None:
        """``employer.inps_employer_annual`` matches the parent result."""
        assert result.employer.inps_employer_annual == result.inps_employer_annual

    def test_frozen(self, result: PayrollResult) -> None:
        """``PayrollEmployer`` is immutable."""
        e = result.employer
        with pytest.raises(Exception, match="cannot assign"):
            e.employer_cost_annual = Decimal(0)  # type: ignore[misc]


class TestPayrollQuality:
    """PayrollResult.quality returns a PayrollQuality with metadata."""

    def test_type(self, result: PayrollResult) -> None:
        """``result.quality`` is a :class:`PayrollQuality` instance."""
        assert isinstance(result.quality, PayrollQuality)

    def test_status(self, result: PayrollResult) -> None:
        """``quality.status`` matches the parent result."""
        assert result.quality.status == result.status

    def test_confidence(self, result: PayrollResult) -> None:
        """``quality.confidence`` matches the parent result."""
        assert result.quality.confidence == result.confidence

    def test_calculation_scope(self, result: PayrollResult) -> None:
        """``quality.calculation_scope`` matches the parent result."""
        assert result.quality.calculation_scope == result.calculation_scope

    def test_warnings(self, result: PayrollResult) -> None:
        """``quality.warnings`` matches the parent result."""
        assert result.quality.warnings == result.warnings

    def test_frozen(self, result: PayrollResult) -> None:
        """``PayrollQuality`` is immutable."""
        q = result.quality
        with pytest.raises(Exception, match="cannot assign"):
            q.status = "partial"  # type: ignore[misc]
