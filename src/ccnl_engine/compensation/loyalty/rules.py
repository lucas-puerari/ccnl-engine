"""Pay annual loyalty premiums or once-only milestones in a regular run.

The fully employed run chain approximates the enumerated contractual pay
components (ANIEM Art. 45 items 1-14; CNA Art. 48 items 1-12). The caller
states the uninterrupted actual service start when it differs from the hire
date. The dismissal pro rata is not implemented.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.loyalty.models import LoyaltyPremium
from ccnl_engine.compensation.sunday_holiday.rules import monthly_pay
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import BonusEarning, LoyaltyPremiumEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.period.context.services import RunContext

_ZERO = Decimal(0)
_KIND = "loyalty_premium_earning"


@dataclass(frozen=True)
class LoyaltySettlement:
    """The anniversary earning and its additions to the event bases."""

    items: tuple[LoyaltyPremiumEarning | BonusEarning, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    amount: Decimal = _ZERO
    taxed: tuple[bool, bool, bool] = (False, False, False)

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return event totals with the policy-selected bases.

        Returns:
            The updated INPS, TFR and IRPEF event totals.
        """
        inps, tfr, irpef = (self.amount if flag else _ZERO for flag in self.taxed)
        return replace(
            totals,
            inps_base=totals.inps_base + inps,
            tfr_base=totals.tfr_base + tfr,
            irpef_base=totals.irpef_base + irpef,
            decisions=totals.decisions + self.decisions,
        )


def _award_amount(
    ctx: RunContext, clause: LoyaltyPremium, anniversary: date
) -> Decimal | None:
    """Value monthly or hourly normal wages, or refuse an unknown hourly rate.

    Returns:
        Rounded award, or ``None`` when the hourly divisor is unavailable.
    """
    monthly = monthly_pay(ctx.regular_chain, frozenset())
    hours = getattr(clause, "manual_hours", None)
    if ctx.worker_category is WorkerCategory.OPERAIO and hours is not None:
        divisor = ctx.contract.ccnl.parameters.hourly_divisor.period_at(anniversary)
        if divisor is None or divisor.value is None:
            return None
        return money(hours * monthly / divisor.value)
    return money(clause.months * monthly)


def _qualified_before(anniversary: date, qualifying_date: date) -> bool:
    """Return whether the anniversary a year earlier had already qualified.

    A once-only award is paid on the first anniversary on or after the
    qualifying date, never again.

    Returns:
        ``True`` when the previous anniversary was on or after it.
    """
    year = anniversary.year - 1
    previous = anniversary.replace(
        year=year,
        day=min(anniversary.day, calendar.monthrange(year, anniversary.month)[1]),
    )
    return previous >= qualifying_date


def _recognised_milestone(
    ctx: RunContext, clause: LoyaltyPremium, period: EmploymentPeriod
) -> bool:
    """Check whether credited service crosses the threshold during employment.

    Returns:
        ``True`` only in the month the milestone is reached.
    """
    seniority = ctx.request.seniority
    if seniority is None or clause.recurrence != "once":
        return False
    month = ctx.request.period_id.month
    year = ctx.request.period_id.year
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    prior_day = date(year, month, 1) - timedelta(days=1)
    if seniority.as_of > prior_day or (
        period.ended_on is not None and period.ended_on <= prior_day
    ):
        return False
    if period.ended_on is not None:
        last_day = min(last_day, period.ended_on)
    threshold = clause.service_years * 12
    return seniority.months_at(prior_day) < threshold <= seniority.months_at(last_day)


def _actual_anniversary(
    clause: LoyaltyPremium, period: EmploymentPeriod, anniversary: date, month: int
) -> bool:
    """Check the qualifying anniversary of uninterrupted actual service.

    Returns:
        ``True`` if the hire anniversary has reached the service threshold.
    """
    service_start = period.uninterrupted_service_started_on or period.started_on
    qualifying_year = service_start.year + clause.service_years
    qualifying_date = service_start.replace(
        year=qualifying_year,
        day=min(
            service_start.day,
            calendar.monthrange(qualifying_year, service_start.month)[1],
        ),
    )
    return (
        month == period.started_on.month
        and anniversary >= qualifying_date
        and (
            clause.recurrence != "once"
            or not _qualified_before(anniversary, qualifying_date)
        )
    )


def _award_anniversary(
    ctx: RunContext, clause: LoyaltyPremium, period: EmploymentPeriod
) -> date | None:
    """Return the qualifying award date, or none outside the milestone month.

    Returns:
        The anniversary used to value the award, or ``None`` when ineligible.
    """
    month = ctx.request.period_id.month
    year = ctx.request.period_id.year
    recognised = clause.service_basis == "recognised"
    anniversary = period.started_on.replace(
        year=year,
        day=min(period.started_on.day, calendar.monthrange(year, month)[1]),
    )
    qualifies = (
        _recognised_milestone(ctx, clause, period)
        if recognised
        else _actual_anniversary(clause, period, anniversary, month)
    )
    end_boundary = date(year, month, 1) if recognised else anniversary
    if not qualifies or (
        period.ended_on is not None and period.ended_on < end_boundary
    ):
        return None
    return anniversary


def loyalty_premium(ctx: RunContext) -> LoyaltySettlement:
    """Pay a full monthly award on each qualifying hire anniversary month.

    A once-only milestone pays solely on its qualifying anniversary; eligible
    manual workers receive normal hourly pay times the configured hours unless
    the clause specifies monthly pay. A historical in-service gate requires
    the current employment period to have begun by that date.
    Recognised-service milestones instead pay in the month the caller's
    credited seniority crosses the threshold, including prior employers.
    Without a known employment period, or on a non-regular run, pay nothing.
    February 29 hires celebrate on February 28 in non-leap years.

    Returns:
        The award and its posting, or an empty settlement.
    """
    clause = ctx.contract.ccnl.parameters.loyalty_premium
    period = ctx.request.employment_period
    if (
        clause is None
        or period is None
        or ctx.run_kind is not RunKind.REGULAR
        or ctx.worker_category not in clause.categories
    ):
        return LoyaltySettlement()
    in_service_on = clause.in_service_on
    if (
        clause.subsectors and ctx.request.employer.subsector not in clause.subsectors
    ) or (in_service_on is not None and period.started_on > in_service_on):
        return LoyaltySettlement()
    if clause.levels and ctx.request.level_code not in clause.levels:
        return LoyaltySettlement()
    anniversary = _award_anniversary(ctx, clause, period)
    if anniversary is None:
        return LoyaltySettlement()
    year = ctx.request.period_id.year
    amount = _award_amount(ctx, clause, anniversary)
    if amount is None:
        return LoyaltySettlement()
    rule, version = _ccnl_rule(ctx.contract.ccnl, year)
    location = clause.provenance.location
    once = getattr(clause, "recurrence", "annual") == "once"
    kind = "bonus_earning" if once else _KIND
    resolution = _require_resolution(ctx.resolver, kind, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"loyalty_premium_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = (BonusEarning if once else LoyaltyPremiumEarning)(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=clause.months,
        amount=amount,
        source=f"Premio di fedeltà: {getattr(location, 'section', '')}",
    )
    entry = _make_entry(
        item_id,
        item_id,
        kind,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    return LoyaltySettlement(
        items=(item,),
        entries=(entry,),
        decisions=(
            CalculationDecision(
                capability="bonus" if once else "base_salary",
                status=CalculationStatus.FINAL,
                reason_code="loyalty_anniversary",
                rule=f"{rule}:parameters.loyalty_premium",
                rule_version=version,
                source=location,
                inputs={"service_years": str(clause.service_years), "monthly": amount},
                amount=amount,
            ),
        ),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
    )
