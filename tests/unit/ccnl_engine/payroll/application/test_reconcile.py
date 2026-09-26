"""Unit tests for reconcile(): ledger, sign and state invariants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityReport
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
    reconcile,
)
from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.tax import TaxComputation
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    TaxYtd,
    TrattamentoAccount,
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
                ytd=TaxYearState(
                    regular_periods_closed=self.closing_months,
                    tax_withholding_periods_closed=self.closing_months,
                    tax=TaxYtd(irpef=self.closing_irpef),
                    earnings=EarningsYtd(
                        inps_employee=self.closing_inps,
                        gross=self.closing_gross,
                    ),
                )
            ),
            pay_items=self.pay_items,
            ledger_entries=self.ledger_entries,
            capability_report=CapabilityReport.empty(_YEAR),
            contribution_breakdown=ContributionBreakdown(
                employee=Decimal(0), employer=Decimal(0), components=()
            ),
            tax_computation=TaxComputation(
                ordinary_tax=Decimal(0),
                trattamento_integrativo=Decimal(0),
                withholding_due=Decimal(0),
                components=(),
            ),
            benefit_breakdown=BenefitBreakdown(
                value=Decimal(0),
                cash=Decimal(0),
                irpef_base=Decimal(0),
                inps_base=Decimal(0),
                employer_cost=Decimal(0),
            ),
        )


_OPENING = PeriodState.zero()


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

    def test_no_violation_when_all_items_have_entries(self) -> None:
        """No pay_item_posted violation when every item has a ledger entry."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        found = [v for v in r.violations if v.invariant_id == "pay_item_posted"]
        assert found == []

    def test_violation_when_item_has_no_entry(self) -> None:
        """pay_item_posted violation for a PayItem with no matching LedgerEntry."""
        orphan = _item("orphan_item", Decimal("100.00"))
        b = _Builder(
            pay_items=(orphan,),
            ledger_entries=(),
            closing_months=1,
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "pay_item_posted"]
        assert len(found) == 1
        assert "orphan_item" in found[0].message


class TestEarningContributionExclusive:
    """earning_contribution_exclusive: no item posts to earnings and contributions."""

    def test_no_violation_on_real_result(self) -> None:
        """No earning_contribution_exclusive violation on a real result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v
            for v in r.violations
            if v.invariant_id == "earning_contribution_exclusive"
        ] == []

    def test_violation_when_item_in_both_accounts(self) -> None:
        """Violation when the same pay_item_id posts to conflicting accounts."""
        e1 = _entry("item_x", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e2 = _entry("item_x", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(ledger_entries=(e1, e2))
        r = reconcile(b.build(), _OPENING)
        found = [
            v
            for v in r.violations
            if v.invariant_id == "earning_contribution_exclusive"
        ]
        assert len(found) == 1
        assert "item_x" in found[0].message


class TestNetIdentity:
    """net_identity: cash + credits - contributions - taxes = period_net."""

    def test_no_violation_on_real_result(self) -> None:
        """No net_identity violation on a real calculate_period result."""
        result, opening = _real_result()
        assert reconcile(result, opening).ok

    def test_violation_when_net_does_not_match(self) -> None:
        """net_identity violation when period_net disagrees with the ledger identity."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_tax = _entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        e_inps = _entry("i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(
            period_net=Decimal("9999.00"),
            ledger_entries=(e_cash, e_tax, e_inps),
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "net_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("2200.00")


class TestIrpefWithheldContinuity:
    """irpef_withheld_continuity: closing IRPEF delta equals ORDINARY_TAX."""

    def test_no_violation_on_real_result(self) -> None:
        """No irpef_withheld_continuity violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "irpef_withheld_continuity"
        ] == []

    def test_violation_when_delta_does_not_match(self) -> None:
        """Violation when the IRPEF delta diverges from the ORDINARY_TAX total."""
        e_tax = _entry("t", AccountKind.ORDINARY_TAX, Decimal("500.00"))
        b = _Builder(
            closing_irpef=Decimal("9999.00"),
            ledger_entries=(e_tax,),
        )
        r = reconcile(b.build(), _OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "irpef_withheld_continuity"
        ]
        assert len(found) == 1
        assert found[0].expected == Decimal("500.00")
        assert found[0].actual == Decimal("9999.00")


class TestStateTransition:
    """Closing state must advance each counter and YTD field correctly."""

    def test_no_violation_on_real_result(self) -> None:
        """No counter or YTD violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        codes = {"run_counters_advance", "ytd_continuity"}
        assert [v for v in r.violations if v.invariant_id in codes] == []

    def test_violation_when_regular_periods_closed_wrong(self) -> None:
        """run_counters_advance violation for a wrong regular_periods_closed."""
        b = _Builder(closing_months=2)  # expected 1 for the first period
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "run_counters_advance"]
        msgs = [v.message for v in found]
        assert any("regular_periods_closed" in m for m in msgs)

    def test_violation_when_gross_ytd_wrong(self) -> None:
        """ytd_continuity violation when gross_ytd is not correctly accumulated."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = _Builder(
            closing_gross=Decimal("9999.00"),
            ledger_entries=(e_cash,),
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "ytd_continuity"]
        msgs = [v.message for v in found]
        assert any("gross_ytd" in m for m in msgs)

    def test_violation_when_inps_ytd_wrong(self) -> None:
        """ytd_continuity violation when inps_employee_ytd is wrongly accumulated."""
        e_inps = _entry("i", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("300.00"))
        b = _Builder(
            closing_inps=Decimal("9999.00"),
            ledger_entries=(e_inps,),
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "ytd_continuity"]
        msgs = [v.message for v in found]
        assert any("inps_employee_ytd" in m for m in msgs)


class TestEmployerCostIdentity:
    """employer_cost_identity: earnings + benefits + employer contributions + TFR."""

    def test_no_violation_on_real_result(self) -> None:
        """No employer_cost_identity violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "employer_cost_identity"
        ] == []

    def test_violation_when_employer_cost_wrong(self) -> None:
        """Violation when period_employer_cost diverges from the ledger identity."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_empl = _entry("e", AccountKind.EMPLOYER_CONTRIBUTIONS, Decimal("300.00"))
        e_tfr = _entry("t", AccountKind.TFR_ACCRUAL, Decimal("100.00"))
        b = _Builder(
            period_employer_cost=Decimal("9999.00"),
            ledger_entries=(e_cash, e_empl, e_tfr),
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "employer_cost_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("3400.00")

    def test_non_cash_benefits_included_in_employer_cost(self) -> None:
        """NON_CASH_BENEFITS entries count toward employer cost identity."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        e_ncb = _entry("n", AccountKind.NON_CASH_BENEFITS, Decimal("200.00"))
        e_empl = _entry("e", AccountKind.EMPLOYER_CONTRIBUTIONS, Decimal("300.00"))
        e_tfr = _entry("t", AccountKind.TFR_ACCRUAL, Decimal("100.00"))
        b = _Builder(
            period_employer_cost=Decimal("3600.00"),
            ledger_entries=(e_cash, e_ncb, e_empl, e_tfr),
        )
        r = reconcile(b.build(), _OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "employer_cost_identity"
        ] == []


class TestGrossIdentity:
    """gross_identity: period_gross must equal the CASH_EARNINGS ledger total."""

    def test_no_violation_on_real_result(self) -> None:
        """No gross_identity violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "gross_identity"] == []

    def test_violation_when_gross_does_not_match(self) -> None:
        """gross_identity violation when period_gross diverges from CASH_EARNINGS."""
        e_cash = _entry("s", AccountKind.CASH_EARNINGS, Decimal("3000.00"))
        b = _Builder(period_gross=Decimal("9999.00"), ledger_entries=(e_cash,))
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "gross_identity"]
        assert len(found) == 1
        assert found[0].actual == Decimal("3000.00")


class TestLedgerEntryUnique:
    """ledger_entry_unique: all ledger entry IDs within a period must be unique."""

    def test_no_violation_on_real_result(self) -> None:
        """No ledger_entry_unique violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "ledger_entry_unique"
        ] == []

    def test_violation_on_duplicate_entry_id(self) -> None:
        """ledger_entry_unique violation when an entry_id appears twice."""
        e1 = _entry("item_a", AccountKind.CASH_EARNINGS, Decimal("1000.00"))
        e2 = LedgerEntry(
            entry_id="e_item_a",
            competence_period=_CP,
            payment_date=_PAYMENT,
            pay_item_id="item_b",
            pay_item_kind="base_salary_earning",
            account=AccountKind.ORDINARY_TAX,
            amount=Decimal("200.00"),
        )
        b = _Builder(
            period_gross=Decimal("1000.00"),
            period_net=Decimal("800.00"),
            ledger_entries=(e1, e2),
        )
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "ledger_entry_unique"]
        assert len(found) == 1
        assert "e_item_a" in found[0].message

    def test_no_violation_when_ids_unique(self) -> None:
        """No ledger_entry_unique violation when entry IDs are all distinct."""
        e1 = _entry("item_x", AccountKind.CASH_EARNINGS, Decimal("1000.00"))
        e2 = _entry("item_y", AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal("100.00"))
        b = _Builder(
            period_gross=Decimal("1000.00"),
            period_net=Decimal("900.00"),
            ledger_entries=(e1, e2),
        )
        r = reconcile(b.build(), _OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "ledger_entry_unique"
        ] == []


class TestGrossNonNegative:
    """gross_non_negative: period_gross must be non-negative."""

    def test_no_violation_on_real_result(self) -> None:
        """No gross_non_negative violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [v for v in r.violations if v.invariant_id == "gross_non_negative"] == []

    def test_violation_when_gross_is_negative(self) -> None:
        """gross_non_negative violation when period_gross is negative."""
        b = _Builder(period_gross=Decimal("-100.00"))
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == "gross_non_negative"]
        assert len(found) == 1
        assert found[0].actual == Decimal("-100.00")

    def test_no_violation_when_gross_is_zero(self) -> None:
        """No gross_non_negative violation when period_gross is exactly zero."""
        b = _Builder(period_gross=Decimal(0))
        r = reconcile(b.build(), _OPENING)
        assert [v for v in r.violations if v.invariant_id == "gross_non_negative"] == []


class TestCreditRecoveryBounds:
    """credit_recovery_bounds: trattamento.recovered is in [0, recognized]."""

    def test_no_violation_on_real_result(self) -> None:
        """No credit_recovery_bounds violation on a genuine calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "credit_recovery_bounds"
        ] == []

    def test_violation_when_recovered_is_negative(self) -> None:
        """credit_recovery_bounds fires when trattamento.recovered is negative.

        A negative recovered value cannot be produced by the engine (which uses
        max(0, ...) when accumulating) but can appear in a synthetic or
        deserialized state with corrupted data.
        """
        neg_tratt = TrattamentoAccount()
        # Corrupt a valid account: the constructor rejects the value itself.
        object.__setattr__(neg_tratt, "recovered", Decimal("-10.00"))  # noqa: PLC2801
        result = _real_result()[0]
        bad_result = type(result)(
            period_id=result.period_id,
            payment_date=result.payment_date,
            period_gross=result.period_gross,
            period_net=result.period_net,
            period_employer_cost=result.period_employer_cost,
            closing_state=PeriodState(
                ytd=TaxYearState(
                    tax_year=result.closing_state.ytd.tax_year,
                    regular_periods_closed=result.closing_state.ytd.regular_periods_closed,
                    tax_withholding_periods_closed=(
                        result.closing_state.ytd.tax_withholding_periods_closed
                    ),
                    closed_run_ids=result.closing_state.ytd.closed_run_ids,
                    earnings=result.closing_state.ytd.earnings,
                    fringe=result.closing_state.ytd.fringe,
                    tax=result.closing_state.ytd.tax,
                    trattamento=neg_tratt,
                    somma_esente=result.closing_state.ytd.somma_esente,
                )
            ),
            pay_items=result.pay_items,
            ledger_entries=result.ledger_entries,
            capability_report=result.capability_report,
            contribution_breakdown=result.contribution_breakdown,
            tax_computation=result.tax_computation,
            benefit_breakdown=result.benefit_breakdown,
            run=result.run,
        )
        violations = reconcile(bad_result, _OPENING).violations
        found = [v for v in violations if v.invariant_id == "credit_recovery_bounds"]
        assert len(found) == 1


class TestSubstituteTaxNonNegative:
    """substitute_tax_non_negative: every SUBSTITUTE_TAX entry is >= 0."""

    def test_no_violation_on_real_result(self) -> None:
        """No substitute_tax_non_negative violation on a real result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "substitute_tax_non_negative"
        ] == []

    def test_violation_on_negative_substitute_tax(self) -> None:
        """Violation when a SUBSTITUTE_TAX entry has a negative amount."""
        e = _entry("st", AccountKind.SUBSTITUTE_TAX, Decimal("-50.00"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "substitute_tax_non_negative"
        ]
        assert len(found) == 1
        assert "st" in found[0].message

    def test_no_violation_for_zero_substitute_tax(self) -> None:
        """Zero SUBSTITUTE_TAX is not a violation."""
        e = _entry("st", AccountKind.SUBSTITUTE_TAX, Decimal("0.00"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
        assert [
            v for v in r.violations if v.invariant_id == "substitute_tax_non_negative"
        ] == []


class TestOrdinaryTaxNonNegative:
    """ordinary_tax_non_negative: every ORDINARY_TAX entry is >= 0."""

    def test_no_violation_on_real_result(self) -> None:
        """No ordinary_tax_non_negative violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "ordinary_tax_non_negative"
        ] == []

    def test_violation_on_negative_ordinary_tax(self) -> None:
        """Violation when an ORDINARY_TAX entry has a negative amount."""
        e = _entry("irpef", AccountKind.ORDINARY_TAX, Decimal("-100.00"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
        found = [
            v for v in r.violations if v.invariant_id == "ordinary_tax_non_negative"
        ]
        assert len(found) == 1
        assert "irpef" in found[0].message

    def test_no_violation_for_zero_ordinary_tax(self) -> None:
        """Zero ORDINARY_TAX is not a violation."""
        e = _entry("irpef", AccountKind.ORDINARY_TAX, Decimal("0.00"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
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

    def test_no_violation_on_real_result(self) -> None:
        """No contribution sign violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v
            for v in r.violations
            if v.invariant_id
            in {
                "employee_contribution_non_negative",
                "employer_contribution_non_negative",
            }
        ] == []

    @pytest.mark.parametrize(("account", "invariant_id"), _CONTRIBUTION_INVARIANTS)
    def test_violation_on_negative_contribution(
        self, account: AccountKind, invariant_id: str
    ) -> None:
        """A negative contribution entry is reported with its pay item id."""
        e = _entry("inps", account, Decimal("-68.80"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
        found = [v for v in r.violations if v.invariant_id == invariant_id]
        assert len(found) == 1
        assert "inps" in found[0].message

    @pytest.mark.parametrize(("account", "invariant_id"), _CONTRIBUTION_INVARIANTS)
    def test_no_violation_for_zero_contribution(
        self, account: AccountKind, invariant_id: str
    ) -> None:
        """A zero contribution is not a violation."""
        e = _entry("inps", account, Decimal("0.00"))
        b = _Builder(ledger_entries=(e,))
        r = reconcile(b.build(), _OPENING)
        assert [v for v in r.violations if v.invariant_id == invariant_id] == []


class TestReconcileIntegration:
    """reconcile() aggregates all invariant checks into one result."""

    def test_real_result_passes_all_invariants(self) -> None:
        """A genuine calculate_period result satisfies all 9 invariants."""
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
        assert "pay_item_posted" in ids
        assert "gross_identity" in ids
        assert not r.ok
