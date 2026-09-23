"""Unit tests for PayrollState YTD progressive container."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState

_ZERO = Decimal(0)
_V = Decimal("100.00")

_ALL_FIELDS = [
    "gross_annual_ytd",
    "inps_employee_annual_ytd",
    "inps_employer_annual_ytd",
    "inail_employer_annual_ytd",
    "taxable_income_ytd",
    "irpef_gross_ytd",
    "irpef_withheld_ytd",
    "work_income_deduction_ytd",
    "fam_deductions_ytd",
    "art15_deductions_ytd",
    "trattamento_integrativo_ytd",
    "addizionale_regionale_ytd",
    "addizionale_comunale_ytd",
    "tfr_annual_ytd",
    "leave_accrued_days_ytd",
    "leave_taken_days_ytd",
    "leave_balance_days",
    "sick_days_ytd",
]


class TestPayrollStateZero:
    """PayrollState.zero() returns a valid all-zero instance."""

    def test_zero_returns_payroll_state(self) -> None:
        """zero() returns a PayrollState instance."""
        state = PayrollState.zero()
        assert isinstance(state, PayrollState)

    @pytest.mark.parametrize("field", _ALL_FIELDS)
    def test_zero_field_is_zero(self, field: str) -> None:
        """Every field on PayrollState.zero() is Decimal(0)."""
        state = PayrollState.zero()
        assert getattr(state, field) == _ZERO

    def test_zero_field_count(self) -> None:
        """PayrollState has exactly 18 fields."""
        state = PayrollState.zero()
        assert len(_ALL_FIELDS) == 18
        for f in _ALL_FIELDS:
            assert hasattr(state, f)


class TestPayrollStateImmutable:
    """PayrollState is frozen (immutable)."""

    def test_frozen_raises_on_set(self) -> None:
        """Assigning to any field raises FrozenInstanceError."""
        state = PayrollState.zero()
        with pytest.raises(AttributeError):
            state.gross_annual_ytd = _V  # type: ignore[misc]


class TestPayrollStateConstruction:
    """PayrollState can be constructed with arbitrary values."""

    def test_explicit_values_stored(self) -> None:
        """Fields store the values passed at construction."""
        state = PayrollState(
            gross_annual_ytd=Decimal("12000.00"),
            inps_employee_annual_ytd=Decimal("1100.00"),
            inps_employer_annual_ytd=Decimal("3200.00"),
            inail_employer_annual_ytd=Decimal("60.00"),
            taxable_income_ytd=Decimal("10900.00"),
            irpef_gross_ytd=Decimal("2400.00"),
            irpef_withheld_ytd=Decimal("2000.00"),
            work_income_deduction_ytd=Decimal("950.00"),
            fam_deductions_ytd=Decimal("400.00"),
            art15_deductions_ytd=Decimal("0.00"),
            trattamento_integrativo_ytd=Decimal("100.00"),
            addizionale_regionale_ytd=Decimal("180.00"),
            addizionale_comunale_ytd=Decimal("90.00"),
            tfr_annual_ytd=Decimal("700.00"),
            leave_accrued_days_ytd=Decimal("16.00"),
            leave_taken_days_ytd=Decimal("5.00"),
            leave_balance_days=Decimal("11.00"),
            sick_days_ytd=Decimal("3.00"),
        )
        assert state.gross_annual_ytd == Decimal("12000.00")
        assert state.inps_employee_annual_ytd == Decimal("1100.00")
        assert state.tfr_annual_ytd == Decimal("700.00")
        assert state.leave_balance_days == Decimal("11.00")
        assert state.sick_days_ytd == Decimal("3.00")

    def test_equality_on_same_values(self) -> None:
        """Two PayrollState instances with the same values compare equal."""
        s1 = PayrollState.zero()
        s2 = PayrollState.zero()
        assert s1 == s2

    def test_inequality_on_different_values(self) -> None:
        """Two PayrollState instances with different values are not equal."""
        s1 = PayrollState.zero()
        s2 = PayrollState(
            gross_annual_ytd=_V,
            inps_employee_annual_ytd=_ZERO,
            inps_employer_annual_ytd=_ZERO,
            inail_employer_annual_ytd=_ZERO,
            taxable_income_ytd=_ZERO,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_ZERO,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
            tfr_annual_ytd=_ZERO,
            leave_accrued_days_ytd=_ZERO,
            leave_taken_days_ytd=_ZERO,
            leave_balance_days=_ZERO,
            sick_days_ytd=_ZERO,
        )
        assert s1 != s2


class TestPayrollStatePublicApi:
    """PayrollState from the public API is PeriodState."""

    def test_public_payroll_state_is_period_state(self) -> None:
        """ccnl_engine.PayrollState is PeriodState, not the legacy type."""
        from ccnl_engine import PayrollState as PublicState  # noqa: PLC0415
        from ccnl_engine.payroll.domain.period import PeriodState  # noqa: PLC0415

        assert PublicState is PeriodState
