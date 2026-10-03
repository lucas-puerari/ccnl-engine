"""Unit tests for reconcile(): ledger and state invariants on synthetic results."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
    reconcile,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.period_state import PeriodState
from tests.fixtures.synthetic_period_result import (
    COMPETENCE,
    OPENING,
    PAYMENT_DATE,
    ResultBuilder,
    ledger_entry,
    salary_item,
)


class TestReconciliationViolation:
    """ReconciliationViolation stores invariant_id, message, and optional amounts."""

    def test_required_fields_stored(self) -> None:
        """invariant_id and message are stored at construction."""
        v = ReconciliationViolation(invariant_id="net_identity", message="test failure")
        assert v.invariant_id == "net_identity"
        assert v.message == "test failure"

    def test_optional_amounts_stored(self) -> None:
        """Expected and actual are stored when supplied."""
        v = ReconciliationViolation(
            invariant_id="net_identity",
            message="mismatch",
            expected=Decimal("100.00"),
            actual=Decimal("99.00"),
        )
        assert v.expected == Decimal("100.00")
        assert v.actual == Decimal("99.00")

    def test_optional_amounts_default_none(self) -> None:
        """Expected and actual default to None when omitted."""
        v = ReconciliationViolation(invariant_id="net_identity", message="msg")
        assert v.expected is None
        assert v.actual is None

    def test_frozen(self) -> None:
        """ReconciliationViolation is immutable."""
        v = ReconciliationViolation(invariant_id="net_identity", message="msg")
        with pytest.raises(AttributeError):
            v.invariant_id = "X"  # type: ignore[misc]


class TestReconciliationResult:
    """ReconciliationResult.ok reflects the absence of violations."""

    def test_ok_when_no_violations(self) -> None:
        """Ok is True when violations is empty."""
        r = ReconciliationResult(violations=())
        assert r.ok is True

    def test_not_ok_when_violations_present(self) -> None:
        """Ok is False when at least one violation exists."""
        v = ReconciliationViolation(invariant_id="net_identity", message="x")
        r = ReconciliationResult(violations=(v,))
        assert r.ok is False


class TestPayItemPosted:
    """pay_item_posted: every PayItem must have at least one matching LedgerEntry."""

    def test_violation_when_item_has_no_entry(self) -> None:
        """pay_item_posted violation for a PayItem with no matching LedgerEntry."""
        orphan = salary_item("orphan_item", Decimal("100.00"))
        b = ResultBuilder(
            pay_items=(orphan,),
            ledger_entries=(),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "pay_item_posted"]
        assert len(found) == 1
        assert "orphan_item" in found[0].message


class TestEarningContributionExclusive:
    """earning_contribution_exclusive: no item posts to earnings and contributions."""

    def test_violation_when_item_in_both_accounts(self) -> None:
        """Violation when the same pay_item_id posts to conflicting accounts."""
        e1 = ledger_entry("item_x", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e2 = ledger_entry(
            "item_x", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00")
        )
        b = ResultBuilder(ledger_entries=(e1, e2))
        r = reconcile(b.build(), OPENING)
        found = [
            v
            for v in r.violations
            if v.invariant_id == "earning_contribution_exclusive"
        ]
        assert len(found) == 1
        assert "item_x" in found[0].message


class TestNetIdentity:
    """net_identity: cash + credits - contributions - taxes = period_net."""

    def test_violation_when_net_does_not_match(self) -> None:
        """net_identity violation when period_net disagrees with the ledger identity."""
        e_cash = ledger_entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_tax = ledger_entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        e_inps = ledger_entry(
            "i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00")
        )
        b = ResultBuilder(
            period_net=Decimal("9999.00"),
            ledger_entries=(e_cash, e_tax, e_inps),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "net_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("2200.00")


class TestIrpefWithheldContinuity:
    """irpef_withheld_continuity: closing IRPEF delta equals ORDINARY_TAX."""

    def test_violation_when_delta_does_not_match(self) -> None:
        """Violation when the IRPEF delta diverges from the ORDINARY_TAX total."""
        e_tax = ledger_entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        b = ResultBuilder(
            closing_irpef=Decimal("9999.00"),
            ledger_entries=(e_tax,),
        )
        r = reconcile(b.build(), OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "irpef_withheld_continuity"
        ]
        assert len(found) == 1
        assert found[0].expected == Decimal("500.00")
        assert found[0].actual == Decimal("9999.00")


class TestStateTransition:
    """Closing state must advance each counter and YTD field correctly."""

    def test_no_counter_violation_when_the_run_closes_once(self) -> None:
        """The run closes its competence run and its payment once."""
        r = reconcile(ResultBuilder().build(), OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "run_counters_advance"
        ] == []

    def test_violation_when_the_run_is_not_closed(self) -> None:
        """A closing state that forgets the run and its payment is reported."""
        result = ResultBuilder().build()
        unclosed = replace(result, closing_state=PeriodState.zero())
        r = reconcile(unclosed, OPENING)
        found = [v for v in r.violations if v.invariant_id == "run_counters_advance"]
        assert [v.message for v in found] == [
            "competence run '2026-01-regular' not closed once",
            "payment of run '2026-01-regular' not closed once",
        ]

    def test_violation_when_gross_ytd_wrong(self) -> None:
        """ytd_continuity violation when gross_ytd is not correctly accumulated."""
        e_cash = ledger_entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = ResultBuilder(
            closing_gross=Decimal("9999.00"),
            ledger_entries=(e_cash,),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "ytd_continuity"]
        msgs = [v.message for v in found]
        assert any("gross_ytd" in m for m in msgs)

    def test_violation_when_inps_ytd_wrong(self) -> None:
        """ytd_continuity violation when inps_employee_ytd is wrongly accumulated."""
        e_inps = ledger_entry(
            "i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00")
        )
        b = ResultBuilder(
            closing_inps=Decimal("9999.00"),
            ledger_entries=(e_inps,),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "ytd_continuity"]
        msgs = [v.message for v in found]
        assert any("inps_employee_ytd" in m for m in msgs)


class TestEmployerCostIdentity:
    """employer_cost_identity: earnings + benefits + employer contributions + TFR."""

    def test_violation_when_employer_cost_wrong(self) -> None:
        """Violation when period_employer_cost diverges from the ledger identity."""
        e_cash = ledger_entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_empl = ledger_entry(
            "e", AccountKind.EMPLOYER_CONTRIBUTIONS, Decimal("300.00")
        )
        e_tfr = ledger_entry("t", AccountKind.TFR_ACCRUAL, Decimal("100.00"))
        b = ResultBuilder(
            period_employer_cost=Decimal("9999.00"),
            ledger_entries=(e_cash, e_empl, e_tfr),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "employer_cost_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("3400.00")

    def test_non_cash_benefits_included_in_employer_cost(self) -> None:
        """NON_CASH_BENEFITS entries count toward employer cost identity."""
        e_cash = ledger_entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_ncb = ledger_entry("n", AccountKind.NON_CASH_BENEFITS, Decimal("200.00"))
        e_empl = ledger_entry(
            "e", AccountKind.EMPLOYER_CONTRIBUTIONS, Decimal("300.00")
        )
        e_tfr = ledger_entry("t", AccountKind.TFR_ACCRUAL, Decimal("100.00"))
        b = ResultBuilder(
            period_employer_cost=Decimal("3600.00"),
            ledger_entries=(e_cash, e_ncb, e_empl, e_tfr),
        )
        r = reconcile(b.build(), OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "employer_cost_identity"
        ] == []


class TestGrossIdentity:
    """gross_identity: period_gross must equal the CASH_EARNINGS ledger total."""

    def test_violation_when_gross_does_not_match(self) -> None:
        """gross_identity violation when period_gross diverges from CASH_EARNINGS."""
        e_cash = ledger_entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = ResultBuilder(period_gross=Decimal("9999.00"), ledger_entries=(e_cash,))
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "gross_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("3000.00")


class TestLedgerEntryUnique:
    """ledger_entry_unique: all ledger entry IDs within a period must be unique."""

    def test_violation_on_duplicate_entry_id(self) -> None:
        """ledger_entry_unique violation when an entry_id appears twice."""
        e1 = ledger_entry("item_a", AccountKind.CASH_EARNINGS, Decimal("1000.00"))
        e2 = LedgerEntry(
            entry_id="e_item_a",
            competence_period=COMPETENCE,
            payment_date=PAYMENT_DATE,
            pay_item_id="item_b",
            pay_item_kind="base_salary_earning",
            account=AccountKind.ORDINARY_TAX,
            amount=Decimal("200.00"),
        )
        b = ResultBuilder(
            period_gross=Decimal("1000.00"),
            period_net=Decimal("800.00"),
            ledger_entries=(e1, e2),
        )
        r = reconcile(b.build(), OPENING)
        found = [v for v in r.violations if v.invariant_id == "ledger_entry_unique"]
        assert len(found) == 1
        assert "e_item_a" in found[0].message

    def test_no_violation_when_ids_unique(self) -> None:
        """No ledger_entry_unique violation when entry IDs are all distinct."""
        e1 = ledger_entry("item_x", AccountKind.CASH_EARNINGS, Decimal("1000.00"))
        e2 = ledger_entry(
            "item_y", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("100.00")
        )
        b = ResultBuilder(
            period_gross=Decimal("1000.00"),
            period_net=Decimal("900.00"),
            ledger_entries=(e1, e2),
        )
        r = reconcile(b.build(), OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "ledger_entry_unique"
        ] == []


class TestReconcileIntegration:
    """reconcile() aggregates all invariant checks into one result."""

    def test_violations_accumulate_across_invariants(self) -> None:
        """Multiple failing invariants produce multiple violations in one result."""
        orphan = salary_item("orphan", Decimal("100.00"))
        b = ResultBuilder(
            period_gross=Decimal("9999.00"),
            pay_items=(orphan,),
            ledger_entries=(),
        )
        r = reconcile(b.build(), OPENING)
        ids = {v.invariant_id for v in r.violations}
        assert "pay_item_posted" in ids
        assert "gross_identity" in ids
        assert not r.ok
