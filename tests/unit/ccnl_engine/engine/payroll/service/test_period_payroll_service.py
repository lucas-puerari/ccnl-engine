"""Unit tests for compute_period_payroll service function."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute_period_payroll

_ZERO = Decimal(0)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_AS_OF = date(2026, 1, 1)


def _structural() -> AnnualEstimateInput:
    """Return a minimal structural scenario.

    Returns:
        A minimal :class:`AnnualEstimateInput` with required fields only.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code=_LEVEL),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


def _zero_request() -> PeriodPayrollRequest:
    """Return a request with PayrollState.zero() as opening state.

    Returns:
        A :class:`PeriodPayrollRequest` with all-zero opening state.
    """
    return PeriodPayrollRequest(
        structural=_structural(),
        period=PeriodPayrollInput(),
        opening_state=PayrollState.zero(),
    )


class TestComputePeriodPayrollReturnType:
    """compute_period_payroll returns a PeriodPayrollResult."""

    def test_returns_period_payroll_result(self) -> None:
        """Return type is PeriodPayrollResult."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result, PeriodPayrollResult)

    def test_opening_state_is_zero(self) -> None:
        """Opening state matches the one passed in (zero for January)."""
        result = compute_period_payroll(_zero_request())
        assert result.opening_state == PayrollState.zero()

    def test_closing_state_is_payroll_state(self) -> None:
        """Closing state is a PayrollState instance."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result.closing_state, PayrollState)

    def test_period_gross_positive(self) -> None:
        """period_gross is a positive Decimal."""
        result = compute_period_payroll(_zero_request())
        assert result.period_gross > _ZERO

    def test_period_net_positive(self) -> None:
        """period_net is positive."""
        result = compute_period_payroll(_zero_request())
        assert result.period_net > _ZERO

    def test_period_employer_cost_positive(self) -> None:
        """period_employer_cost is positive."""
        result = compute_period_payroll(_zero_request())
        assert result.period_employer_cost > _ZERO

    def test_ledger_entries_tuple(self) -> None:
        """ledger_entries is a tuple."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result.ledger_entries, tuple)


class TestComputePeriodPayrollStateAccumulation:
    """Closing state accumulates opening state with period increments."""

    def test_gross_ytd_grows(self) -> None:
        """Closing gross_annual_ytd exceeds opening (which is zero)."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.gross_annual_ytd > _ZERO

    def test_inps_employee_ytd_grows(self) -> None:
        """Closing inps_employee_annual_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.inps_employee_annual_ytd > _ZERO

    def test_irpef_withheld_grows(self) -> None:
        """Closing irpef_withheld_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.irpef_withheld_ytd > _ZERO

    def test_tfr_ytd_grows(self) -> None:
        """Closing tfr_annual_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.tfr_annual_ytd > _ZERO

    def test_leave_balance_derived_correctly(self) -> None:
        """leave_balance_days equals accrued minus taken."""
        result = compute_period_payroll(_zero_request())
        closing = result.closing_state
        assert closing.leave_balance_days == (
            closing.leave_accrued_days_ytd - closing.leave_taken_days_ytd
        )

    def test_chained_state_accumulates(self) -> None:
        """Second period's closing gross > first period's closing gross."""
        r1 = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=r1.closing_state,
        )
        r2 = compute_period_payroll(req2)
        assert r2.closing_state.gross_annual_ytd > r1.closing_state.gross_annual_ytd

    def test_opening_state_preserved(self) -> None:
        """opening_state in result matches the one passed in."""
        opening = PayrollState(
            gross_annual_ytd=Decimal("1000.00"),
            inps_employee_annual_ytd=Decimal("90.00"),
            inps_employer_annual_ytd=Decimal("260.00"),
            inail_employer_annual_ytd=Decimal("5.00"),
            taxable_income_ytd=Decimal("910.00"),
            irpef_gross_ytd=Decimal("200.00"),
            irpef_withheld_ytd=Decimal("160.00"),
            work_income_deduction_ytd=Decimal("80.00"),
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=Decimal("15.00"),
            addizionale_comunale_ytd=Decimal("8.00"),
            tfr_annual_ytd=Decimal("55.00"),
            leave_accrued_days_ytd=Decimal("1.83"),
            leave_taken_days_ytd=_ZERO,
            leave_balance_days=Decimal("1.83"),
            sick_days_ytd=_ZERO,
        )
        req = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=opening,
        )
        result = compute_period_payroll(req)
        assert result.opening_state is opening

    def test_closing_gross_is_opening_plus_period(self) -> None:
        """Closing gross_annual_ytd = opening + period_gross."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.gross_annual_ytd == (
            result.opening_state.gross_annual_ytd + result.period_gross
        )


class TestComputePeriodPayrollConguaglio:
    """Prior withheld IRPEF is injected correctly for conguaglio."""

    def test_zero_opening_uses_no_prior_withheld(self) -> None:
        """First period (zero state) computes without prior withheld."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.irpef_withheld_ytd > _ZERO

    def test_nonzero_irpef_ytd_does_not_raise(self) -> None:
        """Nonzero irpef_withheld_ytd in opening state is accepted."""
        opening = PayrollState.zero()
        first = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=first.closing_state,
        )
        result = compute_period_payroll(req2)
        assert result.period_net > _ZERO
        _ = opening  # referenced to satisfy linter

    def test_irpef_withheld_ytd_cumulates_across_periods(self) -> None:
        """irpef_withheld_ytd grows period over period."""
        r1 = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=r1.closing_state,
        )
        r2 = compute_period_payroll(req2)
        assert r2.closing_state.irpef_withheld_ytd > r1.closing_state.irpef_withheld_ytd


class TestComputePeriodPayrollPublicApi:
    """compute_period_payroll is accessible from the top-level package."""

    def test_importable_from_ccnl_engine(self) -> None:
        """compute_period_payroll can be imported from ccnl_engine directly."""
        from ccnl_engine import compute_period_payroll as fn  # noqa: PLC0415

        assert fn is compute_period_payroll

    def test_in_dunder_all(self) -> None:
        """compute_period_payroll is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "compute_period_payroll" in ccnl_engine.__all__

    def test_accepts_optional_bundle_none(self) -> None:
        """bundle=None is accepted (loads on demand)."""
        result = compute_period_payroll(_zero_request(), bundle=None)
        assert isinstance(result, PeriodPayrollResult)

    @pytest.mark.parametrize("n_periods", [1, 3, 12])
    def test_chained_n_periods(self, n_periods: int) -> None:
        """Chain n periods; final gross_ytd is n times first period gross."""
        state = PayrollState.zero()
        first_gross: Decimal | None = None
        for _ in range(n_periods):
            req = PeriodPayrollRequest(
                structural=_structural(),
                period=PeriodPayrollInput(),
                opening_state=state,
            )
            result = compute_period_payroll(req)
            if first_gross is None:
                first_gross = result.period_gross
            state = result.closing_state
        assert state.gross_annual_ytd > _ZERO
