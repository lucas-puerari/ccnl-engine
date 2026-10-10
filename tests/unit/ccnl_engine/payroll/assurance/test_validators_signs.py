"""Unit tests for reconcile(): sign invariants on synthetic results."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.assurance.validators import reconcile
from ccnl_engine.payroll.ledger.models import AccountKind
from tests.fixtures.synthetic_period_result import OPENING, ResultBuilder, ledger_entry


class TestGrossNonNegative:
    """gross_non_negative: period_gross must be non-negative."""

    def test_violation_when_gross_is_negative(self) -> None:
        """gross_non_negative violation when period_gross is negative."""
        b = ResultBuilder(period_gross=Decimal("-100.00"))
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "gross_non_negative"]
        assert len(found) == 1
        assert found[0].actual == Decimal("-100.00")

    def test_no_violation_when_gross_is_zero(self) -> None:
        """No gross_non_negative violation when period_gross is exactly zero."""
        b = ResultBuilder(period_gross=Decimal(0))
        r = reconcile(b.build(), OPENING)
        assert [v for v in r.violations if v.invariant_id == "gross_non_negative"] == []


class TestSubstituteTaxNonNegative:
    """substitute_tax_non_negative: every SUBSTITUTE_TAX entry is >= 0."""

    def test_violation_on_negative_substitute_tax(self) -> None:
        """Violation when a SUBSTITUTE_TAX entry has a negative amount."""
        e = ledger_entry("st", AccountKind.SUBSTITUTE_TAX, Decimal("-50.00"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "substitute_tax_non_negative"
        ]
        assert len(found) == 1
        assert "st" in found[0].message

    def test_no_violation_for_zero_substitute_tax(self) -> None:
        """Zero SUBSTITUTE_TAX is not a violation."""
        e = ledger_entry("st", AccountKind.SUBSTITUTE_TAX, Decimal("0.00"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "substitute_tax_non_negative"
        ] == []


class TestOrdinaryTaxNonNegative:
    """ordinary_tax_non_negative: every ORDINARY_TAX entry is >= 0."""

    def test_violation_on_negative_ordinary_tax(self) -> None:
        """Violation when an ORDINARY_TAX entry has a negative amount."""
        e = ledger_entry("irpef", AccountKind.ORDINARY_TAX, Decimal("-100.00"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "ordinary_tax_non_negative"
        ]
        assert len(found) == 1
        assert "irpef" in found[0].message

    def test_no_violation_for_zero_ordinary_tax(self) -> None:
        """Zero ORDINARY_TAX is not a violation."""
        e = ledger_entry("irpef", AccountKind.ORDINARY_TAX, Decimal("0.00"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "ordinary_tax_non_negative"
        ] == []


_CONTRIBUTION_INVARIANTS = [
    pytest.param(
        AccountKind.EMPLOYEE_CONTRIBUTIONS,
        "employee_contribution_non_negative",
        id="employee",
    ),
    pytest.param(
        AccountKind.EMPLOYER_CONTRIBUTIONS,
        "employer_contribution_non_negative",
        id="employer",
    ),
]


class TestContributionsNonNegative:
    """Ordinary employee and employer contributions are never negative."""

    @pytest.mark.parametrize(("account", "invariant_id"), _CONTRIBUTION_INVARIANTS)
    def test_violation_on_negative_contribution(
        self, account: AccountKind, invariant_id: str
    ) -> None:
        """A negative contribution entry is reported with its pay item id."""
        e = ledger_entry("inps", account, Decimal("-68.80"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == invariant_id]
        assert len(found) == 1
        assert "inps" in found[0].message

    @pytest.mark.parametrize(("account", "invariant_id"), _CONTRIBUTION_INVARIANTS)
    def test_no_violation_for_zero_contribution(
        self, account: AccountKind, invariant_id: str
    ) -> None:
        """A zero contribution is not a violation."""
        e = ledger_entry("inps", account, Decimal("0.00"))
        b = ResultBuilder(ledger_entries=(e,))
        r = reconcile(b.build(), OPENING)
        assert [v for v in r.violations if v.invariant_id == invariant_id] == []
