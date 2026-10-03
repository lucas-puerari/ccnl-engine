"""Unit tests for PeriodId, PeriodCalculationRequest and PeriodResult."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.capability_report import CapabilityReport
from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
)
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.domain.tax import TaxComputation
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    TaxYtd,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_ZERO = Decimal(0)
_PERIOD = PeriodId(year=2026, month=1)
_DATE = date(2026, 1, 31)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"


def _make_result(**kwargs: object) -> PeriodResult:
    defaults: dict[str, object] = {
        "period_id": _PERIOD,
        "payment_date": _DATE,
        "period_gross": Decimal("2158.26"),
        "period_net": Decimal("1674.42"),
        "period_employer_cost": Decimal("2969.92"),
        "closing_state": PeriodState(cash=TaxCashState(withholding_payments_closed=1)),
        "pay_items": (),
        "ledger_entries": (),
        "capability_report": CapabilityReport.empty(2026),
        "contribution_breakdown": ContributionBreakdown(
            employee=_ZERO, employer=_ZERO, components=()
        ),
        "tax_computation": TaxComputation(
            ordinary_tax=_ZERO,
            trattamento_integrativo=_ZERO,
            withholding_due=_ZERO,
            components=(),
        ),
        "benefit_breakdown": BenefitBreakdown(
            value=_ZERO,
            cash=_ZERO,
            irpef_base=_ZERO,
            inps_base=_ZERO,
            employer_cost=_ZERO,
        ),
    }
    defaults.update(kwargs)
    return PeriodResult(**defaults)  # type: ignore[arg-type]


class TestPeriodId:
    """PeriodId validates year and month ranges and is immutable."""

    def test_stores_year_and_month(self) -> None:
        """Year and month are stored as provided."""
        pid = PeriodId(year=2026, month=3)
        assert pid.year == 2026
        assert pid.month == 3

    def test_month_zero_raises(self) -> None:
        """month=0 raises ValueError."""
        with pytest.raises(InvalidInputError, match="month"):
            PeriodId(year=2026, month=0)

    def test_month_thirteen_raises(self) -> None:
        """month=13 raises ValueError."""
        with pytest.raises(InvalidInputError, match="month"):
            PeriodId(year=2026, month=13)

    def test_year_zero_raises(self) -> None:
        """year=0 raises ValueError."""
        with pytest.raises(InvalidInputError, match="year"):
            PeriodId(year=0, month=1)


class TestPeriodCalculationRequest:
    """PeriodCalculationRequest stores period, CCNL reference, and YTD state."""

    def test_stored_fields(self) -> None:
        """All explicitly supplied fields are stored and retrievable."""
        state = PeriodState(
            cash=TaxCashState(
                withholding_payments_closed=5,
                tax=TaxYtd(irpef=Decimal("1000.00")),
            )
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=state,
        )
        assert req.period_id == PeriodId(year=2026, month=6)
        assert req.payment_date == date(2026, 6, 28)
        assert req.ccnl_slug == _CCNL
        assert req.level_code == _LEVEL
        assert req.opening_state is state

    def test_default_opening_state_is_zero(self) -> None:
        """opening_state defaults to PeriodState.zero() when omitted."""
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        assert req.opening_state == PeriodState.zero()

    def test_default_employer(self) -> None:
        """The employer defaults to 50 employees when omitted."""
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        assert req.employer == EmployerProfile(headcount=Headcount(50))

    def test_frozen(self) -> None:
        """PeriodCalculationRequest is immutable: assignment raises AttributeError."""
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
        )
        with pytest.raises(AttributeError):
            req.level_code = "B2"  # type: ignore[misc]

    def test_year_guard_raises_when_tax_year_mismatch(self) -> None:
        """An opening state of another tax year raises InvalidInputError."""
        prior_year_state = PeriodState(
            cash=TaxCashState(
                tax_year=2025,
                withholding_payments_closed=12,
            )
        )
        with pytest.raises(InvalidInputError, match="opening_state is for tax year"):
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=1),
                payment_date=date(2026, 1, 31),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=prior_year_state,
            )

    def test_payment_before_period_start_raises(self) -> None:
        """A run cannot be paid before its competence period starts."""
        with pytest.raises(InvalidInputError, match="before the start"):
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=3),
                payment_date=date(2026, 2, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
            )

    def test_run_of_next_tax_year_rejects_current_year_state(self) -> None:
        """December paid on 13 January belongs to 2027, not to a 2026 state."""
        state_2026 = PeriodState(
            cash=TaxCashState(
                tax_year=2026,
                withholding_payments_closed=11,
            )
        )
        with pytest.raises(InvalidInputError, match="belongs to tax year 2027") as info:
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=12),
                payment_date=date(2027, 1, 13),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=state_2026,
            )
        assert info.value.feature == "tax_year"

    def test_run_paid_by_twelve_january_accepts_current_year_state(self) -> None:
        """December paid on 12 January stays in the 2026 state."""
        state_2026 = PeriodState(
            cash=TaxCashState(
                tax_year=2026,
                withholding_payments_closed=11,
            )
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=12),
            payment_date=date(2027, 1, 12),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=state_2026,
        )
        assert req.opening_state.tax_year == 2026

    def test_withholding_schedule_of_other_tax_year_raises(self) -> None:
        """The withholding schedule must belong to the attributed tax year."""
        with pytest.raises(InvalidInputError, match=r"withholding_schedule\.year"):
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(50)),
                period_id=PeriodId(year=2026, month=12),
                payment_date=date(2027, 1, 13),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                withholding_schedule=WithholdingSchedule.from_calendar(
                    WorkCalendar(year=2026)
                ),
            )

    def test_year_guard_passes_when_tax_year_none(self) -> None:
        """Manually constructed state with tax_year=None bypasses the year guard."""
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=_PERIOD,
            payment_date=_DATE,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        assert req.opening_state.tax_year is None

    def test_year_guard_passes_when_tax_year_matches(self) -> None:
        """opening_state.tax_year == period_id.year is accepted."""
        current_state = PeriodState(
            cash=TaxCashState(
                tax_year=2026,
                withholding_payments_closed=5,
            )
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=current_state,
        )
        assert req.opening_state.tax_year == 2026


class TestPeriodCalculationResult:
    """PeriodResult stores all output fields and is immutable."""

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
        cs = PeriodState(
            cash=TaxCashState(
                withholding_payments_closed=1,
                earnings=EarningsYtd(gross=Decimal("2158.26")),
            )
        )
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
        """PeriodResult is immutable: assignment raises AttributeError."""
        result = _make_result()
        with pytest.raises(AttributeError):
            result.period_net = Decimal(0)  # type: ignore[misc]
