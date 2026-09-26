"""Work-time regime cap account: validation, availability and the plafond invariant."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.invariants._types import RunFacts
from ccnl_engine.payroll.application.invariants.decisions import (
    check_substitute_tax_plafond,
)
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.employer import (
    EmployerActivity,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.payroll.domain.events import NightShiftEvent
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount
from ccnl_engine.tax.domain.preferential_regime import EmploymentSector

_YEAR = 2026
_CAP = Decimal(1_500)


def _night_run(amount: Decimal, opening: PeriodState) -> PeriodResult:
    event = NightShiftEvent(
        event_date=date(_YEAR, 3, 10),
        supplement_amount=amount,
    )
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(50), activity=EmployerActivity.OTHER
            ),
            sector=EmploymentSector.PRIVATE,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(20_000)),
            period_id=PeriodId(year=_YEAR, month=3),
            payment_date=date(_YEAR, 3, 27),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            opening_state=opening,
            events=(event,),
        )
    )


def _with_used(result: PeriodResult, used: Decimal) -> PeriodResult:
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


class TestPlafondInvariant:
    """substitute_tax_plafond: the account advances by the eligible amounts."""

    def test_real_run_passes(self) -> None:
        """An engine run above the cap consumes exactly the cap."""
        opening = PeriodState.zero()
        result = _night_run(Decimal(2_000), opening)

        assert result.closing_state.ytd.work_time_regime.used == _CAP
        assert check_substitute_tax_plafond(result, opening, RunFacts()) == []

    def test_wrong_advance_is_reported(self) -> None:
        """A closing account that ignores the eligible amount is a violation."""
        opening = PeriodState.zero()
        bad = _with_used(_night_run(Decimal(500), opening), Decimal(0))

        (violation,) = check_substitute_tax_plafond(bad, opening, RunFacts())
        assert violation.invariant_id == "substitute_tax_plafond"
        assert violation.expected == Decimal(500)
        assert violation.actual == Decimal(0)
        assert "substitute_tax_plafond" in {
            v.invariant_id for v in reconcile(bad, opening).violations
        }

    def test_used_above_cap_is_reported(self) -> None:
        """An account above the annual cap is a violation even if it adds up."""
        result = _night_run(Decimal(1_500), PeriodState.zero())
        opening = PeriodState(
            ytd=TaxYearState(work_time_regime=RegimeCapAccount(Decimal(100)))
        )
        bad = _with_used(result, Decimal(1_600))

        violations = check_substitute_tax_plafond(bad, opening, RunFacts())
        above = [v for v in violations if "exceeds the annual cap" in v.message]
        assert [(v.expected, v.actual) for v in above] == [(_CAP, Decimal(1_600))]
