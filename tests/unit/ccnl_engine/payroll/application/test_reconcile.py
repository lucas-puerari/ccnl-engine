"""Unit tests for reconcile(): all I1-I13 invariants and ReconciliationResult."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityReport
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
)
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
    reconcile,
)
from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_CP = CompetencePeriod(year=_YEAR, month=1)
_PAYMENT = date(_YEAR, 1, 28)
_PID = PeriodId(year=_YEAR, month=1)


def _real_result(
    month: int = 1, opening: PeriodState | None = None
) -> tuple[PeriodCalculationResult, PeriodState]:
    """Run a real calculation and return (result, opening_state).

    Returns:
        Tuple of the :class:`PeriodCalculationResult` and the
        :class:`PeriodState` that was used as the opening state.
    """
    op = opening or PeriodState.zero()
    req = PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=op,
    )
    return calculate_period(req), op


def _entry(
    pay_item_id: str,
    account: AccountKind,
    amount: Decimal,
) -> LedgerEntry:
    """Build a minimal LedgerEntry for invariant violation tests.

    Returns:
        A :class:`LedgerEntry` with the given item id, account and amount.
    """
    return LedgerEntry(
        entry_id=f"e_{pay_item_id}",
        competence_period=_CP,
        payment_date=_PAYMENT,
        pay_item_id=pay_item_id,
        pay_item_kind="base_salary_earning",
        account=account,
        amount=amount,
    )


def _item(item_id: str, amount: Decimal) -> BaseSalaryEarning:
    """Build a minimal BaseSalaryEarning for coverage tests.

    Returns:
        A :class:`BaseSalaryEarning` with the given item_id and amount.
    """
    return BaseSalaryEarning(
        item_id=item_id,
        competence_period=_CP,
        payment_date=_PAYMENT,
        quantity=Decimal(1),
        amount=amount,
    )


@dataclass
class _Builder:
    """Mutable result builder for constructing synthetic violation scenarios."""

    period_gross: Decimal = Decimal("3000.00")
    period_net: Decimal = Decimal("2000.00")
    period_employer_cost: Decimal = Decimal("3400.00")
    closing_months: int = 1
    closing_irpef: Decimal = Decimal("500.00")
    closing_inps: Decimal = Decimal("300.00")
    closing_gross: Decimal = Decimal("3000.00")
    pay_items: tuple[BaseSalaryEarning, ...] = ()
    ledger_entries: tuple[LedgerEntry, ...] = ()

    def build(self) -> PeriodCalculationResult:
        """Construct a :class:`PeriodCalculationResult` from the builder state.

        Returns:
            A frozen :class:`PeriodCalculationResult`.
        """
        return PeriodCalculationResult(
            period_id=_PID,
            payment_date=_PAYMENT,
            period_gross=self.period_gross,
            period_net=self.period_net,
            period_employer_cost=self.period_employer_cost,
            closing_state=PeriodState(
                months_closed=self.closing_months,
                irpef_withheld_ytd=self.closing_irpef,
                inps_employee_ytd=self.closing_inps,
                gross_ytd=self.closing_gross,
            ),
            pay_items=self.pay_items,
            ledger_entries=self.ledger_entries,
            capability_report=CapabilityReport.empty(_YEAR),
            contribution_breakdown=ContributionBreakdown(
                employee=Decimal(0), employer=Decimal(0), components=()
            ),
        )


_OPENING = PeriodState.zero()


class TestReconciliationViolation:
    """ReconciliationViolation stores invariant_id, message, and optional amounts."""

    def test_required_fields_stored(self) -> None:
        """invariant_id and message are stored at construction."""
        v = ReconciliationViolation(invariant_id="I9", message="test failure")
        assert v.invariant_id == "I9"
        assert v.message == "test failure"

    def test_optional_amounts_stored(self) -> None:
        """Expected and actual are stored when supplied."""
        v = ReconciliationViolation(
            invariant_id="I9",
            message="mismatch",
            expected=Decimal("100.00"),
            actual=Decimal("99.00"),
        )
        assert v.expected == Decimal("100.00")
        assert v.actual == Decimal("99.00")

    def test_optional_amounts_default_none(self) -> None:
        """Expected and actual default to None when omitted."""
        v = ReconciliationViolation(invariant_id="I9", message="msg")
        assert v.expected is None
        assert v.actual is None

    def test_frozen(self) -> None:
        """ReconciliationViolation is immutable."""
        v = ReconciliationViolation(invariant_id="I9", message="msg")
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
        v = ReconciliationViolation(invariant_id="I9", message="x")
        r = ReconciliationResult(violations=(v,))
        assert r.ok is False


class TestI1Coverage:
    """I1: every PayItem must have at least one matching LedgerEntry."""

    def test_no_violation_when_all_items_have_entries(self) -> None:
        """No I1 violation when every pay_item_id is present in ledger_entries."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        i1 = [v for v in r.violations if v.invariant_id == "I1"]
        assert i1 == []

    def test_violation_when_item_has_no_entry(self) -> None:
        """I1 violation is raised for a PayItem with no matching LedgerEntry."""
        orphan = _item("orphan_item", Decimal("100.00"))
        b = _Builder(
            pay_items=(orphan,),
            ledger_entries=(),
            closing_months=1,
        )
        r = reconcile(b.build(), _OPENING)
        i1 = [v for v in r.violations if v.invariant_id == "I1"]
        assert len(i1) == 1
        assert "orphan_item" in i1[0].message


class TestI2NoDoubleTreatment:
    """I2: no pay_item_id may post to both CASH_EARNINGS and EMPLOYEE_CONTRIBUTIONS."""

    def test_no_violation_on_real_result(self) -> None:
        """No I2 violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "I2"] == []

    def test_violation_when_item_in_both_accounts(self) -> None:
        """I2 violation when the same pay_item_id posts to conflicting accounts."""
        e1 = _entry("item_x", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e2 = _entry("item_x", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(ledger_entries=(e1, e2))
        r = reconcile(b.build(), _OPENING)
        i2 = [v for v in r.violations if v.invariant_id == "I2"]
        assert len(i2) == 1
        assert "item_x" in i2[0].message


class TestI9NetIdentity:
    """I9: net identity — cash + credits - contributions - taxes = period_net."""

    def test_no_violation_on_real_result(self) -> None:
        """No I9 violation on a real calculate_period result."""
        result, opening = _real_result()
        assert reconcile(result, opening).ok

    def test_violation_when_net_does_not_match(self) -> None:
        """I9 violation when period_net disagrees with the ledger identity."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_tax = _entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        e_inps = _entry("i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(
            period_net=Decimal("9999.00"),
            ledger_entries=(e_cash, e_tax, e_inps),
        )
        r = reconcile(b.build(), _OPENING)
        i9 = [v for v in r.violations if v.invariant_id == "I9"]
        assert len(i9) == 1
        assert i9[0].actual == Decimal("2200.00")


class TestI10ConguaglioSource:
    """I10: closing IRPEF delta must equal the ORDINARY_TAX ledger total."""

    def test_no_violation_on_real_result(self) -> None:
        """No I10 violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "I10"] == []

    def test_violation_when_delta_does_not_match(self) -> None:
        """I10 violation when IRPEF delta diverges from ORDINARY_TAX total."""
        e_tax = _entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        b = _Builder(
            closing_irpef=Decimal("9999.00"),
            ledger_entries=(e_tax,),
        )
        r = reconcile(b.build(), _OPENING)
        i10 = [v for v in r.violations if v.invariant_id == "I10"]
        assert len(i10) == 1
        assert i10[0].expected == Decimal("500.00")
        assert i10[0].actual == Decimal("9999.00")


class TestI11StateTransition:
    """I11: closing state must advance each YTD field correctly."""

    def test_no_violation_on_real_result(self) -> None:
        """No I11 violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "I11"] == []

    def test_violation_when_months_closed_wrong(self) -> None:
        """I11 violation when months_closed is not incremented by 1."""
        b = _Builder(closing_months=99)
        r = reconcile(b.build(), _OPENING)
        i11 = [v for v in r.violations if v.invariant_id == "I11"]
        msgs = [v.message for v in i11]
        assert any("months_closed" in m for m in msgs)

    def test_violation_when_gross_ytd_wrong(self) -> None:
        """I11 violation when gross_ytd is not correctly accumulated."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = _Builder(
            closing_gross=Decimal("9999.00"),
            ledger_entries=(e_cash,),
        )
        r = reconcile(b.build(), _OPENING)
        i11 = [v for v in r.violations if v.invariant_id == "I11"]
        msgs = [v.message for v in i11]
        assert any("gross_ytd" in m for m in msgs)

    def test_violation_when_inps_ytd_wrong(self) -> None:
        """I11 violation when inps_employee_ytd is not correctly accumulated."""
        e_inps = _entry("i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(
            closing_inps=Decimal("9999.00"),
            ledger_entries=(e_inps,),
        )
        r = reconcile(b.build(), _OPENING)
        i11 = [v for v in r.violations if v.invariant_id == "I11"]
        msgs = [v.message for v in i11]
        assert any("inps_employee_ytd" in m for m in msgs)


class TestI12EmployerCostIdentity:
    """I12: CASH_EARNINGS + employer contributions + TFR = period_employer_cost."""

    def test_no_violation_on_real_result(self) -> None:
        """No I12 violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "I12"] == []

    def test_violation_when_employer_cost_wrong(self) -> None:
        """I12 violation when period_employer_cost diverges from the ledger identity."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_empl = _entry("e", AccountKind.EMPLOYER_CONTRIBUTIONS, Decimal("300.00"))
        e_tfr = _entry("t", AccountKind.TFR_ACCRUAL, Decimal("100.00"))
        b = _Builder(
            period_employer_cost=Decimal("9999.00"),
            ledger_entries=(e_cash, e_empl, e_tfr),
        )
        r = reconcile(b.build(), _OPENING)
        i12 = [v for v in r.violations if v.invariant_id == "I12"]
        assert len(i12) == 1
        assert i12[0].actual == Decimal("3400.00")


class TestI13GrossIdentity:
    """I13: period_gross must equal the CASH_EARNINGS ledger total."""

    def test_no_violation_on_real_result(self) -> None:
        """No I13 violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "I13"] == []

    def test_violation_when_gross_does_not_match(self) -> None:
        """I13 violation when period_gross diverges from CASH_EARNINGS total."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = _Builder(period_gross=Decimal("9999.00"), ledger_entries=(e_cash,))
        r = reconcile(b.build(), _OPENING)
        i13 = [v for v in r.violations if v.invariant_id == "I13"]
        assert len(i13) == 1
        assert i13[0].actual == Decimal("3000.00")


class TestReconcileIntegration:
    """reconcile() aggregates all invariant checks into one result."""

    def test_real_result_passes_all_invariants(self) -> None:
        """A genuine calculate_period result satisfies all 7 invariants."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert r.ok, f"Unexpected violations: {r.violations}"

    def test_second_period_passes_all_invariants(self) -> None:
        """A second-period result with non-zero opening state also passes."""
        r1, _ = _real_result(month=1)
        r2, op2 = _real_result(month=2, opening=r1.closing_state)
        assert reconcile(r2, op2).ok

    def test_violations_accumulate_across_invariants(self) -> None:
        """Multiple failing invariants produce multiple violations in one result."""
        orphan = _item("orphan", Decimal("100.00"))
        b = _Builder(
            period_gross=Decimal("9999.00"),
            pay_items=(orphan,),
            ledger_entries=(),
        )
        r = reconcile(b.build(), _OPENING)
        ids = {v.invariant_id for v in r.violations}
        assert "I1" in ids
        assert "I13" in ids
        assert not r.ok
