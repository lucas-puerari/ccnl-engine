"""Lifecycle, contribution ceiling, YTD and net pay invariants of a period run."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.errors import (
    DataIntegrityError,
    InvalidInputError,
    OutOfScopeError,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.invariants._types import RunFacts
from ccnl_engine.payroll.application.invariants.lifecycle import (
    check_extra_month_accrual_limit,
    check_run_within_employment,
)
from ccnl_engine.payroll.application.invariants.signs import check_signs
from ccnl_engine.payroll.application.invariants.state import check_ytd_continuity
from ccnl_engine.payroll.application.invariants.withholding import (
    check_contribution_ceiling,
)
from ccnl_engine.payroll.application.period import _closing_state
from ccnl_engine.payroll.application.period._checks import check_net_covered
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.credit_accounts import TrattamentoAccount
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.extra_month_schedule import (
    AccrualWindow,
    ExtraMonthKind,
)
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun
from tests.fixtures.imported_surtax import opening_with_2025_surtax

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_OPENING = PeriodState.zero()
_CEILING = Decimal(122_295)


def _run(
    month: int = 1,
    opening: PeriodState = _OPENING,
    **kwargs: object,
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=opening,
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _with_ytd(result: PeriodResult, **ytd: object) -> PeriodResult:
    state = result.closing_state
    closing = replace(state, cash=replace(state.cash, **ytd))  # type: ignore[arg-type]
    return replace(result, closing_state=closing)


def _accrual(months: int) -> ExtraMonthAccrual:
    start = date(_YEAR, 1, 1)
    return ExtraMonthAccrual(
        kind=ExtraMonthKind.THIRTEENTH,
        window=AccrualWindow(start, start, date(_YEAR, 12, 31)),
        months=months,
    )


class TestRunWithinEmployment:
    """A regular run falls in a month with a day of employment."""

    def test_run_in_employment_passes(self) -> None:
        """A run of a hire month passes."""
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 1, 20)))
        assert check_run_within_employment(_run(), facts) == []

    def test_regular_run_before_hire_is_reported(self) -> None:
        """A regular run before the hire month is a violation."""
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 3, 1)))
        (violation,) = check_run_within_employment(_run(), facts)
        assert violation.invariant_id == "run_within_employment"
        assert "2026-01-regular" in violation.message

    def test_extra_month_run_is_not_checked(self) -> None:
        """Only regular runs are bound to the employment months."""
        result = replace(_run(), run=PayrollRun.thirteenth(_YEAR, 1))
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 3, 1)))
        assert check_run_within_employment(result, facts) == []

    def test_untracked_employment_is_not_checked(self) -> None:
        """Without an employment period nothing is checked."""
        assert check_run_within_employment(_run(), RunFacts()) == []


class TestExtraMonthAccrualLimit:
    """The ratei of one extra month and window reach at most 12 months."""

    def test_full_rateo_passes(self) -> None:
        """Twelve months of one window are within the limit."""
        facts = RunFacts(accruals=(_accrual(8), _accrual(4)))
        assert check_extra_month_accrual_limit(facts) == []

    def test_ratei_above_twelve_months_are_reported(self) -> None:
        """A run paying 13 months of one window is a violation."""
        facts = RunFacts(accruals=(_accrual(12), _accrual(1)))
        (violation,) = check_extra_month_accrual_limit(facts)
        assert violation.invariant_id == "extra_month_accrual_limit"
        assert violation.actual == Decimal(13)


class TestContributionCeiling:
    """The IVS base of a run fits in the massimale headroom."""

    _NEAR_CEILING = PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, _CEILING - 1_000),)
        )
    )

    def _capped_run(self) -> PeriodResult:
        return _run(
            12,
            self._NEAR_CEILING,
            contribution_history=ContributionHistory(date(2001, 9, 1)),
        )

    def test_capped_run_passes(self) -> None:
        """A real run near the massimale takes only the headroom."""
        result = self._capped_run()
        facts = RunFacts(ivs_ceiling=_CEILING)
        assert check_contribution_ceiling(result, self._NEAR_CEILING, facts) == []
        assert reconcile(result, self._NEAR_CEILING, facts).ok

    def test_base_above_headroom_is_reported(self) -> None:
        """An IVS base above the headroom is a violation per IVS component."""
        result = self._capped_run()
        facts = RunFacts(ivs_ceiling=_CEILING - 900)
        violations = check_contribution_ceiling(result, self._NEAR_CEILING, facts)
        assert {v.invariant_id for v in violations} == {"contribution_ceiling"}
        assert [v.expected for v in violations] == [Decimal(100)] * 2

    def test_ceiling_not_applied_is_not_checked(self) -> None:
        """Without a massimale nothing is checked."""
        assert check_contribution_ceiling(_run(), _OPENING, RunFacts()) == []


class TestYtdContinuity:
    """Each YTD accumulator closes at its opening plus the run amount."""

    def test_real_run_passes(self) -> None:
        """A real run with surtax advances every accumulator."""
        opening = opening_with_2025_surtax()
        result = _run(opening=opening, regione="IT-25", comune_belfiore="F205")
        assert result.closing_state.cash.tax.surtax > 0
        assert check_ytd_continuity(result, opening) == []

    def test_wrong_surtax_is_reported(self) -> None:
        """A surtax YTD that ignores the SURTAX posting is a violation."""
        opening = opening_with_2025_surtax()
        result = _run(opening=opening, regione="IT-25", comune_belfiore="F205")
        tax = result.closing_state.cash.tax
        bad = _with_ytd(result, tax=replace(tax, surtax=Decimal(0)))

        (violation,) = check_ytd_continuity(bad, opening)
        assert violation.invariant_id == "ytd_continuity"
        assert "surtax_ytd" in violation.message

    def test_wrong_credit_account_is_reported(self) -> None:
        """A trattamento account that the ledger does not explain is caught."""
        bad = _with_ytd(_run(), trattamento=TrattamentoAccount(Decimal(50)))

        (violation,) = check_ytd_continuity(bad, _OPENING)
        assert "trattamento net credit" in violation.message
        assert violation.actual == Decimal(50)


class TestNetPayNonNegative:
    """A negative net is refused before the invariant, which stays as a guard."""

    def test_real_run_passes(self) -> None:
        """A real run has a non-negative net."""
        assert check_signs(_run()) == []
        check_net_covered(_run())

    def test_negative_net_is_reported(self) -> None:
        """A negative period_net is a violation."""
        bad = replace(_run(), period_net=Decimal("-19.08"))
        (violation,) = check_signs(bad)
        assert violation.invariant_id == "net_pay_non_negative"
        assert violation.actual == Decimal("-19.08")

    def test_negative_net_with_absences_is_out_of_scope(self) -> None:
        """Deductions other than the capped taxes above the pay left raise."""
        bad = replace(
            _run(),
            period_net=Decimal("-5.00"),
            unpaid_absence_deduction=Decimal(2000),
        )
        with pytest.raises(OutOfScopeError, match=r"absences of 2000") as exc:
            check_net_covered(bad)
        assert exc.value.reason == "negative_net"

    def test_negative_net_without_absences_is_out_of_scope(self) -> None:
        """Without absences a negative net is out of scope too, not an invariant."""
        bad = replace(_run(), period_net=Decimal("-1.00"))
        with pytest.raises(OutOfScopeError, match=r"is -1\.00: the") as exc:
            check_net_covered(bad)
        assert (exc.value.reason, exc.value.feature) == ("negative_net", "net_pay")


class TestClosingStateRejected:
    """A closing state that breaks the state invariants is an engine error."""

    @pytest.mark.parametrize(
        "error",
        [
            ValueError("negative YTD"),
            InvalidInputError("payment of another tax year", field="x"),
        ],
    )
    def test_invalid_closing_state_is_a_data_integrity_error(
        self, monkeypatch: pytest.MonkeyPatch, error: Exception
    ) -> None:
        """The opening state was validated, so a broken closing is not input."""

        def broken(*_: object) -> TaxCashState:
            raise error

        monkeypatch.setattr(_closing_state, "_closing_cash", broken)
        with pytest.raises(DataIntegrityError, match="Closing state rejected"):
            _run(1, _OPENING)
