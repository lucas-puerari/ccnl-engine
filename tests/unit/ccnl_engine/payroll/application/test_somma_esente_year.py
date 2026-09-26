"""Somma esente over a payroll year: conguaglio, recovery and closed runs."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.service.rounding import money
from tests.helpers import year_input

_YEAR = 2026
# Low-income contract: somma esente of about 877 EUR a year.
_CCNL = "autoscuole-unasca.json"
_LEVEL = "3"
_YEAR_RESULT = calculate_year(year_input(_YEAR, _CCNL, _LEVEL))


def _somma(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("somma_esente")),
        Decimal(0),
    )


def _last_run(opening: PeriodState) -> PeriodResult:
    """Compute the tredicesima, the last withholding slot, from ``opening``.

    Returns:
        The result of the run.
    """
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=12),
            payment_date=date(_YEAR, 12, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
            run=PayrollRun.thirteenth(_YEAR, 12),
        )
    )


def _over_paid(extra: Decimal) -> PeriodState:
    """State before the tredicesima with ``extra`` more somma esente paid.

    Returns:
        The closing state of December with the inflated account.
    """
    opening = _YEAR_RESULT.period_results[-2].closing_state
    account = opening.ytd.somma_esente
    inflated = replace(account, recognized=account.recognized + extra)
    return replace(opening, ytd=replace(opening.ytd, somma_esente=inflated))


class TestYear:
    """A full year pays exactly the annual somma esente."""

    def test_credits_sum_to_the_annual_due(self) -> None:
        """The conguaglio settles the rounding and projection drift."""
        last = _YEAR_RESULT.period_results[-1]
        annual = next(
            c.amount
            for c in last.tax_computation.components
            if c.name == "somma_esente"
        )
        total = sum((_somma(r) for r in _YEAR_RESULT.period_results), Decimal(0))

        assert total == money(annual)
        account = last.closing_state.ytd.somma_esente
        assert account.recognized == total
        assert account.due == money(annual)
        assert account.residual == Decimal(0)
        assert account.reason == "settled_at_conguaglio"


class TestOverPaymentAtConguaglio:
    """Somma esente paid above the updated due is recovered at the conguaglio."""

    def test_same_state_reproduces_the_year(self) -> None:
        """Sanity: the standalone tredicesima matches the year calculation."""
        base = _last_run(_YEAR_RESULT.period_results[-2].closing_state)

        assert _somma(base) == _somma(_YEAR_RESULT.period_results[-1])

    def test_excess_up_to_60_eur_is_recovered_in_full(self) -> None:
        """40 EUR over the balance due: the payslip takes back the difference."""
        base = _somma(_YEAR_RESULT.period_results[-1])
        result = _last_run(_over_paid(base + Decimal(40)))

        assert _somma(result) == Decimal(-40)
        account = result.closing_state.ytd.somma_esente
        assert account.recovered == Decimal(40)
        assert account.residual == Decimal(0)
        decision = next(d for d in result.decisions if d.capability == "somma_esente")
        assert decision.reason_code == "overpayment_recovered"
        assert decision.amount == Decimal(-40)
        assert result.closing_state.obligations == EmploymentObligations()

    def test_excess_above_60_eur_opens_ten_installments(self) -> None:
        """150 EUR over: 15 EUR now, nine installments carried to next year."""
        base = _somma(_YEAR_RESULT.period_results[-1])
        result = _last_run(_over_paid(base + Decimal(150)))

        assert _somma(result) == Decimal("-15.00")
        assert result.closing_state.obligations == EmploymentObligations(
            recoveries=(
                RecoveryObligation(
                    tax_year=_YEAR,
                    plan=RecoveryPlan(
                        kind=SOMMA_ESENTE_RECOVERY,
                        original_amount=Decimal("150.00"),
                        installment_amount=Decimal("15.00"),
                        installments_total=10,
                        installments_posted=1,
                    ),
                ),
            )
        )
        account = result.closing_state.ytd.somma_esente
        assert account.recovered == Decimal("15.00")
        assert account.residual == Decimal("135.00")
        assert result.closing_state.ytd.is_complete


class TestCarriedSommaEsenteRecovery:
    """A somma esente recovery opened in 2025 keeps running in 2026."""

    def test_remaining_installments_are_deducted_once(self) -> None:
        """Three installments of 15 EUR left cost exactly 45.00."""
        plan = RecoveryPlan(
            kind=SOMMA_ESENTE_RECOVERY,
            original_amount=Decimal(150),
            installment_amount=Decimal(15),
            installments_total=10,
            installments_posted=7,
        )
        opening = PeriodState(
            obligations=EmploymentObligations(
                recoveries=(RecoveryObligation(tax_year=2025, plan=plan),)
            )
        )

        with_plan = calculate_year(
            year_input(_YEAR, _CCNL, _LEVEL, opening_state=opening)
        )

        assert _YEAR_RESULT.annual_net - with_plan.annual_net == Decimal("45.00")
        decisions = [
            d for d in with_plan.decisions if d.capability == "somma_esente_recovery"
        ]
        assert [d.reason_code for d in decisions] == [
            "installment_posted",
            "installment_posted",
            "last_installment_posted",
        ]
        assert {d.rule for d in decisions} == {"l207-2024-art1-c7"}
        last_with = with_plan.period_results[-1].closing_state.ytd
        assert last_with == _YEAR_RESULT.period_results[-1].closing_state.ytd


class TestClosedRuns:
    """A run is rejected when it cannot close next in the tax year."""

    def _request(self, month: int, opening: PeriodState) -> PeriodCalculationRequest:
        return PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
            run=PayrollRun.regular(_YEAR, month),
        )

    def test_run_out_of_order_is_rejected(self) -> None:
        """February cannot close after March."""
        opening = PeriodState(
            ytd=TaxYearState(
                tax_year=_YEAR,
                regular_periods_closed=1,
                tax_withholding_periods_closed=1,
                closed_run_ids=(PayrollRunId.parse("2026-03-regular"),),
            )
        )

        with pytest.raises(InvalidInputError, match="out of order") as info:
            calculate_period(self._request(2, opening))

        assert info.value.feature == "payroll_run"

    def test_run_already_closed_is_rejected(self) -> None:
        """March cannot close twice."""
        opening = _YEAR_RESULT.period_results[2].closing_state

        with pytest.raises(InvalidInputError, match="already processed"):
            calculate_period(self._request(3, opening))

    def test_closed_runs_are_recorded_in_payment_order(self) -> None:
        """The year closes its runs as typed ids, the tredicesima last."""
        closed = _YEAR_RESULT.period_results[-1].closing_state.ytd.closed_run_ids

        assert closed[0] == PayrollRunId.parse("2026-01-regular")
        assert closed[-1] == PayrollRunId.parse("2026-12-thirteenth")
        assert len(closed) == len(_YEAR_RESULT.period_results)

    def test_state_with_a_run_of_a_later_year_is_rejected(self) -> None:
        """A 2027 run cannot be closed in tax year 2026."""
        with pytest.raises(ValueError, match="after the tax year 2026"):
            TaxYearState(
                tax_year=_YEAR,
                regular_periods_closed=1,
                tax_withholding_periods_closed=1,
                closed_run_ids=(PayrollRunId.parse("2027-01-regular"),),
            )
