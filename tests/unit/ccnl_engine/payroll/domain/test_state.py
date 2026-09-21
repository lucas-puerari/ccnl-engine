"""Unit tests for FiscalState, ContributiveState, LeaveState, PayrollState."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.state import (
    ContributiveState,
    FiscalState,
    LeaveState,
    PayrollState,
)

_ZERO = Decimal(0)
_V = Decimal("100.00")
_YEAR = 2026


class TestFiscalState:
    """FiscalState stores fiscal accumulators and provides a zero factory."""

    def test_zero_factory_returns_fiscal_state(self) -> None:
        """FiscalState.zero() returns a FiscalState instance."""
        assert isinstance(FiscalState.zero(), FiscalState)

    def test_zero_all_fields_are_zero(self) -> None:
        """Every field in FiscalState.zero() is Decimal(0)."""
        s = FiscalState.zero()
        assert s.taxable_income_ytd == _ZERO
        assert s.irpef_gross_ytd == _ZERO
        assert s.irpef_withheld_ytd == _ZERO
        assert s.work_income_deduction_ytd == _ZERO
        assert s.fam_deductions_ytd == _ZERO
        assert s.art15_deductions_ytd == _ZERO
        assert s.trattamento_integrativo_ytd == _ZERO
        assert s.addizionale_regionale_ytd == _ZERO
        assert s.addizionale_comunale_ytd == _ZERO

    def test_stored_values(self) -> None:
        """All fields are stored and retrievable after explicit construction."""
        s = FiscalState(
            taxable_income_ytd=Decimal("10000.00"),
            irpef_gross_ytd=Decimal("2300.00"),
            irpef_withheld_ytd=Decimal("1955.00"),
            work_income_deduction_ytd=Decimal("1200.00"),
            fam_deductions_ytd=Decimal("400.00"),
            art15_deductions_ytd=Decimal("0.00"),
            trattamento_integrativo_ytd=Decimal("92.31"),
            addizionale_regionale_ytd=Decimal("180.00"),
            addizionale_comunale_ytd=Decimal("90.00"),
        )
        assert s.taxable_income_ytd == Decimal("10000.00")
        assert s.irpef_withheld_ytd == Decimal("1955.00")
        assert s.trattamento_integrativo_ytd == Decimal("92.31")

    def test_frozen(self) -> None:
        """FiscalState is immutable: attribute assignment raises AttributeError."""
        s = FiscalState.zero()
        with pytest.raises(AttributeError):
            s.irpef_withheld_ytd = _V  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two FiscalState instances with equal fields compare equal."""
        assert FiscalState.zero() == FiscalState.zero()


class TestContributiveState:
    """ContributiveState stores INPS, INAIL, TFR, and gross accumulators."""

    def test_zero_factory_returns_contributive_state(self) -> None:
        """ContributiveState.zero() returns a ContributiveState instance."""
        assert isinstance(ContributiveState.zero(), ContributiveState)

    def test_zero_all_fields_are_zero(self) -> None:
        """Every field in ContributiveState.zero() is Decimal(0)."""
        s = ContributiveState.zero()
        assert s.gross_ytd == _ZERO
        assert s.inps_employee_ytd == _ZERO
        assert s.inps_employer_ytd == _ZERO
        assert s.inail_employer_ytd == _ZERO
        assert s.tfr_ytd == _ZERO

    def test_stored_values(self) -> None:
        """All fields are stored and retrievable after explicit construction."""
        s = ContributiveState(
            gross_ytd=Decimal("12000.00"),
            inps_employee_ytd=Decimal("1100.00"),
            inps_employer_ytd=Decimal("3200.00"),
            inail_employer_ytd=Decimal("60.00"),
            tfr_ytd=Decimal("700.00"),
        )
        assert s.gross_ytd == Decimal("12000.00")
        assert s.tfr_ytd == Decimal("700.00")

    def test_frozen(self) -> None:
        """ContributiveState is immutable: assignment raises AttributeError."""
        s = ContributiveState.zero()
        with pytest.raises(AttributeError):
            s.gross_ytd = _V  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two ContributiveState instances with equal fields compare equal."""
        assert ContributiveState.zero() == ContributiveState.zero()


class TestLeaveState:
    """LeaveState stores leave and sickness day counters."""

    def test_zero_factory_returns_leave_state(self) -> None:
        """LeaveState.zero() returns a LeaveState instance."""
        assert isinstance(LeaveState.zero(), LeaveState)

    def test_zero_all_fields_are_zero(self) -> None:
        """Every field in LeaveState.zero() is Decimal(0)."""
        s = LeaveState.zero()
        assert s.leave_accrued_days_ytd == _ZERO
        assert s.leave_taken_days_ytd == _ZERO
        assert s.sick_days_ytd == _ZERO

    def test_stored_values(self) -> None:
        """All fields are stored and retrievable after explicit construction."""
        s = LeaveState(
            leave_accrued_days_ytd=Decimal("16.00"),
            leave_taken_days_ytd=Decimal("5.00"),
            sick_days_ytd=Decimal("3.00"),
        )
        assert s.leave_accrued_days_ytd == Decimal("16.00")
        assert s.leave_taken_days_ytd == Decimal("5.00")
        assert s.sick_days_ytd == Decimal("3.00")

    def test_frozen(self) -> None:
        """LeaveState is immutable: attribute assignment raises AttributeError."""
        s = LeaveState.zero()
        with pytest.raises(AttributeError):
            s.sick_days_ytd = _V  # type: ignore[misc]


class TestPayrollState:
    """PayrollState composes sub-states with audit metadata."""

    def test_zero_factory_returns_payroll_state(self) -> None:
        """PayrollState.zero(year) returns a PayrollState instance."""
        assert isinstance(PayrollState.zero(_YEAR), PayrollState)

    def test_zero_tax_year_stored(self) -> None:
        """PayrollState.zero() stores the supplied tax_year."""
        s = PayrollState.zero(_YEAR)
        assert s.tax_year == _YEAR

    def test_zero_periods_closed_is_zero(self) -> None:
        """PayrollState.zero() starts with periods_closed == 0."""
        assert PayrollState.zero(_YEAR).periods_closed == 0

    def test_zero_revision_id_format(self) -> None:
        """revision_id for zero state is 'ytd-{year}-p00'."""
        assert PayrollState.zero(_YEAR).revision_id == "ytd-2026-p00"

    def test_zero_source_period_ids_empty(self) -> None:
        """source_period_ids is empty for the zero state."""
        assert PayrollState.zero(_YEAR).source_period_ids == ()

    def test_zero_sub_states_are_zero(self) -> None:
        """All sub-states on zero() are themselves at zero."""
        s = PayrollState.zero(_YEAR)
        assert s.fiscal == FiscalState.zero()
        assert s.contributive == ContributiveState.zero()
        assert s.leave == LeaveState.zero()

    def test_stored_sub_states(self) -> None:
        """Sub-states passed at construction are stored by value."""
        fiscal = FiscalState(
            taxable_income_ytd=_V,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_ZERO,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
        )
        s = PayrollState(
            tax_year=_YEAR,
            periods_closed=1,
            revision_id="ytd-2026-p01",
            fiscal=fiscal,
            contributive=ContributiveState.zero(),
            leave=LeaveState.zero(),
            source_period_ids=(),
        )
        assert s.fiscal is fiscal
        assert s.fiscal.taxable_income_ytd == _V

    def test_frozen(self) -> None:
        """PayrollState is immutable: attribute assignment raises AttributeError."""
        s = PayrollState.zero(_YEAR)
        with pytest.raises(AttributeError):
            s.periods_closed = 1  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two PayrollState instances with equal sub-states compare equal."""
        assert PayrollState.zero(_YEAR) == PayrollState.zero(_YEAR)
