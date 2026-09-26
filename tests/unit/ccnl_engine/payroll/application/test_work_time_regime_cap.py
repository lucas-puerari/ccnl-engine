"""Work-time regime cap account: validation, availability and invariant I18."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.application.state_invariants import check_i18
from ccnl_engine.payroll.domain.events import NightShiftEvent
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount

_YEAR = 2026
_CAP = Decimal(1_500)


def _night_run(amount: Decimal, opening: PeriodState) -> PeriodCalculationResult:
    event = NightShiftEvent(
        event_date=date(_YEAR, 3, 10),
        supplement_amount=amount,
        prior_income=Decimal(20_000),
    )
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=3),
            payment_date=date(_YEAR, 3, 27),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            opening_state=opening,
            events=(event,),
        )
    )


def _with_used(
    result: PeriodCalculationResult, used: Decimal
) -> PeriodCalculationResult:
    state = result.closing_state
    closing = replace(
        state, ytd=replace(state.ytd, work_time_regime=RegimeCapAccount(used))
    )
    return replace(result, closing_state=closing)


class TestRegimeCapAccount:
    """The account holds a non-negative used amount."""

    def test_zero_by_default(self) -> None:
        """A new tax year starts with nothing used."""
        assert PeriodState.zero().ytd.work_time_regime.used == Decimal(0)

    def test_negative_used_is_rejected(self) -> None:
        """A negative used amount cannot be represented."""
        with pytest.raises(ValueError, match="must be >= 0"):
            RegimeCapAccount(used=Decimal("-0.01"))

    @pytest.mark.parametrize(
        ("used", "available"),
        [
            (Decimal(0), _CAP),
            (Decimal(1_000), Decimal(500)),
            (_CAP, Decimal(0)),
            (Decimal(2_000), Decimal(0)),
        ],
    )
    def test_available_is_never_negative(
        self, used: Decimal, available: Decimal
    ) -> None:
        """What is left of the cap is ``cap - used``, floored at zero."""
        assert RegimeCapAccount(used).available(_CAP) == available


class TestInvariantI18:
    """I18: the account advances by the eligible amounts, within the cap."""

    def test_real_run_passes(self) -> None:
        """An engine run above the cap consumes exactly the cap."""
        opening = PeriodState.zero()
        result = _night_run(Decimal(2_000), opening)

        assert result.closing_state.ytd.work_time_regime.used == _CAP
        assert check_i18(result, opening) == []

    def test_wrong_advance_is_reported(self) -> None:
        """A closing account that ignores the eligible amount is a violation."""
        opening = PeriodState.zero()
        bad = _with_used(_night_run(Decimal(500), opening), Decimal(0))

        (violation,) = check_i18(bad, opening)
        assert violation.invariant_id == "I18"
        assert violation.expected == Decimal(500)
        assert violation.actual == Decimal(0)
        assert "I18" in {v.invariant_id for v in reconcile(bad, opening).violations}

    def test_used_above_cap_is_reported(self) -> None:
        """An account above the annual cap is a violation even if it adds up."""
        result = _night_run(Decimal(1_500), PeriodState.zero())
        opening = PeriodState(
            ytd=TaxYearState(work_time_regime=RegimeCapAccount(Decimal(100)))
        )
        bad = _with_used(result, Decimal(1_600))

        (violation,) = check_i18(bad, opening)
        assert violation.expected == _CAP
        assert violation.actual == Decimal(1_600)
