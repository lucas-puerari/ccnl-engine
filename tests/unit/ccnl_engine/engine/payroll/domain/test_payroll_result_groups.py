"""Tests for AnnualEstimate and PeriodPayroll sub-object views."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Contributions,
    Coverage,
    Earnings,
    EmployerCost,
    Taxes,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual


@pytest.fixture(scope="module")
def result() -> AnnualEstimate:
    """Return an AnnualEstimate for CCNL Commercio level 4, 2026, full-time.

    Returns:
        An :class:`AnnualEstimate` for the nominal test scenario.
    """
    return estimate_annual(
        AnnualEstimateInput(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="commercio-confcommercio.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )
    ).result


class TestEarnings:
    """AnnualEstimate.earnings contains employee gross pay amounts."""

    def test_type(self, result: AnnualEstimate) -> None:
        """``result.earnings`` is an :class:`Earnings` instance."""
        assert isinstance(result.earnings, Earnings)

    def test_gross_annual_positive(self, result: AnnualEstimate) -> None:
        """``earnings.gross_annual`` is positive."""
        assert result.earnings.gross_annual > Decimal(0)

    def test_gross_monthly_positive(self, result: AnnualEstimate) -> None:
        """``earnings.gross_monthly`` is positive."""
        assert result.earnings.gross_monthly > Decimal(0)

    def test_seniority_count_zero_for_new_hire(self, result: AnnualEstimate) -> None:
        """Seniority count is zero at start of employment."""
        assert result.earnings.seniority_count == 0

    def test_apprenticeship_pct_none_for_permanent(
        self, result: AnnualEstimate
    ) -> None:
        """apprenticeship_pct is None for a permanent employee."""
        assert result.earnings.apprenticeship_pct is None

    def test_frozen(self, result: AnnualEstimate) -> None:
        """``Earnings`` is immutable."""
        with pytest.raises(Exception, match="cannot assign"):
            result.earnings.gross_annual = Decimal(0)  # type: ignore[misc]


class TestContributions:
    """AnnualEstimate.contributions contains social contribution amounts."""

    def test_type(self, result: AnnualEstimate) -> None:
        """``result.contributions`` is a :class:`Contributions` instance."""
        assert isinstance(result.contributions, Contributions)

    def test_inps_employee_annual_positive(self, result: AnnualEstimate) -> None:
        """``contributions.inps_employee_annual`` is positive."""
        assert result.contributions.inps_employee_annual > Decimal(0)

    def test_inps_employer_annual_positive(self, result: AnnualEstimate) -> None:
        """``contributions.inps_employer_annual`` is positive."""
        assert result.contributions.inps_employer_annual > Decimal(0)

    def test_tfr_annual_positive(self, result: AnnualEstimate) -> None:
        """``contributions.tfr_annual`` is positive."""
        assert result.contributions.tfr_annual > Decimal(0)

    def test_frozen(self, result: AnnualEstimate) -> None:
        """``Contributions`` is immutable."""
        with pytest.raises(Exception, match="cannot assign"):
            result.contributions.inps_employee_annual = Decimal(0)  # type: ignore[misc]


class TestTaxes:
    """AnnualEstimate.taxes contains IRPEF and deduction fields."""

    def test_type(self, result: AnnualEstimate) -> None:
        """``result.taxes`` is a :class:`Taxes` instance."""
        assert isinstance(result.taxes, Taxes)

    def test_taxable_income_positive(self, result: AnnualEstimate) -> None:
        """``taxes.taxable_income`` is positive."""
        assert result.taxes.taxable_income > Decimal(0)

    def test_irpef_net_positive(self, result: AnnualEstimate) -> None:
        """``taxes.irpef_net`` is positive."""
        assert result.taxes.irpef_net > Decimal(0)

    def test_employer_withholds_irpef_true(self, result: AnnualEstimate) -> None:
        """``taxes.employer_withholds_irpef`` is True for standard contracts."""
        assert result.taxes.employer_withholds_irpef is True

    def test_fiscal_simplifications_frozenset(self, result: AnnualEstimate) -> None:
        """``taxes.fiscal_simplifications`` is a frozenset."""
        assert isinstance(result.taxes.fiscal_simplifications, frozenset)

    def test_frozen(self, result: AnnualEstimate) -> None:
        """``Taxes`` is immutable."""
        with pytest.raises(Exception, match="cannot assign"):
            result.taxes.irpef_net = Decimal(0)  # type: ignore[misc]


class TestEmployerCost:
    """AnnualEstimate.employer_cost contains employer cost amounts."""

    def test_type(self, result: AnnualEstimate) -> None:
        """``result.employer_cost`` is an :class:`EmployerCost` instance."""
        assert isinstance(result.employer_cost, EmployerCost)

    def test_employer_cost_annual_positive(self, result: AnnualEstimate) -> None:
        """``employer_cost.employer_cost_annual`` is positive."""
        assert result.employer_cost.employer_cost_annual > Decimal(0)

    def test_employer_cost_exceeds_gross(self, result: AnnualEstimate) -> None:
        """Total employer cost exceeds gross annual pay."""
        assert result.employer_cost.employer_cost_annual > result.earnings.gross_annual

    def test_frozen(self, result: AnnualEstimate) -> None:
        """``EmployerCost`` is immutable."""
        with pytest.raises(Exception, match="cannot assign"):
            result.employer_cost.employer_cost_annual = Decimal(0)  # type: ignore[misc]


class TestCoverage:
    """AnnualEstimate.coverage contains quality and scope metadata."""

    def test_type(self, result: AnnualEstimate) -> None:
        """``result.coverage`` is a :class:`Coverage` instance."""
        assert isinstance(result.coverage, Coverage)

    def test_status_valid(self, result: AnnualEstimate) -> None:
        """``coverage.status`` is one of the valid literals."""
        assert result.coverage.status in {"partial", "complete"}

    def test_confidence_valid(self, result: AnnualEstimate) -> None:
        """``coverage.confidence`` is one of the valid literals."""
        assert result.coverage.confidence in {"low", "medium", "high"}

    def test_calculation_scope_is_tuple(self, result: AnnualEstimate) -> None:
        """``coverage.calculation_scope`` is a tuple."""
        assert isinstance(result.coverage.calculation_scope, tuple)

    def test_warnings_is_tuple(self, result: AnnualEstimate) -> None:
        """``coverage.warnings`` is a tuple."""
        assert isinstance(result.coverage.warnings, tuple)

    def test_frozen(self, result: AnnualEstimate) -> None:
        """``Coverage`` is immutable."""
        with pytest.raises(Exception, match="cannot assign"):
            result.coverage.status = "partial"  # type: ignore[misc]
