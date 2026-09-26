"""Pay items and ledger entries projected from the monthly pay chain."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.compensation import Allowance
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    FixedAllowanceEarning,
    SeniorityEarning,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)

_RESOLVER = load_policy_resolver()

_POLICY_CTX = PolicyContext(year=2026, as_of=date(2026, 1, 1))


def _amounts(*, period_tratt: Decimal = _ZERO) -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=Decimal("2158.26"),
        inps_employee=Decimal("204.82"),
        inps_employer=Decimal("651.79"),
        tfr=Decimal("159.87"),
        period_irpef=Decimal("279.02"),
        period_tratt=period_tratt,
        period_surtax=_ZERO,
        period_taxable=Decimal("1953.44"),
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
    )


def _chain() -> MonthlyPayChain:
    return MonthlyPayChain(base=Decimal("2158.26"), seniority=_ZERO, allowances=())


def _chain_with_seniority() -> MonthlyPayChain:
    return MonthlyPayChain(
        base=Decimal("2069.34"), seniority=Decimal("88.92"), allowances=()
    )


def _allowance(code: str = "EDR", amount: Decimal = Decimal("10.33")) -> Allowance:
    ts = TimeSeries(
        periods=(
            ValidityPeriod(value=amount, valid_from=date(2024, 1, 1), valid_until=None),
        )
    )
    return Allowance(code=code, description=code, monthly=ts)


def _chain_with_allowance() -> MonthlyPayChain:
    a = _allowance()
    return MonthlyPayChain(
        base=Decimal("2147.93"),
        seniority=_ZERO,
        allowances=((a, Decimal("10.33")),),
    )


class TestElementaryChainItems:
    """Elementary pay items and ledger entries from chain components."""

    def test_seniority_item_emitted_when_positive(self) -> None:
        """A SeniorityEarning is emitted when chain.seniority > 0."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(),
            _chain_with_seniority(),
            period_id,
            date(2026, 1, 31),
        )
        seniority_items = [i for i in items if isinstance(i, SeniorityEarning)]
        assert len(seniority_items) == 1
        assert seniority_items[0].amount == Decimal("88.92")

    def test_allowance_item_emitted_when_positive(self) -> None:
        """A FixedAllowanceEarning is emitted for each positive allowance."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(),
            _chain_with_allowance(),
            period_id,
            date(2026, 1, 31),
        )
        allowance_items = [i for i in items if isinstance(i, FixedAllowanceEarning)]
        assert len(allowance_items) == 1
        assert allowance_items[0].amount == Decimal("10.33")
        assert allowance_items[0].allowance_code == "EDR"

    def test_seniority_ledger_entry_emitted_when_positive(self) -> None:
        """A CASH_EARNINGS entry for seniority is posted when chain.seniority > 0."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(),
            _chain_with_seniority(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        cash_entries = [e for e in entries if e.account == AccountKind.CASH_EARNINGS]
        amounts = [e.amount for e in cash_entries]
        assert Decimal("88.92") in amounts

    def test_allowance_ledger_entry_emitted_when_positive(self) -> None:
        """A CASH_EARNINGS entry for each allowance is posted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(),
            _chain_with_allowance(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        cash_entries = [e for e in entries if e.account == AccountKind.CASH_EARNINGS]
        amounts = [e.amount for e in cash_entries]
        assert Decimal("10.33") in amounts

    def test_zero_allowance_not_emitted(self) -> None:
        """An allowance with amount == 0 produces no pay item or ledger entry."""
        a = _allowance(amount=_ZERO)
        chain = MonthlyPayChain(
            base=Decimal("2158.26"), seniority=_ZERO, allowances=((a, _ZERO),)
        )
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(_amounts(), chain, period_id, date(2026, 1, 31))
        entries = _project_ledger(
            _amounts(), chain, period_id, date(2026, 1, 31), _RESOLVER, _POLICY_CTX
        )
        assert not any(isinstance(i, FixedAllowanceEarning) for i in items)
        cash_amounts = [
            e.amount for e in entries if e.account == AccountKind.CASH_EARNINGS
        ]
        assert _ZERO not in cash_amounts


class TestProjectLedgerWithTrattamento:
    """_project_ledger includes CREDITS entry when period_tratt > 0."""

    def test_no_credits_entry_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no CREDITS ledger entry is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        accounts = [e.account for e in entries]
        assert AccountKind.CREDITS not in accounts

    def test_credits_entry_when_tratt_positive(self) -> None:
        """When period_tratt > 0, a CREDITS entry with correct amount is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=Decimal("92.31")),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        credit_entries = [e for e in entries if e.account == AccountKind.CREDITS]
        assert len(credit_entries) == 1
        assert credit_entries[0].amount == Decimal("92.31")

    def test_base_accounts_always_present(self) -> None:
        """All five base ledger accounts are always emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        accounts = {e.account for e in entries}
        assert AccountKind.CASH_EARNINGS in accounts
        assert AccountKind.EMPLOYEE_CONTRIBUTIONS in accounts
        assert AccountKind.ORDINARY_TAX in accounts
        assert AccountKind.EMPLOYER_CONTRIBUTIONS in accounts
        assert AccountKind.TFR_ACCRUAL in accounts
