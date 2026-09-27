"""Integration tests for reconcile(): invariants hold on real period results."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.credit_accounts import TrattamentoAccount
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


def _real_result(
    month: int = 1, opening: PeriodState | None = None
) -> tuple[PeriodResult, PeriodState]:
    """Run a real calculation and return (result, opening_state).

    Returns:
        Tuple of the :class:`PeriodResult` and the
        :class:`PeriodState` that was used as the opening state.
    """
    op = opening or PeriodState.zero()
    req = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=op,
    )
    return calculate_period(req), op


_OPENING = PeriodState.zero()


class TestPayItemPosted:
    """pay_item_posted: every PayItem must have at least one matching LedgerEntry."""

    def test_no_violation_when_all_items_have_entries(self) -> None:
        """No pay_item_posted violation when every item has a ledger entry."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        found = [v for v in r.violations if v.invariant_id == "pay_item_posted"]
        assert found == []


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


class TestNetIdentity:
    """net_identity: cash + credits - contributions - taxes = period_net."""

    def test_no_violation_on_real_result(self) -> None:
        """No net_identity violation on a real calculate_period result."""
        result, opening = _real_result()
        assert reconcile(result, opening).ok


class TestIrpefWithheldContinuity:
    """irpef_withheld_continuity: closing IRPEF delta equals ORDINARY_TAX."""

    def test_no_violation_on_real_result(self) -> None:
        """No irpef_withheld_continuity violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "irpef_withheld_continuity"
        ] == []


class TestStateTransition:
    """Closing state must advance each counter and YTD field correctly."""

    def test_no_violation_on_real_result(self) -> None:
        """No counter or YTD violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        codes = {"run_counters_advance", "ytd_continuity"}
        assert [v for v in r.violations if v.invariant_id in codes] == []


class TestEmployerCostIdentity:
    """employer_cost_identity: earnings + benefits + employer contributions + TFR."""

    def test_no_violation_on_real_result(self) -> None:
        """No employer_cost_identity violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
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


class TestLedgerEntryUnique:
    """ledger_entry_unique: all ledger entry IDs within a period must be unique."""

    def test_no_violation_on_real_result(self) -> None:
        """No ledger_entry_unique violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
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


class TestOrdinaryTaxNonNegative:
    """ordinary_tax_non_negative: every ORDINARY_TAX entry is >= 0."""

    def test_no_violation_on_real_result(self) -> None:
        """No ordinary_tax_non_negative violation on a real calculate_period result."""
        result, opening = _real_result()
        r = reconcile(result, opening)
        assert [
            v for v in r.violations if v.invariant_id == "ordinary_tax_non_negative"
        ] == []


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
