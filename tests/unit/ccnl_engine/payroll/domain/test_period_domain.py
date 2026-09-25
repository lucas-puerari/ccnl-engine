"""Unit tests for PeriodState, PeriodCalculationRequest, PeriodCalculationResult."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityReport
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
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    TaxYtd,
)

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
        "closing_state": PeriodState(
            regular_periods_closed=1, tax_withholding_periods_closed=1
        ),
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
    return PeriodCalculationResult(**defaults)  # type: ignore[arg-type]


class TestPeriodId:
    """PeriodId validates year and month ranges and is immutable."""

    def test_stores_year_and_month(self) -> None:
        """Year and month are stored as provided."""
        pid = PeriodId(year=2026, month=3)
        assert pid.year == 2026
        assert pid.month == 3

    def test_month_zero_raises(self) -> None:
        """month=0 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PeriodId(year=2026, month=0)

    def test_month_thirteen_raises(self) -> None:
        """month=13 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PeriodId(year=2026, month=13)

    def test_year_zero_raises(self) -> None:
        """year=0 raises ValueError."""
        with pytest.raises(ValueError, match="year"):
            PeriodId(year=0, month=1)


class TestPeriodState:
    """PeriodState stores YTD progressives and provides a zero factory."""

    def test_zero_factory(self) -> None:
        """PeriodState.zero() returns a state with all counters at zero."""
        s = PeriodState.zero()
        assert s.regular_periods_closed == 0
        assert s.tax_withholding_periods_closed == 0
        assert s.closed_run_ids == frozenset()
        assert s.tax.irpef == _ZERO
        assert s.earnings.inps_employee == _ZERO
        assert s.earnings.gross == _ZERO

    def test_stored_values(self) -> None:
        """All fields are stored and retrievable after construction."""
        s = PeriodState(
            regular_periods_closed=3,
            tax_withholding_periods_closed=3,
            tax=TaxYtd(irpef=Decimal("837.06")),
            earnings=EarningsYtd(
                inps_employee=Decimal("614.46"),
                gross=Decimal("6474.78"),
            ),
        )
        assert s.regular_periods_closed == 3
        assert s.tax_withholding_periods_closed == 3
        assert s.tax.irpef == Decimal("837.06")
        assert s.earnings.inps_employee == Decimal("614.46")
        assert s.earnings.gross == Decimal("6474.78")

    def test_frozen(self) -> None:
        """PeriodState is immutable: attribute assignment raises AttributeError."""
        s = PeriodState.zero()
        with pytest.raises(AttributeError):
            s.regular_periods_closed = 1  # type: ignore[misc]

    def test_negative_regular_periods_raises(self) -> None:
        """regular_periods_closed < 0 raises ValueError."""
        with pytest.raises(ValueError, match="regular_periods_closed"):
            PeriodState(regular_periods_closed=-1)

    def test_tax_withholding_less_than_regular_raises(self) -> None:
        """tax_withholding_periods_closed < regular_periods_closed raises ValueError."""
        with pytest.raises(ValueError, match="tax_withholding_periods_closed"):
            PeriodState(regular_periods_closed=5, tax_withholding_periods_closed=3)

    def test_fringe_taxed_above_fringe_raises(self) -> None:
        """FringeYtd.taxed > FringeYtd.value raises ValueError."""
        with pytest.raises(ValueError, match="taxed"):
            FringeYtd(value=Decimal("100.00"), taxed=Decimal("200.00"))

    def test_regular_periods_exceeds_twelve_raises(self) -> None:
        """regular_periods_closed > 12 raises ValueError."""
        with pytest.raises(ValueError, match="regular_periods_closed"):
            PeriodState(regular_periods_closed=13, tax_withholding_periods_closed=13)

    def test_tax_withholding_exceeds_fourteen_raises(self) -> None:
        """tax_withholding_periods_closed > 14 raises ValueError."""
        with pytest.raises(ValueError, match="tax_withholding_periods_closed"):
            PeriodState(regular_periods_closed=12, tax_withholding_periods_closed=15)

    def test_schema_version_is_one(self) -> None:
        """PeriodState.SCHEMA_VERSION is 1."""
        assert PeriodState.SCHEMA_VERSION == 1

    def test_tax_year_defaults_to_none(self) -> None:
        """tax_year defaults to None on manual construction."""
        assert PeriodState.zero().tax_year is None

    def test_tax_year_stored(self) -> None:
        """tax_year is stored when explicitly set."""
        s = PeriodState(tax_year=2026)
        assert s.tax_year == 2026

    def test_tax_year_below_2020_raises(self) -> None:
        """tax_year < 2020 raises ValueError."""
        with pytest.raises(ValueError, match="tax_year"):
            PeriodState(tax_year=2019)


class TestPeriodCalculationRequest:
    """PeriodCalculationRequest stores period, CCNL reference, and YTD state."""

    def test_stored_fields(self) -> None:
        """All explicitly supplied fields are stored and retrievable."""
        state = PeriodState(
            regular_periods_closed=5,
            tax_withholding_periods_closed=5,
            tax=TaxYtd(irpef=Decimal("1000.00")),
        )
        req = PeriodCalculationRequest(
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

    def test_year_guard_raises_when_tax_year_mismatch(self) -> None:
        """opening_state.tax_year != period_id.year raises ValueError."""
        prior_year_state = PeriodState(
            tax_year=2025,
            regular_periods_closed=12,
            tax_withholding_periods_closed=12,
        )
        with pytest.raises(ValueError, match=r"opening_state\.tax_year"):
            PeriodCalculationRequest(
                period_id=PeriodId(year=2026, month=1),
                payment_date=date(2026, 1, 31),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=prior_year_state,
            )

    def test_year_guard_passes_when_tax_year_none(self) -> None:
        """Manually constructed state with tax_year=None bypasses the year guard."""
        req = PeriodCalculationRequest(
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
            tax_year=2026,
            regular_periods_closed=5,
            tax_withholding_periods_closed=5,
        )
        req = PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=6),
            payment_date=date(2026, 6, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=current_state,
        )
        assert req.opening_state.tax_year == 2026


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
        cs = PeriodState(
            regular_periods_closed=1,
            tax_withholding_periods_closed=1,
            earnings=EarningsYtd(gross=Decimal("2158.26")),
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
        """PeriodCalculationResult is immutable: assignment raises AttributeError."""
        result = _make_result()
        with pytest.raises(AttributeError):
            result.period_net = Decimal(0)  # type: ignore[misc]
