"""Integration tests for financial variable events.

Covers: arrears, bilateral fund, TFR, surtax, family deductions.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.events import (
    ArrearsEvent,
    BilateralFundEvent,
    TerminationTFREvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)


def _req(*events: object) -> PeriodCalculationRequest:

    return PeriodCalculationRequest(
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
    )


def _base() -> PeriodCalculationRequest:
    return _req()


def _inps_employee(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        ),
        Decimal(0),
    )


def _employer_contrib(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYER_CONTRIBUTIONS
        ),
        Decimal(0),
    )


def _sep_tax(result: PeriodCalculationResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.SEPARATE_TAX
        ),
        Decimal(0),
    )


def _surtax(result: PeriodCalculationResult) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == AccountKind.SURTAX),
        Decimal(0),
    )


def _tfr_settle(result: PeriodCalculationResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.TFR_SETTLEMENT
        ),
        Decimal(0),
    )


def _req_surtax(*events: object) -> PeriodCalculationRequest:
    """Request with Lombardia region and comune A001 for surtax computation.

    Returns:
        A :class:`PeriodCalculationRequest` with Lombardia region and comune A001.
    """
    return PeriodCalculationRequest(
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
        regione="03",
        comune_belfiore="A001",
    )


def _req_family(*events: object) -> PeriodCalculationRequest:
    """Request with one fiscally dependent spouse.

    Returns:
        A :class:`PeriodCalculationRequest` with a spouse in family_composition.
    """
    spouse = Dependent(relationship=DependentRelationship.SPOUSE)
    family = FamilyComposition(dependents=(spouse,))
    return PeriodCalculationRequest(
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
        family_composition=family,
    )


class TestArrearsEventAccounting:
    """ArrearsEvent posts gross to CASH_EARNINGS and separate tax to SEPARATE_TAX."""

    def _arrears(self) -> ArrearsEvent:
        return ArrearsEvent(
            event_date=date(_YEAR, _MONTH, 28),
            amount=Decimal("2000.00"),
            separate_tax_rate=Decimal("0.23"),
        )

    def test_gross_increases(self) -> None:
        """period_gross increases by the arrears amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._arrears()))
        assert result.period_gross == base.period_gross + Decimal("2000.00")

    def test_separate_tax_entry_posted(self) -> None:
        """A SEPARATE_TAX entry is posted for the computed tax."""
        result = calculate_period(_req(self._arrears()))
        assert _sep_tax(result) > Decimal(0)

    def test_separate_tax_amount_correct(self) -> None:
        """SEPARATE_TAX equals amount * rate, rounded."""
        result = calculate_period(_req(self._arrears()))
        expected = (Decimal("2000.00") * Decimal("0.23")).quantize(Decimal("0.01"))
        assert _sep_tax(result) == expected

    def test_inps_not_affected(self) -> None:
        """Arrears do not flow through INPS (tassazione separata bypasses INPS)."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._arrears()))
        assert _inps_employee(result) == _inps_employee(base)

    def test_pay_item_present(self) -> None:
        """A contract_renewal_arrears pay item is present."""
        result = calculate_period(_req(self._arrears()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "contract_renewal_arrears" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for an arrears period."""
        result = calculate_period(_req(self._arrears()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestBilateralFundEventAccounting:
    """BilateralFundEvent posts employee deduction and employer contribution."""

    def _bilateral(self) -> BilateralFundEvent:
        return BilateralFundEvent(
            event_date=date(_YEAR, _MONTH, 28),
            employee_amount=Decimal("30.00"),
            employer_amount=Decimal("50.00"),
        )

    def test_gross_unchanged(self) -> None:
        """period_gross is not affected by bilateral fund contributions."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert result.period_gross == base.period_gross

    def test_employee_contributions_increase(self) -> None:
        """EMPLOYEE_CONTRIBUTIONS includes the employee bilateral amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert _inps_employee(result) == _inps_employee(base) + Decimal("30.00")

    def test_employer_contributions_increase(self) -> None:
        """EMPLOYER_CONTRIBUTIONS includes the employer bilateral amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert _employer_contrib(result) == _employer_contrib(base) + Decimal("50.00")

    def test_net_reduced_by_employee_amount(self) -> None:
        """period_net decreases by the employee bilateral amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert result.period_net == base.period_net - Decimal("30.00")

    def test_employer_cost_increases_by_employer_amount(self) -> None:
        """period_employer_cost increases by the employer bilateral amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert result.period_employer_cost == base.period_employer_cost + Decimal(
            "50.00"
        )

    def test_two_pay_items_produced(self) -> None:
        """BilateralFundEvent produces two pay items (employee + employer)."""
        base_result = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert len(result.pay_items) == len(base_result.pay_items) + 2

    def test_two_ledger_entries_produced(self) -> None:
        """BilateralFundEvent produces two ledger entries."""
        base_result = calculate_period(_base())
        result = calculate_period(_req(self._bilateral()))
        assert len(result.ledger_entries) == len(base_result.ledger_entries) + 2

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a bilateral fund period."""
        result = calculate_period(_req(self._bilateral()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestTerminationTFREventAccounting:
    """TerminationTFREvent posts TFR settlement and separate tax."""

    def _termination(self) -> TerminationTFREvent:
        return TerminationTFREvent(
            event_date=date(_YEAR, _MONTH, 28),
            amount=Decimal("5000.00"),
            separate_tax_rate=Decimal("0.20"),
        )

    def test_gross_unchanged(self) -> None:
        """period_gross is not affected by TFR settlement."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._termination()))
        assert result.period_gross == base.period_gross

    def test_tfr_settlement_entry_posted(self) -> None:
        """A TFR_SETTLEMENT ledger entry is posted."""
        result = calculate_period(_req(self._termination()))
        assert _tfr_settle(result) == Decimal("5000.00")

    def test_separate_tax_entry_posted(self) -> None:
        """A SEPARATE_TAX entry is posted for the tassazione separata."""
        result = calculate_period(_req(self._termination()))
        expected = (Decimal("5000.00") * Decimal("0.20")).quantize(Decimal("0.01"))
        assert _sep_tax(result) == expected

    def test_net_increases_by_tfr_minus_tax(self) -> None:
        """period_net increases by TFR settlement minus its separate tax."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._termination()))
        sep = (Decimal("5000.00") * Decimal("0.20")).quantize(Decimal("0.01"))
        assert result.period_net == base.period_net + Decimal("5000.00") - sep

    def test_pay_item_present(self) -> None:
        """A tfr_settlement_item pay item is present."""
        result = calculate_period(_req(self._termination()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "tfr_settlement_item" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a termination TFR period."""
        result = calculate_period(_req(self._termination()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestSurtaxAccounting:
    """Addizionali regionale/comunale post to SURTAX, not ORDINARY_TAX."""

    def test_surtax_entry_posted_when_regione_set(self) -> None:
        """A SURTAX ledger entry appears when regione is supplied."""
        result = calculate_period(_req_surtax())
        assert _surtax(result) > Decimal(0)

    def test_surtax_absent_without_regione(self) -> None:
        """No SURTAX entry when regione and comune_belfiore are not supplied."""
        result = calculate_period(_base())
        assert _surtax(result) == Decimal(0)

    def test_ordinary_tax_not_inflated_by_surtax(self) -> None:
        """ORDINARY_TAX total is the same with or without surtax supplied."""
        base_irpef = sum(
            e.amount
            for e in calculate_period(_base()).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        surtax_irpef = sum(
            e.amount
            for e in calculate_period(_req_surtax()).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert base_irpef == surtax_irpef

    def test_surtax_pay_item_present(self) -> None:
        """An EmployeeWithholdingItem with 'surtax' in id appears when surtax > 0."""
        result = calculate_period(_req_surtax())
        surtax_items = [pi for pi in result.pay_items if "surtax" in pi.item_id]
        assert len(surtax_items) == 1

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold when addizionali are computed."""
        result = calculate_period(_req_surtax())
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestFamilyDeductionsAccounting:
    """family_composition reduces IRPEF via Art. 12 TUIR deductions."""

    def test_net_increases_with_spouse_deduction(self) -> None:
        """Declaring a dependent spouse increases period_net."""
        base = calculate_period(_base())
        result = calculate_period(_req_family())
        assert result.period_net > base.period_net

    def test_ordinary_tax_decreases_with_spouse_deduction(self) -> None:
        """IRPEF withheld decreases when family deductions apply."""
        base_irpef = sum(
            e.amount
            for e in calculate_period(_base()).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        family_irpef = sum(
            e.amount
            for e in calculate_period(_req_family()).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert family_irpef < base_irpef

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold when family deductions are applied."""
        result = calculate_period(_req_family())
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations
