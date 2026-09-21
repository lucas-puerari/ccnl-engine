"""Unit tests for FiscalYTD domain type."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.payroll.domain.fiscal_ytd import FiscalYTD

_ZERO = Decimal(0)
_V = Decimal("100.00")


class TestFiscalYTDZero:
    """FiscalYTD.zero() returns a zero-valued instance."""

    def test_zero_returns_fiscal_ytd(self) -> None:
        """zero() returns a FiscalYTD instance."""
        assert isinstance(FiscalYTD.zero(), FiscalYTD)

    def test_taxable_income_ytd_is_zero(self) -> None:
        """taxable_income_ytd is zero."""
        assert FiscalYTD.zero().taxable_income_ytd == _ZERO

    def test_irpef_gross_ytd_is_zero(self) -> None:
        """irpef_gross_ytd is zero."""
        assert FiscalYTD.zero().irpef_gross_ytd == _ZERO

    def test_irpef_withheld_ytd_is_zero(self) -> None:
        """irpef_withheld_ytd is zero."""
        assert FiscalYTD.zero().irpef_withheld_ytd == _ZERO

    def test_work_income_deduction_ytd_is_zero(self) -> None:
        """work_income_deduction_ytd is zero."""
        assert FiscalYTD.zero().work_income_deduction_ytd == _ZERO

    def test_fam_deductions_ytd_is_zero(self) -> None:
        """fam_deductions_ytd is zero."""
        assert FiscalYTD.zero().fam_deductions_ytd == _ZERO

    def test_art15_deductions_ytd_is_zero(self) -> None:
        """art15_deductions_ytd is zero."""
        assert FiscalYTD.zero().art15_deductions_ytd == _ZERO

    def test_trattamento_integrativo_ytd_is_zero(self) -> None:
        """trattamento_integrativo_ytd is zero."""
        assert FiscalYTD.zero().trattamento_integrativo_ytd == _ZERO

    def test_addizionale_regionale_ytd_is_zero(self) -> None:
        """addizionale_regionale_ytd is zero."""
        assert FiscalYTD.zero().addizionale_regionale_ytd == _ZERO

    def test_addizionale_comunale_ytd_is_zero(self) -> None:
        """addizionale_comunale_ytd is zero."""
        assert FiscalYTD.zero().addizionale_comunale_ytd == _ZERO

    def test_zero_is_idempotent(self) -> None:
        """Calling zero() twice returns equal instances."""
        assert FiscalYTD.zero() == FiscalYTD.zero()


class TestFiscalYTDImmutability:
    """FiscalYTD is a frozen dataclass."""

    def test_frozen_cannot_assign(self) -> None:
        """Assignment to a field raises FrozenInstanceError."""
        import dataclasses  # noqa: PLC0415

        import pytest  # noqa: PLC0415

        ytd = FiscalYTD.zero()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ytd.irpef_withheld_ytd = _V  # type: ignore[misc]


class TestFiscalYTDFields:
    """FiscalYTD stores the values passed at construction."""

    def test_taxable_income_ytd_stored(self) -> None:
        """taxable_income_ytd holds the value passed at construction."""
        ytd = FiscalYTD(
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
        assert ytd.taxable_income_ytd == _V

    def test_irpef_withheld_ytd_stored(self) -> None:
        """irpef_withheld_ytd holds the value passed at construction."""
        ytd = FiscalYTD(
            taxable_income_ytd=_ZERO,
            irpef_gross_ytd=_ZERO,
            irpef_withheld_ytd=_V,
            work_income_deduction_ytd=_ZERO,
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=_ZERO,
            addizionale_comunale_ytd=_ZERO,
        )
        assert ytd.irpef_withheld_ytd == _V

    def test_nine_fields(self) -> None:
        """FiscalYTD has exactly nine fields."""
        import dataclasses  # noqa: PLC0415

        assert len(dataclasses.fields(FiscalYTD)) == 9
