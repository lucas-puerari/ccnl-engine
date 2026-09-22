"""Unit tests for PeriodState, PeriodCalculationRequest, PeriodCalculationResult."""

from __future__ import annotations

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
from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.tax import TaxComputation

_ZERO = Decimal(0)
_PERIOD = PeriodId(year=2026, month=1)
_DATE = date(2026, 1, 31)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"


def _make_result(**kwargs: object) -> PeriodCalculationResult:
    defaults: dict[str, object] = {
        "period_id": _PERIOD,
        "payment_date": _DATE,
        "period_gross": Decimal("2158.26"),
        "period_net": Decimal("1674.42"),
        "period_employer_cost": Decimal("2969.92"),
        "closing_state": PeriodState(months_closed=1),
        "pay_items": (),
        "ledger_entries": (),
        "capability_report": CapabilityReport.empty(2026),
        "contribution_breakdown": ContributionBreakdown(
            employee=_ZERO, employer=_ZERO, components=()
        ),
        "tax_computation": TaxComputation(
            ordinary_tax=_ZERO, trattamento_integrativo=_ZERO, components=()
        ),
    }
    defaults.update(kwargs)
    return PeriodCalculationResult(**defaults)  # type: ignore[arg-type]


class TestPeriodState:
    """PeriodState stores YTD progressives and provides a zero factory."""

    def test_zero_factory(self) -> None:
        """PeriodState.zero() returns a state with all fields at zero."""
        s = PeriodState.zero()
        assert s.months_closed == 0
        assert s.irpef_withheld_ytd == _ZERO
        assert s.inps_employee_ytd == _ZERO
        assert s.gross_ytd == _ZERO

    def test_stored_values(self) -> None:
        """All fields are stored and retrievable after construction."""
        s = PeriodState(
            months_closed=3,
            irpef_withheld_ytd=Decimal("837.06"),
            inps_employee_ytd=Decimal("614.46"),
            gross_ytd=Decimal("6474.78"),
        )
        assert s.months_closed == 3
        assert s.irpef_withheld_ytd == Decimal("837.06")
        assert s.inps_employee_ytd == Decimal("614.46")
        assert s.gross_ytd == Decimal("6474.78")

    def test_frozen(self) -> None:
        """PeriodState is immutable: attribute assignment raises AttributeError."""
        s = PeriodState.zero()
        with pytest.raises(AttributeError):
            s.months_closed = 1  # type: ignore[misc]


class TestPeriodCalculationRequest:
    """PeriodCalculationRequest stores period, CCNL reference, and YTD state."""

    def test_stored_fields(self) -> None:
        """All explicitly supplied fields are stored and retrievable."""
        state = PeriodState(months_closed=5, irpef_withheld_ytd=Decimal("1000.00"))
        req = PeriodCalculationRequest(
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=state,
        )
        assert req.period_id is _PERIOD
        assert req.payment_date == _DATE
        assert req.ccnl_slug == _CCNL
        assert req.level_code == _LEVEL
        assert req.opening_state is state

    def test_default_opening_state_is_zero(self) -> None:
        """opening_state defaults to PeriodState.zero() when omitted."""
        req = PeriodCalculationRequest(
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        assert req.opening_state == PeriodState.zero()

    def test_default_num_employees(self) -> None:
        """num_employees defaults to 50 when omitted."""
        req = PeriodCalculationRequest(
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        assert req.num_employees == 50

    def test_frozen(self) -> None:
        """PeriodCalculationRequest is immutable: assignment raises AttributeError."""
        req = PeriodCalculationRequest(
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        with pytest.raises(AttributeError):
            req.level_code = "B2"  # type: ignore[misc]


class TestPeriodCalculationResult:
    """PeriodCalculationResult stores all output fields and is immutable."""

    def test_stored_scalar_fields(self) -> None:
        """All scalar fields are stored and retrievable after construction."""
        result = _make_result()
        assert result.period_id == _PERIOD
        assert result.payment_date == _DATE
        assert result.period_gross == Decimal("2158.26")
        assert result.period_net == Decimal("1674.42")
        assert result.period_employer_cost == Decimal("2969.92")

    def test_stored_closing_state(self) -> None:
        """closing_state is stored by identity."""
        cs = PeriodState(months_closed=1, gross_ytd=Decimal("2158.26"))
        result = _make_result(closing_state=cs)
        assert result.closing_state is cs

    def test_pay_items_and_ledger_stored(self) -> None:
        """pay_items and ledger_entries tuples are stored by identity."""
        cp = CompetencePeriod(year=2026, month=1)
        item = BaseSalaryEarning(
            item_id="base_salary_2026_01",
            competence_period=cp,
            payment_date=_DATE,
            quantity=Decimal(1),
            amount=Decimal("2158.26"),
        )
        entry = LedgerEntry(
            entry_id="cash_earnings_2026_01",
            competence_period=cp,
            payment_date=_DATE,
            pay_item_id="base_salary_2026_01",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=Decimal("2158.26"),
        )
        result = _make_result(pay_items=(item,), ledger_entries=(entry,))
        assert len(result.pay_items) == 1
        assert result.pay_items[0] is item
        assert len(result.ledger_entries) == 1
        assert result.ledger_entries[0] is entry

    def test_frozen(self) -> None:
        """PeriodCalculationResult is immutable: assignment raises AttributeError."""
        result = _make_result()
        with pytest.raises(AttributeError):
            result.period_net = Decimal(0)  # type: ignore[misc]
