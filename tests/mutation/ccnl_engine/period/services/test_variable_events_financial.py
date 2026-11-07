"""Integration tests for financial variable events.

Covers: arrears, bilateral fund, TFR, surtax, family deductions.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import (
    ArrearsEvent,
    BilateralFundEvent,
    TerminationTFREvent,
)
from ccnl_engine.family.inputs import (
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.run.types import PeriodId
from tests.integration.ccnl_engine.family.builders import (
    declared_dependent,
)
from tests.integration.ccnl_engine.surtax.builders import (
    opening_with_2025_surtax,
)

_CCNL = "metalmeccanico-federmeccanica"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)


def _req(*events: object) -> PeriodCalculationRequest:

    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_id=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
    )


def _base() -> PeriodCalculationRequest:
    return _req()


def _inps_employee(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        ),
        Decimal(0),
    )


def _sep_tax(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.SEPARATE_TAX
        ),
        Decimal(0),
    )


def _codes(result: PeriodResult, account: AccountKind) -> set[str | None]:
    return {e.remittance_code for e in result.ledger_entries if e.account == account}


def _surtax(result: PeriodResult) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == AccountKind.SURTAX),
        Decimal(0),
    )


#: Items of the contractual funds the CCNL owes on every run (mètaSalute of
#: the Metalmeccanico), apart from the bilateral fund event under test.
_FUNDS = ("metasalute_",)


def _event_trail(
    result: PeriodResult, accounts: set[AccountKind]
) -> list[tuple[AccountKind, str, str, str | None, Decimal]]:
    """Return how each entry of ``accounts`` traces to its pay item and policy.

    Returns:
        For each entry: its account, the kind of the item it was posted for
        (checked against the item itself), that item's quantity, the policy
        that governed it and the amount.
    """
    items = {item.item_id: item for item in result.pay_items}
    trail: list[tuple[AccountKind, str, str, str | None, Decimal]] = []
    for entry in result.ledger_entries:
        if entry.account not in accounts or entry.pay_item_id.startswith(_FUNDS):
            continue
        item = items[entry.pay_item_id]
        assert entry.pay_item_kind == item.kind
        trail.append((
            entry.account,
            item.kind,
            str(item.quantity),
            entry.policy_decision_id,
            entry.amount,
        ))
    return trail


def _tfr_settle(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.TFR_SETTLEMENT
        ),
        Decimal(0),
    )


def _req_surtax(*events: object) -> PeriodCalculationRequest:
    """Request with Lombardia region, comune A001 and the 2025 surtax.

    Returns:
        A :class:`PeriodCalculationRequest` with Lombardia region and comune
        A001, opening with the 2025 surtax still to withhold.
    """
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_id=_CCNL,
        level_code=_LEVEL,
        opening_state=opening_with_2025_surtax("IT-25", "A001"),
        events=tuple(events),  # type: ignore[arg-type]
        regione="IT-25",
        comune_belfiore="A001",
    )


def _req_family(*events: object) -> PeriodCalculationRequest:
    """Request with one fiscally dependent spouse.

    Returns:
        A :class:`PeriodCalculationRequest` with a spouse in family_composition.
    """
    spouse = declared_dependent(relationship=DependentRelationship.SPOUSE)
    family = FamilyComposition(dependents=(spouse,))
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_id=_CCNL,
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
            reference_period=PeriodId(year=_YEAR - 1, month=6),
        )

    def test_gross_increases(self) -> None:
        """period_gross increases by the arrears amount."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert result.period_gross == base.period_gross + Decimal("2000.00")

    def test_separate_tax_entry_posted(self) -> None:
        """A SEPARATE_TAX entry is posted for the computed tax."""
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert _sep_tax(result) > Decimal(0)

    def test_separate_tax_amount_correct(self) -> None:
        """SEPARATE_TAX equals amount * rate, rounded, remitted under 1002.

        1002 is "RITENUTE SU EMOLUMENTI ARRETRATI" (Allegato 1 to the AdE
        provvedimento of 31 January 2025).
        """
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        expected = (Decimal("2000.00") * Decimal("0.23")).quantize(Decimal("0.01"))
        assert _sep_tax(result) == expected
        assert _codes(result, AccountKind.SEPARATE_TAX) == {"1002"}

    def test_inps_increases_with_arrears(self) -> None:
        """Arrears increment the INPS base when policy contribution is 'included'."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert _inps_employee(result) > _inps_employee(base)

    def test_pay_item_present(self) -> None:
        """A contract_renewal_arrears pay item is present."""
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        kinds = {pi.kind for pi in result.pay_items}
        assert "contract_renewal_arrears" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for an arrears period."""
        result = calculate_period(
            _req(self._arrears()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
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
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert result.period_gross == base.period_gross

    def test_bilateral_fund_employee_account_posted(self) -> None:
        """BILATERAL_FUND_EMPLOYEE carries the employee bilateral amount."""
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        total = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.BILATERAL_FUND_EMPLOYEE
        )
        assert total == Decimal("30.00")

    def test_bilateral_fund_employer_account_posted(self) -> None:
        """BILATERAL_FUND_EMPLOYER carries the employer bilateral amount."""
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        total = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.BILATERAL_FUND_EMPLOYER
            and not e.pay_item_id.startswith(_FUNDS)
        )
        assert total == Decimal("50.00")

    def test_net_reduced_by_employee_amount(self) -> None:
        """period_net decreases by the employee bilateral amount."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert result.period_net == base.period_net - Decimal("30.00")

    def test_employer_cost_increases_by_employer_amount(self) -> None:
        """period_employer_cost increases by the employer bilateral amount."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert result.period_employer_cost == base.period_employer_cost + Decimal(
            "50.00"
        )

    def test_each_entry_traces_to_one_unit_of_its_item_and_its_policy(self) -> None:
        """The worker share is a withholding, the employer share a contribution."""
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )

        assert _event_trail(
            result,
            {AccountKind.BILATERAL_FUND_EMPLOYEE, AccountKind.BILATERAL_FUND_EMPLOYER},
        ) == [
            (
                AccountKind.BILATERAL_FUND_EMPLOYEE,
                "employee_withholding_item",
                "1",
                "it/contribution/employee",
                Decimal("30.00"),
            ),
            (
                AccountKind.BILATERAL_FUND_EMPLOYER,
                "employer_contribution_item",
                "1",
                "it/contribution/employer",
                Decimal("50.00"),
            ),
        ]

    def test_two_pay_items_produced(self) -> None:
        """BilateralFundEvent produces two pay items (employee + employer)."""
        base_result = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert len(result.pay_items) == len(base_result.pay_items) + 2

    def test_two_ledger_entries_produced(self) -> None:
        """BilateralFundEvent produces two ledger entries."""
        base_result = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert len(result.ledger_entries) == len(base_result.ledger_entries) + 2

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a bilateral fund period."""
        result = calculate_period(
            _req(self._bilateral()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
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
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert result.period_gross == base.period_gross

    def test_tfr_settlement_entry_posted(self) -> None:
        """A TFR_SETTLEMENT ledger entry is posted."""
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        assert _tfr_settle(result) == Decimal("5000.00")

    def test_separate_tax_entry_posted(self) -> None:
        """A SEPARATE_TAX entry is posted for the tassazione separata.

        It is remitted under 1012, "RITENUTE SU INDENNITA' PER CESSAZIONE DI
        RAPPORTO DI LAVORO" (Allegato 1 to the AdE provvedimento of 31
        January 2025).
        """
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        expected = (Decimal("5000.00") * Decimal("0.20")).quantize(Decimal("0.01"))
        assert _sep_tax(result) == expected
        assert _codes(result, AccountKind.SEPARATE_TAX) == {"1012"}

    def test_net_increases_by_tfr_minus_tax(self) -> None:
        """period_net increases by TFR settlement minus its separate tax."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        sep = (Decimal("5000.00") * Decimal("0.20")).quantize(Decimal("0.01"))
        assert result.period_net == base.period_net + Decimal("5000.00") - sep

    def test_payout_and_tax_trace_to_one_settlement_under_its_policy(self) -> None:
        """The payout and its separate tax both trace to the one settlement."""
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )

        assert _event_trail(
            result, {AccountKind.TFR_SETTLEMENT, AccountKind.SEPARATE_TAX}
        ) == [
            (
                AccountKind.TFR_SETTLEMENT,
                "tfr_settlement_item",
                "1",
                "it/tfr/settlement",
                Decimal("5000.00"),
            ),
            (
                AccountKind.SEPARATE_TAX,
                "tfr_settlement_item",
                "1",
                "it/tfr/settlement",
                Decimal("1000.00"),
            ),
        ]

    def test_pay_item_present(self) -> None:
        """A tfr_settlement_item pay item is present."""
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        kinds = {pi.kind for pi in result.pay_items}
        assert "tfr_settlement_item" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a termination TFR period."""
        result = calculate_period(
            _req(self._termination()),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestSurtaxAccounting:
    """Addizionali regionale/comunale post to SURTAX, not ORDINARY_TAX."""

    def test_surtax_entry_posted_when_regione_set(self) -> None:
        """A SURTAX ledger entry appears when regione is supplied."""
        result = calculate_period(
            _req_surtax(), repo=bundled_repository(), resolver=bundled_policies()
        )
        assert _surtax(result) > Decimal(0)

    def test_surtax_absent_without_regione(self) -> None:
        """No SURTAX entry when regione and comune_belfiore are not supplied."""
        result = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        assert _surtax(result) == Decimal(0)

    def test_ordinary_tax_not_inflated_by_surtax(self) -> None:
        """ORDINARY_TAX total is the same with or without surtax supplied."""
        base_irpef = sum(
            e.amount
            for e in calculate_period(
                _base(), repo=bundled_repository(), resolver=bundled_policies()
            ).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        surtax_irpef = sum(
            e.amount
            for e in calculate_period(
                _req_surtax(), repo=bundled_repository(), resolver=bundled_policies()
            ).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert base_irpef == surtax_irpef

    def test_surtax_pay_items_present(self) -> None:
        """One item per surtax component due on the run."""
        result = calculate_period(
            _req_surtax(), repo=bundled_repository(), resolver=bundled_policies()
        )
        surtax_items = {
            pi.item_id.rsplit("_", 1)[0]: pi.amount
            for pi in result.pay_items
            if "surtax" in pi.item_id
        }
        assert set(surtax_items) >= {
            "surtax_regional_balance_2025",
            "surtax_municipal_balance_2025",
        }
        assert sum(surtax_items.values()) == _surtax(result)

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold when addizionali are computed."""
        request = _req_surtax()
        result = calculate_period(
            request, repo=bundled_repository(), resolver=bundled_policies()
        )
        r = reconcile(result, request.opening_state)
        assert r.ok, r.violations


class TestFamilyDeductionsAccounting:
    """family_composition reduces IRPEF via Art. 12 TUIR deductions."""

    def test_net_increases_with_spouse_deduction(self) -> None:
        """Declaring a dependent spouse increases period_net."""
        base = calculate_period(
            _base(), repo=bundled_repository(), resolver=bundled_policies()
        )
        result = calculate_period(
            _req_family(), repo=bundled_repository(), resolver=bundled_policies()
        )
        assert result.period_net > base.period_net

    def test_ordinary_tax_decreases_with_spouse_deduction(self) -> None:
        """IRPEF withheld decreases when family deductions apply."""
        base_irpef = sum(
            e.amount
            for e in calculate_period(
                _base(), repo=bundled_repository(), resolver=bundled_policies()
            ).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        family_irpef = sum(
            e.amount
            for e in calculate_period(
                _req_family(), repo=bundled_repository(), resolver=bundled_policies()
            ).ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert family_irpef < base_irpef

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold when family deductions are applied."""
        result = calculate_period(
            _req_family(), repo=bundled_repository(), resolver=bundled_policies()
        )
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


def _arrears_of(reference: PeriodId | None) -> PeriodResult:
    return calculate_period(
        _req(
            ArrearsEvent(
                event_date=date(_YEAR, _MONTH, 28),
                amount=Decimal("2000.00"),
                separate_tax_rate=Decimal("0.23"),
                reference_period=reference,
            )
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _arrears_trail(
    result: PeriodResult,
) -> tuple[object, ...]:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "contract_renewal_arrears"
        and d.reason_code != "caller_supplied_rate"
    )
    (item,) = (i for i in result.pay_items if i.kind == "contract_renewal_arrears")
    entries = {
        e.account: (e.amount, e.policy_decision_id)
        for e in result.ledger_entries
        if e.pay_item_id == item.item_id
    }
    return (
        decision.reason_code,
        decision.status.value,
        decision.rule_version,
        dict(decision.inputs),
        decision.amount,
        item.quantity,
        entries,
    )


_ARREARS = "it/earning/arrears"


@pytest.mark.parametrize(
    ("reference", "reason", "status", "shown", "amount", "taxed"),
    [
        (
            PeriodId(year=_YEAR, month=1),
            "ordinary_taxation",
            "final",
            "2026-01",
            "2000.00",
            False,
        ),
        (
            PeriodId(year=_YEAR - 1, month=6),
            "separate_taxation",
            "final",
            "2025-06",
            "460.00",
            True,
        ),
        (None, "reference_period_unknown", "incomplete", "unknown", "460.00", True),
    ],
    ids=["this_year", "earlier_year", "unknown_year"],
)
def test_arrears_trace_their_year_tax_and_policy(
    reference: PeriodId | None,
    reason: str,
    status: str,
    shown: str,
    amount: str,
    taxed: bool,
) -> None:
    """Art. 17 c. 1 lett. b TUIR: only arrears of earlier years are taxed apart."""
    entries = {AccountKind.CASH_EARNINGS: (Decimal("2000.00"), _ARREARS)}
    if taxed:
        entries[AccountKind.SEPARATE_TAX] = (Decimal("460.00"), _ARREARS)

    assert _arrears_trail(_arrears_of(reference)) == (
        reason,
        status,
        str(_YEAR),
        {
            "tax_year": str(_YEAR),
            "reference_period": shown,
            "amount": Decimal("2000.00"),
            **(
                {"separate_tax_rate": Decimal("0.23"), "rate_source": "caller"}
                if taxed
                else {}
            ),
        },
        Decimal(amount),
        Decimal(1),
        entries,
    )


def test_arrears_of_the_year_are_ordinary_income_with_their_contributions() -> None:
    """All arrears bear INPS; only those of the year enter the IRPEF base."""
    base = calculate_period(
        _base(), repo=bundled_repository(), resolver=bundled_policies()
    )
    this_year = _arrears_of(PeriodId(year=_YEAR, month=1))
    earlier = _arrears_of(PeriodId(year=_YEAR - 1, month=6))

    def contributions(result: PeriodResult) -> Decimal:
        return sum(
            (
                e.amount
                for e in result.ledger_entries
                if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
            ),
            Decimal(0),
        )

    assert contributions(this_year) == contributions(earlier) > contributions(base)
    taxable = this_year.closing_state.cash.earnings.taxable
    assert taxable - earlier.closing_state.cash.earnings.taxable == Decimal("2000.00")


def test_arrears_of_an_unknown_year_name_the_event_in_their_issue() -> None:
    """The missing fact names the event and the law of the separate tax."""
    result = _arrears_of(None)
    (issue,) = (
        i for i in result.issues if i.code == "arrears_reference_period_unknown"
    )

    assert issue.message.startswith(
        "ArrearsEvent 2026-03-regular_evt0 states no reference_period: arrears "
        "of an earlier year are taxed separately (art. 17 c. 1 lett. b TUIR)"
    )


def test_arrears_of_a_year_not_begun_name_the_event_and_field() -> None:
    """A reference period after the tax year of the run is rejected."""
    with pytest.raises(InvalidInputError) as raised:
        _arrears_of(PeriodId(year=_YEAR + 1, month=2))

    assert raised.value.field == "ArrearsEvent.reference_period"
    assert raised.value.feature == "contract_renewal_arrears"
    assert str(raised.value).startswith(
        "ArrearsEvent 2026-03-regular_evt0 refers to 2027-02, after the tax "
        "year 2026 of the run"
    )
