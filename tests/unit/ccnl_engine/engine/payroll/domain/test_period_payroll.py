"""Unit tests for PeriodPayrollRequest and PeriodPayrollResult."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    PeriodPayrollInput,
)

_ZERO = Decimal(0)
_V = Decimal("100.00")


def _minimal_structural() -> AnnualEstimateInput:
    """Return a minimal AnnualEstimateInput for testing.

    Returns:
        A minimal :class:`AnnualEstimateInput` with only required fields set.
    """
    from datetime import date  # noqa: PLC0415

    from ccnl_engine.engine.payroll.domain.employment import (  # noqa: PLC0415
        Permanent,
    )
    from ccnl_engine.engine.payroll.domain.scenario import (  # noqa: PLC0415
        Employee,
        Employer,
        Employment,
    )

    return AnnualEstimateInput(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="metalmeccanico-federmeccanica.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )


def _zero_state() -> PayrollState:
    return PayrollState.zero()


def _nonzero_state() -> PayrollState:
    return PayrollState(
        gross_annual_ytd=Decimal("12000.00"),
        inps_employee_annual_ytd=Decimal("1100.00"),
        inps_employer_annual_ytd=Decimal("3200.00"),
        inail_employer_annual_ytd=Decimal("60.00"),
        taxable_income_ytd=Decimal("10900.00"),
        irpef_gross_ytd=Decimal("2400.00"),
        irpef_withheld_ytd=Decimal("2000.00"),
        work_income_deduction_ytd=Decimal("950.00"),
        fam_deductions_ytd=Decimal("400.00"),
        art15_deductions_ytd=_ZERO,
        trattamento_integrativo_ytd=Decimal("100.00"),
        addizionale_regionale_ytd=Decimal("180.00"),
        addizionale_comunale_ytd=Decimal("90.00"),
        tfr_annual_ytd=Decimal("700.00"),
        leave_accrued_days_ytd=Decimal("16.00"),
        leave_taken_days_ytd=Decimal("5.00"),
        leave_balance_days=Decimal("11.00"),
        sick_days_ytd=Decimal("3.00"),
    )


def _ledger_entry() -> LedgerEntry:
    return LedgerEntry(
        entry_id="base_salary_2026_01",
        competence_period=CompetencePeriod(year=2026, month=1),
        pay_item_id="base_salary_2026_01",
        pay_item_kind="base_salary_earning",
        account=__import__(
            "ccnl_engine.engine.payroll.domain.ledger",
            fromlist=["AccountKind"],
        ).AccountKind.GROSS_EARNINGS,
        amount=Decimal("1000.00"),
    )


class TestPeriodPayrollRequestConstruction:
    """PeriodPayrollRequest stores structural, period, and opening_state."""

    def test_stores_structural(self) -> None:
        """Structural field holds the AnnualEstimateInput."""
        structural = _minimal_structural()
        req = PeriodPayrollRequest(
            structural=structural,
            period=PeriodPayrollInput(),
            opening_state=_zero_state(),
        )
        assert req.structural is structural

    def test_stores_period(self) -> None:
        """Period field holds the PeriodPayrollInput."""
        period = PeriodPayrollInput()
        req = PeriodPayrollRequest(
            structural=_minimal_structural(),
            period=period,
            opening_state=_zero_state(),
        )
        assert req.period is period

    def test_stores_opening_state(self) -> None:
        """opening_state field holds the PayrollState."""
        state = _zero_state()
        req = PeriodPayrollRequest(
            structural=_minimal_structural(),
            period=PeriodPayrollInput(),
            opening_state=state,
        )
        assert req.opening_state is state

    def test_frozen_raises_on_set(self) -> None:
        """PeriodPayrollRequest is immutable."""
        req = PeriodPayrollRequest(
            structural=_minimal_structural(),
            period=PeriodPayrollInput(),
            opening_state=_zero_state(),
        )
        with pytest.raises(AttributeError):
            req.opening_state = _nonzero_state()  # type: ignore[misc]

    def test_opening_state_zero_for_january(self) -> None:
        """Opening state may be PayrollState.zero() for the first period."""
        req = PeriodPayrollRequest(
            structural=_minimal_structural(),
            period=PeriodPayrollInput(),
            opening_state=PayrollState.zero(),
        )
        assert req.opening_state.gross_annual_ytd == _ZERO

    def test_nonzero_opening_state(self) -> None:
        """Opening state may carry prior-period progressives."""
        state = _nonzero_state()
        req = PeriodPayrollRequest(
            structural=_minimal_structural(),
            period=PeriodPayrollInput(),
            opening_state=state,
        )
        assert req.opening_state.gross_annual_ytd == Decimal("12000.00")


class TestPeriodPayrollResultConstruction:
    """PeriodPayrollResult stores opening/closing state and period figures."""

    def _make_result(self, **kwargs: object) -> PeriodPayrollResult:
        defaults: dict[str, object] = {
            "opening_state": _zero_state(),
            "closing_state": _nonzero_state(),
            "period_gross": Decimal("1000.00"),
            "period_net": Decimal("750.00"),
            "period_employer_cost": Decimal("1280.00"),
        }
        defaults.update(kwargs)
        return PeriodPayrollResult(**defaults)  # type: ignore[arg-type]

    def test_stores_opening_state(self) -> None:
        """opening_state is the YTD state passed in."""
        state = _zero_state()
        result = self._make_result(opening_state=state)
        assert result.opening_state is state

    def test_stores_closing_state(self) -> None:
        """closing_state is the updated YTD state after the period."""
        state = _nonzero_state()
        result = self._make_result(closing_state=state)
        assert result.closing_state is state

    def test_stores_period_gross(self) -> None:
        """period_gross is stored."""
        result = self._make_result(period_gross=Decimal("1500.00"))
        assert result.period_gross == Decimal("1500.00")

    def test_stores_period_net(self) -> None:
        """period_net is stored."""
        result = self._make_result(period_net=Decimal("900.00"))
        assert result.period_net == Decimal("900.00")

    def test_stores_period_employer_cost(self) -> None:
        """period_employer_cost is stored."""
        result = self._make_result(period_employer_cost=Decimal("1800.00"))
        assert result.period_employer_cost == Decimal("1800.00")

    def test_ledger_entries_defaults_empty(self) -> None:
        """ledger_entries defaults to an empty tuple."""
        result = self._make_result()
        assert result.ledger_entries == ()

    def test_ledger_entries_stored(self) -> None:
        """ledger_entries is stored when provided."""
        entry = _ledger_entry()
        result = self._make_result(ledger_entries=(entry,))
        assert len(result.ledger_entries) == 1
        assert result.ledger_entries[0] is entry

    def test_frozen_raises_on_set(self) -> None:
        """PeriodPayrollResult is immutable."""
        result = self._make_result()
        with pytest.raises(AttributeError):
            result.period_net = _V  # type: ignore[misc]

    def test_closing_state_reflects_period(self) -> None:
        """closing_state has higher YTD gross than opening_state."""
        result = self._make_result(
            opening_state=_zero_state(),
            closing_state=_nonzero_state(),
        )
        closing = result.closing_state.gross_annual_ytd
        opening = result.opening_state.gross_annual_ytd
        assert closing > opening


class TestPeriodPayrollPublicApi:
    """Both types are accessible from the top-level ccnl_engine package."""

    def test_request_importable_from_package(self) -> None:
        """PeriodPayrollRequest can be imported from ccnl_engine directly."""
        from ccnl_engine import PeriodPayrollRequest as Req  # noqa: PLC0415

        assert Req is PeriodPayrollRequest

    def test_result_importable_from_package(self) -> None:
        """PeriodPayrollResult can be imported from ccnl_engine directly."""
        from ccnl_engine import PeriodPayrollResult as Res  # noqa: PLC0415

        assert Res is PeriodPayrollResult
