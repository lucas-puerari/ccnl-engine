"""Unit tests for the withholding plan used by a period calculation."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.withholding._plan import (
    resolve_withholding_schedule,
    slot_share,
    upcoming_recurring_gross,
)
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import PayrollRunCount
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.types import MonthlyPayChain
from tests.fixtures.withholding import calendar_schedule, paid_before, paid_on_day

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.withholding_schedule import (
        WithholdingSchedule,
    )

_YEAR = 2026
_COOP_SOCIALI = "cooperative-sociali.json"
_HALF_FOURTEENTH = calendar_schedule(
    WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
)


def _chain() -> MonthlyPayChain:
    return MonthlyPayChain(base=Decimal(1000), seniority=Decimal(0), allowances=())


def _request(
    run: PayrollRun,
    paid_on: date,
    opening: PeriodState | None = None,
    schedule: WithholdingSchedule | None = None,
    planned: tuple[PaymentId, ...] | None = None,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=run.year, month=run.month),
        payment_date=paid_on,
        ccnl_slug=_COOP_SOCIALI,
        level_code="D2",
        opening_state=opening or PeriodState.zero(),
        run=run,
        withholding_schedule=schedule,
        planned_payments=planned,
    )


def _resolve(request: PeriodCalculationRequest) -> WithholdingSchedule:
    ccnl = BundledKnowledgeRepository().load_ccnl(_COOP_SOCIALI)
    payment = PaymentId(request.run.identifier, request.payment_date)  # type: ignore[union-attr]
    competence = date(request.period_id.year, request.period_id.month, 1)
    return resolve_withholding_schedule(request, payment, ccnl, competence)


_LATE_DECEMBER = PayrollRun.regular(_YEAR, 12)


def _paid(payments: tuple[PaymentId, ...]) -> PeriodState:
    """Return the state after ``payments`` of 2026, with no amount.

    Returns:
        A state whose accrual and cash parts close ``payments``.
    """
    return PeriodState(
        accrual=EmploymentAccrualState(
            competence_runs=tuple(p.run_id for p in payments)
        ),
        cash=TaxCashState(tax_year=_YEAR, payments=payments),
    )


_PAID_LATE = date(_YEAR + 1, 1, 13)


class TestResolveWithholdingSchedule:
    """The period uses the requested schedule, else the payments of its year."""

    def test_requested_schedule_wins(self) -> None:
        """A schedule passed with the request is used unchanged."""
        requested = calendar_schedule(WorkCalendar(year=_YEAR))
        request = _request(PayrollRun.regular(_YEAR, 1), date(_YEAR, 1, 28))
        resolved = _resolve(replace(request, withholding_schedule=requested))
        assert resolved is requested

    def test_fractional_ccnl_default_has_one_slot_per_payslip(self) -> None:
        """Cooperative Sociali (13.5 months) defaults to 14 slots, not 13."""
        resolved = _resolve(_request(PayrollRun.regular(_YEAR, 1), date(_YEAR, 1, 28)))
        assert resolved == _HALF_FOURTEENTH
        assert resolved.run_count == PayrollRunCount(14)

    def test_late_december_takes_the_first_slot_of_the_next_year(self) -> None:
        """December 2026 paid on 13 January 2027 is the first of 15 payments."""
        resolved = _resolve(_request(_LATE_DECEMBER, _PAID_LATE))

        assert resolved.year == _YEAR + 1
        assert resolved.run_count == PayrollRunCount(15)
        assert resolved.slots[0].run == _LATE_DECEMBER

    def test_late_payment_already_closed_keeps_its_slot(self) -> None:
        """January 2027 sees the late December among the payments of 2027."""
        december = PaymentId(_LATE_DECEMBER.identifier, _PAID_LATE)
        opening = PeriodState(
            accrual=EmploymentAccrualState(competence_runs=(december.run_id,)),
            cash=TaxCashState(tax_year=_YEAR + 1, payments=(december,)),
        )
        january = PayrollRun.regular(_YEAR + 1, 1)

        resolved = _resolve(_request(january, date(_YEAR + 1, 1, 27), opening))

        assert [s.run for s in resolved.slots[:2]] == [_LATE_DECEMBER, january]
        assert resolved.run_count == PayrollRunCount(15)

    def test_a_tredicesima_before_december_leaves_december_projected(self) -> None:
        """Without a plan, the standard December salary is still to come."""
        thirteenth = PayrollRun.thirteenth(_YEAR, 12)
        opening = _paid(paid_before(_LATE_DECEMBER, Decimal("13.5")))
        payment = paid_on_day(thirteenth, 15)

        resolved = _resolve(_request(thirteenth, payment.payment_date, opening))
        position = resolved.position(payment, opening.cash.paid_runs)

        assert resolved.conguaglio.run_id == _LATE_DECEMBER.identifier
        assert (position.remaining, position.settles) == (2, False)

    def test_no_planned_payment_makes_the_tredicesima_the_conguaglio(self) -> None:
        """December paid on 13 January: the tredicesima is the last of 2026."""
        thirteenth = PayrollRun.thirteenth(_YEAR, 12)
        opening = _paid(paid_before(_LATE_DECEMBER, Decimal("13.5")))
        payment = paid_on_day(thirteenth, 15)
        request = _request(thirteenth, payment.payment_date, opening, planned=())

        resolved = _resolve(request)

        assert resolved.conguaglio == payment
        assert resolved.position(payment, opening.cash.paid_runs).settles

    def test_planned_payments_replace_the_projection(self) -> None:
        """A December paid on 12 January keeps the tredicesima from settling."""
        thirteenth = PayrollRun.thirteenth(_YEAR, 12)
        december = PaymentId(_LATE_DECEMBER.identifier, date(_YEAR + 1, 1, 12))
        request = _request(thirteenth, date(_YEAR, 12, 15), planned=(december,))

        resolved = _resolve(request)

        assert resolved.conguaglio == december
        assert resolved.year == _YEAR

    @pytest.mark.parametrize(
        "planned",
        [
            PaymentId(_LATE_DECEMBER.identifier, _PAID_LATE),
            paid_on_day(PayrollRun.thirteenth(_YEAR, 12), 15),
        ],
        ids=["another tax year", "the run itself"],
    )
    def test_rejects_a_planned_payment_that_cannot_follow(
        self, planned: PaymentId
    ) -> None:
        """A planned payment is of the tax year and of another run."""
        thirteenth = PayrollRun.thirteenth(_YEAR, 12)
        request = _request(thirteenth, date(_YEAR, 12, 15), planned=(planned,))

        with pytest.raises(InvalidInputError, match="cannot follow") as info:
            _resolve(request)

        assert info.value.field == "PeriodInput.planned_payments"

    def test_rejects_a_planned_payment_already_paid(self) -> None:
        """A run already paid is not planned again."""
        november = paid_on_day(PayrollRun.regular(_YEAR, 11))
        opening = PeriodState(
            accrual=EmploymentAccrualState(competence_runs=(november.run_id,)),
            cash=TaxCashState(tax_year=_YEAR, payments=(november,)),
        )
        thirteenth = PayrollRun.thirteenth(_YEAR, 12)
        request = _request(
            thirteenth, date(_YEAR, 12, 15), opening, planned=(november,)
        )

        with pytest.raises(InvalidInputError, match="cannot follow"):
            _resolve(request)


class TestUpcomingRecurringGross:
    """Upcoming slots are valued at the pay their run kind carries."""

    def test_first_slot_projects_the_rest_of_the_year(self) -> None:
        """11 regular months, half a fourteenth and a full thirteenth."""
        gross = upcoming_recurring_gross(_chain(), _HALF_FOURTEENTH.slots[1:])
        assert gross == Decimal(11 * 1000 + 500 + 1000)

    def test_last_slot_has_nothing_upcoming(self) -> None:
        """On the last slot the projection adds nothing."""
        assert upcoming_recurring_gross(_chain(), ()) == 0


def test_slot_share_divides_by_run_count() -> None:
    """An annual amount is split over the 14 payslips, not over 13.5."""
    assert slot_share(Decimal(1400), _HALF_FOURTEENTH.run_count.value) == Decimal(100)


def test_request_schedule_of_other_year_rejected() -> None:
    """A withholding schedule of another tax year is rejected."""
    with pytest.raises(InvalidInputError, match=r"withholding_schedule\.year"):
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=1),
            payment_date=date(_YEAR, 1, 28),
            ccnl_slug=_COOP_SOCIALI,
            level_code="D2",
            withholding_schedule=calendar_schedule(WorkCalendar(year=_YEAR + 1)),
        )


def test_standalone_december_is_not_the_last_slot_with_half_fourteenth() -> None:
    """Without a schedule, December regular still leaves the tredicesima slot.

    With the twelve earlier payments identified, December is not the
    conguaglio: it withholds the tax of its own pay period (art. 23 c. 2
    lett. a) DPR 600/1973), not the balance of the year, which the
    tredicesima settles.
    """
    paid = _paid(paid_before(PayrollRun.regular(_YEAR, 12), Decimal("13.5")))
    opening = replace(
        paid,
        cash=replace(paid.cash, earnings=EarningsYtd(taxable=Decimal("18043.97"))),
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=12),
            payment_date=date(_YEAR, 12, 28),
            ccnl_slug=_COOP_SOCIALI,
            level_code="D2",
            opening_state=opening,
            run=PayrollRun.regular(_YEAR, 12),
        )
    )
    tax = result.tax_computation
    assert tax.withholding_due > 0
    assert 0 < tax.ordinary_tax < tax.withholding_due
