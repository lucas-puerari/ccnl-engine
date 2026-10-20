"""Leave of one run: accrual of its month, leave taken, residual paid.

The stage reads the leave account of the opening state and returns the
account the closing state carries, in one fixed order:

1. a regular run credits its competence month
   (:func:`~ccnl_engine.leave.accrual.rules.accrue_month`), when the CCNL
   states an accrual;
2. each :class:`~ccnl_engine.leave.inputs.LeaveTakenEvent` of the run
   consumes its bucket;
3. the run that closes the employment pays the residual
   (:func:`~ccnl_engine.leave.settlement.services.settle_leave`).

A run closes once, so its month is credited once over the employment; the
residual is paid once, since the settlement settles the balances.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.inputs import AbsenceEvent
from ccnl_engine.leave.accrual.rules import AccrualFacts, accrue_month, month_service
from ccnl_engine.leave.handlers import LeaveTerms
from ccnl_engine.leave.inputs import LeaveTakenEvent
from ccnl_engine.leave.settlement.services import SettlementTerms, settle_leave
from ccnl_engine.run.models import RunKind
from ccnl_engine.seniority.services import seniority_months_at
from ccnl_engine.working_time.overtime.policies import CCNLOvertimeBands

if TYPE_CHECKING:
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.models import LeaveRules
    from ccnl_engine.leave.settlement.services import LeaveSettlement
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["RunLeave", "leave_terms", "part_time_ratio", "run_leave"]


@dataclass(frozen=True)
class RunLeave:
    """Leave account after the run, with the indemnity it paid, if any.

    Attributes:
        account: The leave account the closing state carries.
        settlement: Indemnity of the residual leave, on a run that closes
            the employment; ``None`` on any other run.
    """

    account: LeaveAccount
    settlement: LeaveSettlement | None = None

    @property
    def items(self) -> tuple[PayItem, ...]:
        """Pay items of the indemnity."""
        return () if self.settlement is None else self.settlement.items

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        """Ledger entries of the indemnity."""
        return () if self.settlement is None else self.settlement.entries

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return ``totals`` with the account and the indemnity added.

        Returns:
            A copy of ``totals`` carrying the leave account, with the bases
            of the indemnity, its decision and its issues added.
        """
        settlement = self.settlement
        if settlement is None:
            return replace(totals, leave=self.account)
        return replace(
            totals,
            inps_base=totals.inps_base + settlement.inps_base,
            tfr_base=totals.tfr_base + settlement.tfr_base,
            irpef_base=totals.irpef_base + settlement.irpef_base,
            decisions=(*totals.decisions, settlement.decision),
            issues=totals.issues + settlement.issues,
            leave=self.account,
        )


def leave_rules(ctx: RunContext) -> LeaveRules | None:
    """Return the leave rules of the CCNL of the run.

    Returns:
        The rules, ``None`` when the CCNL file has none.
    """
    work = ctx.contract.ccnl.work_rules
    return None if work is None else work.leave_rules


def leave_terms(ctx: RunContext) -> LeaveTerms:
    """Return the leave rules of the run with the ruleset they come from.

    Returns:
        The terms the leave handler and the settlement read.
    """
    bands = CCNLOvertimeBands.of(ctx.contract.ccnl, ctx.contract.tctx.competence.year)
    return LeaveTerms(leave_rules(ctx), bands.ruleset, bands.version)


def part_time_ratio(ctx: RunContext) -> Decimal | None:
    """Return the weekly over the full-time hours of a part-time worker.

    Returns:
        The ratio below one, ``None`` for a full-time worker or when either
        hours are not stated.
    """
    request = ctx.request
    weekly, full = request.weekly_hours, request.full_time_weekly_hours
    if weekly is None or full is None or weekly.value >= full.value:
        return None
    return Decimal(weekly.value) / Decimal(full.value)


def _accrual_facts(ctx: RunContext) -> AccrualFacts:
    """Return the facts the accrual of the run's month reads.

    Returns:
        The days served, the employer size, the hire date, the seniority
        and the part-time ratio of the run.
    """
    request = ctx.request
    absences = [e for e in request.events if isinstance(e, AbsenceEvent)]
    suspended = frozenset(
        day for event in absences if event.suspends_accrual for day in event.days
    )
    month = request.period_id
    period = request.employment_period
    return AccrualFacts(
        year=month.year,
        month=month.month,
        service=month_service(
            month.year,
            month.month,
            period,
            suspended,
            known=all(e.suspends_accrual is not None for e in absences),
        ),
        headcount=request.employer.headcount.value,
        hired_on=None if period is None else period.started_on,
        seniority_months=seniority_months_at(
            request.seniority, ctx.contract.tctx.competence
        ),
        part_time_ratio=part_time_ratio(ctx),
    )


def _settlement_terms(ctx: RunContext, terms: LeaveTerms) -> SettlementTerms:
    divisor = ctx.contract.ccnl.parameters.hourly_divisor.period_at(
        ctx.contract.tctx.competence
    )
    return SettlementTerms(
        leave=terms,
        monthly_pay=ctx.regular_gross,
        hourly_divisor=None if divisor is None else divisor.value,
        part_time_ratio=part_time_ratio(ctx),
        competence_period=ctx.cp,
        payment_date=ctx.contract.tctx.payment,
        tag=ctx.run_id,
        resolver=ctx.resolver,
        context=ctx.policy_context,
    )


def run_leave(ctx: RunContext) -> RunLeave:
    """Accrue the month, take the leave of the run and pay the residual.

    Returns:
        The leave account after the run, with the indemnity of a run that
        closes the employment.
    """
    account = ctx.opening.accrual.leave
    terms = leave_terms(ctx)
    rules = terms.rules
    if ctx.run_kind is RunKind.REGULAR and rules is not None and rules.buckets:
        account = accrue_month(account, rules, _accrual_facts(ctx))
    for event in ctx.request.events:
        if isinstance(event, LeaveTakenEvent):
            account = account.taken(event.bucket, event.event_date.year, event.quantity)
    if not ctx.closes_employment:
        return RunLeave(account)
    settlement = settle_leave(account, _settlement_terms(ctx, terms))
    return RunLeave(settlement.account, settlement)
