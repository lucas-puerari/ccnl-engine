"""Unit tests for the treatment enums in treatments.py."""

from __future__ import annotations

import ccnl_engine.engine.payroll.domain.pay_items as _pay_items
from ccnl_engine.engine.payroll.domain.treatments import (
    ContributionTreatment,
    CostTreatment,
    TaxTreatment,
    TfrTreatment,
)


class TestTaxTreatment:
    """TaxTreatment StrEnum covers all IRPEF classification cases."""

    def test_ordinary(self) -> None:
        """ORDINARY maps to 'ordinary'."""
        assert TaxTreatment.ORDINARY.value == "ordinary"

    def test_separate(self) -> None:
        """SEPARATE maps to 'separate'."""
        assert TaxTreatment.SEPARATE.value == "separate"

    def test_substitute(self) -> None:
        """SUBSTITUTE maps to 'substitute'."""
        assert TaxTreatment.SUBSTITUTE.value == "substitute"

    def test_exempt(self) -> None:
        """EXEMPT maps to 'exempt'."""
        assert TaxTreatment.EXEMPT.value == "exempt"

    def test_non_cash_taxable(self) -> None:
        """NON_CASH_TAXABLE maps to 'non_cash_taxable'."""
        assert TaxTreatment.NON_CASH_TAXABLE.value == "non_cash_taxable"

    def test_is_str(self) -> None:
        """TaxTreatment members are strings (StrEnum)."""
        assert isinstance(TaxTreatment.ORDINARY, str)

    def test_five_members(self) -> None:
        """TaxTreatment has exactly five members."""
        assert len(TaxTreatment) == 5


class TestContributionTreatment:
    """ContributionTreatment StrEnum covers all INPS base classification cases."""

    def test_included(self) -> None:
        """INCLUDED maps to 'included'."""
        assert ContributionTreatment.INCLUDED.value == "included"

    def test_excluded(self) -> None:
        """EXCLUDED maps to 'excluded'."""
        assert ContributionTreatment.EXCLUDED.value == "excluded"

    def test_capped(self) -> None:
        """CAPPED maps to 'capped'."""
        assert ContributionTreatment.CAPPED.value == "capped"

    def test_special_base(self) -> None:
        """SPECIAL_BASE maps to 'special_base'."""
        assert ContributionTreatment.SPECIAL_BASE.value == "special_base"

    def test_is_str(self) -> None:
        """ContributionTreatment members are strings (StrEnum)."""
        assert isinstance(ContributionTreatment.INCLUDED, str)

    def test_four_members(self) -> None:
        """ContributionTreatment has exactly four members."""
        assert len(ContributionTreatment) == 4


class TestTfrTreatment:
    """TfrTreatment StrEnum covers all TFR accrual base cases."""

    def test_included(self) -> None:
        """INCLUDED maps to 'included'."""
        assert TfrTreatment.INCLUDED.value == "included"

    def test_excluded(self) -> None:
        """EXCLUDED maps to 'excluded'."""
        assert TfrTreatment.EXCLUDED.value == "excluded"

    def test_special(self) -> None:
        """SPECIAL maps to 'special'."""
        assert TfrTreatment.SPECIAL.value == "special"

    def test_is_str(self) -> None:
        """TfrTreatment members are strings (StrEnum)."""
        assert isinstance(TfrTreatment.INCLUDED, str)

    def test_three_members(self) -> None:
        """TfrTreatment has exactly three members."""
        assert len(TfrTreatment) == 3


class TestCostTreatment:
    """CostTreatment StrEnum covers all employer cost perspective cases."""

    def test_employee_cash(self) -> None:
        """EMPLOYEE_CASH maps to 'employee_cash'."""
        assert CostTreatment.EMPLOYEE_CASH.value == "employee_cash"

    def test_employer_cost(self) -> None:
        """EMPLOYER_COST maps to 'employer_cost'."""
        assert CostTreatment.EMPLOYER_COST.value == "employer_cost"

    def test_third_party_cash(self) -> None:
        """THIRD_PARTY_CASH maps to 'third_party_cash'."""
        assert CostTreatment.THIRD_PARTY_CASH.value == "third_party_cash"

    def test_accrual_only(self) -> None:
        """ACCRUAL_ONLY maps to 'accrual_only'."""
        assert CostTreatment.ACCRUAL_ONLY.value == "accrual_only"

    def test_is_str(self) -> None:
        """CostTreatment members are strings (StrEnum)."""
        assert isinstance(CostTreatment.EMPLOYEE_CASH, str)

    def test_four_members(self) -> None:
        """CostTreatment has exactly four members."""
        assert len(CostTreatment) == 4


class TestCrossImport:
    """Treatment enums are importable from pay_items for backward compatibility."""

    def test_tax_treatment_importable_from_pay_items(self) -> None:
        """TaxTreatment is re-exported from pay_items."""
        assert _pay_items.TaxTreatment.ORDINARY.value == "ordinary"

    def test_contribution_treatment_importable_from_pay_items(self) -> None:
        """ContributionTreatment is re-exported from pay_items."""
        assert _pay_items.ContributionTreatment.INCLUDED.value == "included"

    def test_tfr_treatment_importable_from_pay_items(self) -> None:
        """TfrTreatment is re-exported from pay_items."""
        assert _pay_items.TfrTreatment.INCLUDED.value == "included"

    def test_cost_treatment_importable_from_pay_items(self) -> None:
        """CostTreatment is re-exported from pay_items."""
        assert _pay_items.CostTreatment.EMPLOYEE_CASH.value == "employee_cash"
