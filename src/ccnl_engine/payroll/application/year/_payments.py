"""Payments of a tax year drawn from competence-year plans, and their schedule.

A competence year generates its runs; each run is paid on the date of its
plan, which sets its tax year (TUIR art. 51 c. 1, cassa allargata).  The
payments of one tax year are computed in payment order on one withholding
schedule: the payments already closed in the opening state, then those
still to compute.  Its last slot is the conguaglio.  A payment the opening
state already closed with the same payment id is not computed again, so a
plan resumed on the state of an interrupted run neither duplicates nor
skips a payment.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.year._accrual_rule import month_accrual_rule
from ccnl_engine.payroll.application.year._calendar import effective_calendar
from ccnl_engine.payroll.application.year._coverage import split_covered
from ccnl_engine.payroll.application.year._runs import plan_year
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.withholding_schedule import (
    WithholdingSchedule,
    WithholdingSlot,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.application.year._runs import YearPlan
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
    from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId
    from ccnl_engine.payroll.domain.uncovered_run import UncoveredRun

__all__ = [
    "PlannedPayment",
    "PreparedYear",
    "check_opening",
    "prepare_year",
    "tax_year_payments",
    "tax_year_schedule",
]

_ONE = Decimal(1)
_FEATURE = "tax_year"


@dataclass(frozen=True)
class PlannedPayment:
    """One run of a competence year and the payment that settles it.

    Attributes:
        plan: The competence-year plan of the run.
        year_plan: Runs, ratei and settlements of that competence year.
        run: The run.
        payment: Its payment: the run and its payment date.
        pay_fraction: Share of a monthly pay the run carries at full
            accrual, from the calendar of its competence year.
        uncovered: Runs of its competence year left out of the year because
            the bundle holds no pay rules on their date.
    """

    plan: CompetenceYearPlan
    year_plan: YearPlan
    run: PayrollRun
    payment: PaymentId
    pay_fraction: Decimal
    uncovered: tuple[PayrollRunId, ...] = ()

    @property
    def slot(self) -> WithholdingSlot:
        """The withholding slot of the payment."""
        return WithholdingSlot(self.payment, self.pay_fraction)


@dataclass(frozen=True)
class PreparedYear:
    """A competence-year plan resolved against its CCNL.

    Attributes:
        plan: The plan.
        ccnl: The contract of its employment.
        calendar: Calendar the year runs on: the CCNL standard one or the
            accepted override.
        payments: One payment per run of the year the bundle can compute,
            in run order.
        uncovered: The runs of the year set aside: the bundle holds no base
            salary of the level on their competence date.
    """

    plan: CompetenceYearPlan
    ccnl: CCNL
    calendar: WorkCalendar
    payments: tuple[PlannedPayment, ...]
    uncovered: tuple[UncoveredRun, ...] = ()


def prepare_year(plan: CompetenceYearPlan, repo: KnowledgeRepository) -> PreparedYear:
    """Resolve the runs of ``plan`` and the payment of each.

    A rejected calendar override, an employment with no day in the year
    or a payment date of a run the year does not compute raises
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.  A run
    whose competence date has no base salary of the level is set aside in
    :attr:`PreparedYear.uncovered`; when every run is,
    :class:`~ccnl_engine.shared.domain.errors.MissingRuleError` of the
    first run is raised.

    Returns:
        The prepared year.
    """
    ccnl = repo.load_ccnl(plan.employment.ccnl_slug)
    calendar = effective_calendar(ccnl, plan.year, plan.calendar_override)
    year_plan = plan_year(plan, calendar, month_accrual_rule(ccnl))
    fractions = {e.kind.value: e.max_fraction for e in calendar.extra_months}
    planned = tuple(
        PlannedPayment(
            plan=plan,
            year_plan=year_plan,
            run=run,
            payment=_payment_of(plan, run, ccnl),
            pay_fraction=fractions.get(run.run_kind, _ONE),
        )
        for run in year_plan.schedule.runs
    )
    payments, uncovered = split_covered(ccnl, plan.employment.level_code, planned)
    left_out = tuple(u.payment.run_id for u in uncovered)
    return PreparedYear(
        plan=plan,
        ccnl=ccnl,
        calendar=calendar,
        payments=tuple(replace(p, uncovered=left_out) for p in payments),
        uncovered=uncovered,
    )


def _payment_of(plan: CompetenceYearPlan, run: PayrollRun, ccnl: CCNL) -> PaymentId:
    """Return the payment of ``run``: the plan's, or the CCNL day of the month.

    An extra month the plan gives no date is paid on the day the CCNL fixes
    (``parameters.thirteenth_payment_day`` or ``fourteenth_payment_day``,
    e.g. Christmas Eve and 1 July for the CCNL Terziario art. 220 and 221),
    unless the plan overrides the calendar.

    Returns:
        The payment of the run.
    """
    days = {
        RunKind.THIRTEENTH: ccnl.parameters.thirteenth_payment_day,
        RunKind.FOURTEENTH: ccnl.parameters.fourteenth_payment_day,
    }
    clause = days.get(run.run_kind)
    if (
        clause is None
        or plan.calendar_override is not None
        or run.run_id in plan.dated_runs
    ):
        return plan.payment_for(run)
    return PaymentId(run.identifier, date(run.year, clause.month, clause.day))


def check_opening(opening: PeriodState | None, tax_year: int, path: str) -> PeriodState:
    """Return the state a sequence of payments of ``tax_year`` opens with.

    Returns:
        ``opening``, or :meth:`PeriodState.zero` when it is ``None``.

    Raises:
        InvalidInputError: When ``opening`` is bound to another tax year, or
            carries YTD amounts without the payments that produced them: the
            payments it closed are needed to tell which runs not to compute
            again.
    """
    if opening is None:
        return PeriodState.zero()
    cash = opening.cash
    bare = replace(cash, obligations=EmploymentObligations())
    if cash.tax_year not in {None, tax_year} or (
        not cash.payments and bare != TaxCashState(tax_year=cash.tax_year)
    ):
        msg = (
            f"the opening state of tax year {tax_year} must be of that tax "
            "year and identify every payment its totals hold: pass "
            "PeriodState.zero(), close_tax_year() of the previous tax year, "
            "or a state of the year computed or imported with its payments"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    return opening


def tax_year_payments(
    years: Iterable[PreparedYear], tax_year: int, opening: PeriodState
) -> tuple[PlannedPayment, ...]:
    """Return the payments of ``tax_year`` still to compute, in payment order.

    A payment of the plans already closed in ``opening`` is skipped; ties on
    the payment date keep the run order (year, month, regular first).

    Returns:
        The payments of the plans attributed to ``tax_year`` and not closed.

    Raises:
        InvalidInputError: When a planned run is closed in ``opening`` with
            another payment: paid on another date, or in another tax year.
    """
    closed = {p.run_id: p for p in opening.cash.payments}
    settled = set(opening.accrual.competence_runs)
    pending: list[PlannedPayment] = []
    for planned in (p for y in years for p in y.payments):
        payment = planned.payment
        if payment.tax_year != tax_year:
            continue
        if closed.get(payment.run_id) == payment:
            continue
        if payment.run_id in settled:
            msg = (
                f"run '{payment.run_id}' is already closed with another "
                f"payment than '{payment}': a run is paid once"
            )
            raise InvalidInputError(msg, feature="accrual_state")
        pending.append(planned)
    pending.sort(key=lambda p: (p.payment.payment_date, p.payment.run_id.order_key))
    return tuple(pending)


def tax_year_schedule(
    tax_year: int,
    opening: PeriodState,
    pending: tuple[PlannedPayment, ...],
    projected: tuple[WithholdingSlot, ...] = (),
) -> WithholdingSchedule:
    """Return the withholding schedule of the payments of ``tax_year``.

    Args:
        tax_year: The tax year.
        opening: State the payments open with; its payments come first.
        pending: Payments still to compute, in payment order.
        projected: Payments expected after ``pending`` that no plan states
            (the standard runs of a later competence year), last.

    Returns:
        One slot per payment that takes one.
    """
    slots = (
        *(WithholdingSlot(p) for p in opening.cash.payments if _takes_slot(p)),
        *(p.slot for p in pending if _takes_slot(p.payment)),
        *projected,
    )
    return WithholdingSchedule(year=tax_year, slots=slots)


def _takes_slot(payment: PaymentId) -> bool:
    return payment.run_id.kind.consumes_withholding_slot
