"""_build_pay_items turns period amounts into typed pay items."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
)
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    TaxCreditItem,
    TfrAccrualItem,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)


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


class TestBuildPayItemsWithTrattamento:
    """_build_pay_items includes TaxCreditItem when period_tratt > 0."""

    def test_no_tax_credit_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no TaxCreditItem is emitted."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
        )
        assert not any(isinstance(i, TaxCreditItem) for i in items)

    def test_tax_credit_included_when_tratt_positive(self) -> None:
        """When period_tratt > 0, exactly one TaxCreditItem with correct amount."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=Decimal("92.31")),
            _chain(),
            period_id,
            date(2026, 1, 31),
        )
        credit_items = [i for i in items if isinstance(i, TaxCreditItem)]
        assert len(credit_items) == 1
        assert credit_items[0].amount == Decimal("92.31")

    def test_base_items_always_present(self) -> None:
        """Base, INPS, IRPEF, employer, and TFR items are always present."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
        )
        assert any(isinstance(i, BaseSalaryEarning) for i in items)
        assert any(isinstance(i, EmployeeWithholdingItem) for i in items)
        assert any(isinstance(i, EmployerContributionItem) for i in items)
        assert any(isinstance(i, TfrAccrualItem) for i in items)
