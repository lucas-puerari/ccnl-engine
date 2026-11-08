"""Former legal operai's holiday hours and former Part One's annual pay."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.sunday_holiday.rules import monthly_pay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import FixedAllowanceEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.compensation.legacy_holiday.models import LegacyHolidayPayment
    from ccnl_engine.period.context.services import RunContext

_ZERO = Decimal(0)
_HOLIDAY_ROLE = "former_legal_operaio"
_ANNUAL_ROLE = "former_part_one_2008"
_CUTOFF = date(2008, 12, 31)
_KIND = "fixed_allowance_earning"


def _issue(fact: str) -> ExtraMonthSettlement:
    return ExtraMonthSettlement(
        issues=(
            CalculationIssue(
                code=f"legacy_holiday_{fact}_unknown",
                capability="base_salary",
                message=f"Former-worker pay requires {fact}; the amount is left out",
                status=CalculationStatus.INCOMPLETE,
                fact=fact,
            ),
        )
    )


def _pay(
    ctx: RunContext, code: str, quantity: Decimal, amount: Decimal
) -> ExtraMonthSettlement:
    if amount <= _ZERO:
        return ExtraMonthSettlement()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"{code}_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = FixedAllowanceEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=quantity,
        amount=amount,
        source=f"CCNL Art. {'32' if code == 'former_operaio_holidays' else '38'}",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    return ExtraMonthSettlement(
        items=(item,),
        entries=(entry,),
        inps_base=amount if treatment.inps else _ZERO,
        tfr_base=amount if treatment.tfr else _ZERO,
        irpef_base=amount if treatment.irpef else _ZERO,
    )


def _holiday_count(ctx: RunContext) -> int:
    """Count weekday civil holidays, plus Epiphany on a weekend in January.

    Returns:
        The number of eligible holidays within this worker's service.
    """
    year, month = ctx.request.period_id.year, ctx.request.period_id.month
    period = ctx.request.employment_period
    count = 0
    for holiday in ctx.repo.load_national_holidays().holidays:
        if holiday.day == "11-04":
            continue
        day = holiday.on(year)
        if day is None or day.month != month:
            continue
        if period is not None and (
            day < period.started_on
            or (period.ended_on is not None and day > period.ended_on)
        ):
            continue
        if day.weekday() < 5 or (holiday.day == "01-06" and day.weekday() >= 5):
            count += 1
    return count


def _holiday(
    ctx: RunContext, clause: LegacyHolidayPayment, hourly: Decimal
) -> ExtraMonthSettlement:
    """Settle the eligible holiday hours, net of company compensation.

    Returns:
        An earning, an issue for the missing role or offset, or nothing.
    """
    count = _holiday_count(ctx)
    if not count:
        return ExtraMonthSettlement()
    roles = ctx.request.roles
    if roles is None:
        return _issue("roles")
    if _HOLIDAY_ROLE not in roles:
        return ExtraMonthSettlement()
    offset = ctx.request.holiday_company_offset
    if offset is None:
        return _issue("holiday_company_offset")
    amount = max(_ZERO, money(hourly * clause.holiday_hours * count) - offset)
    return _pay(ctx, "former_operaio_holidays", Decimal(count), amount)


def _annual(
    ctx: RunContext, clause: LegacyHolidayPayment, hourly: Decimal
) -> ExtraMonthSettlement:
    """Settle the December annual, non-absorbable payment of the old cohort.

    Returns:
        An earning, an issue for the missing cohort, or nothing.
    """
    period = ctx.request.employment_period
    if (
        ctx.request.period_id.month != 12
        or ctx.request.period_id.year < 2009
        or (period is not None and period.started_on > _CUTOFF)
    ):
        return ExtraMonthSettlement()
    roles = ctx.request.roles
    if roles is None:
        return _issue("roles")
    if _ANNUAL_ROLE not in roles:
        return ExtraMonthSettlement()
    return _pay(
        ctx,
        "former_part_one_annual",
        Decimal(1),
        money(hourly * clause.annual_hours),
    )


def legacy_holiday_payment(ctx: RunContext) -> tuple[ExtraMonthSettlement, ...]:
    """Settle separately each eligible holiday and the December annual amount.

    A missing cohort role or company offset blocks only a month in which
    the relevant clause could pay. The offset absorbs the holiday amount,
    never the non-absorbable annual payment.

    Returns:
        The payable settlements and issues for the month.
    """
    rules = ctx.contract.ccnl.work_rules
    clause = None if rules is None else rules.legacy_holiday_payment
    if clause is None or ctx.run_kind is not RunKind.REGULAR:
        return ()
    divisor = ctx.contract.ccnl.parameters.hourly_divisor.value_at(
        ctx.contract.tctx.competence
    )
    hourly = monthly_pay(ctx.regular_chain, frozenset()) / divisor
    return (_holiday(ctx, clause, hourly), _annual(ctx, clause, hourly))
