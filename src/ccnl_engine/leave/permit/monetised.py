"""Permit hours a CCNL pays in money with the thirteenth month.

Federmeccanica art. 5 (CCNL 5 February 2021, PDF p. 155): "Per gli stessi
lavoratori turnisti addetti al settore siderurgico, tale permesso di 8 ore è
monetizzato e riconosciuto a decorrere dal 1° gennaio 2000; la
monetizzazione è corrisposta insieme alla tredicesima mensilità al valore
retributivo sul quale la stessa è computata."

The hours are "computato in ragione di anno di servizio o frazione di esso",
as the thirteenth: the run paying the thirteenth pays ``hours`` over the
CCNL hourly divisor of the thirteenth it pays, which carries the same
fraction of the year.  That is the thirteenth run, or the run liquidating
its ratei at the termination.  The facts of the run (sub-sector, shift
status) are read for the whole year of the thirteenth.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.extra_month.schedule.models import ExtraMonthKind
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import FixedAllowanceEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _apply_extra_month_policy,
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.leave.permit.supplements import PermitExtraHours
    from ccnl_engine.period.context.services import RunContext

__all__ = ["monetised_permit_payment"]

_KIND = "fixed_allowance_earning"
_ZERO = Decimal(0)


def _thirteenth_gross(ctx: RunContext) -> Decimal | None:
    """Return the gross of the thirteenth the run pays.

    Returns:
        The pay of a thirteenth run, the ratei of the thirteenth a run
        liquidates at the termination, ``None`` on any other run.
    """
    if ctx.run_kind is RunKind.THIRTEENTH:
        return ctx.monthly_gross
    ratei = [s for s in ctx.settlements if s.kind is ExtraMonthKind.THIRTEENTH]
    if not ratei or ratei[0].accrued <= 0:
        return None
    scaled = _apply_extra_month_policy(
        ctx.regular_chain, ExtraMonthKind.THIRTEENTH.value, ratei[0].fraction
    )
    return money(scaled.base + scaled.seniority + scaled.allowances_total)


def _monetised(ctx: RunContext) -> tuple[PermitExtraHours, ...]:
    """Return the monetised permit hours of the CCNL.

    Returns:
        The extra hours paid with the thirteenth, empty when none.
    """
    rules = ctx.contract.ccnl.work_rules
    leave = None if rules is None else rules.leave_rules
    permits = () if leave is None else leave.permits
    return tuple(e for p in permits for e in p.extra_hours if e.paid_with_thirteenth)


def monetised_permit_payment(ctx: RunContext) -> ExtraMonthSettlement:
    """Pay the permit hours a CCNL monetises with the thirteenth.

    Returns:
        The earning on the run paying the thirteenth, nothing otherwise:
        a run that does not state the sub-sector or the shift status pays
        no hours (``Employment.qualifying_shifts`` is a pending fact).
    """
    items = _monetised(ctx)
    gross = None if not items else _thirteenth_gross(ctx)
    if gross is None or gross <= _ZERO:
        return ExtraMonthSettlement()
    request, day = ctx.request, ctx.contract.tctx.competence
    subsector, shifts = request.employer.subsector, request.qualifying_shifts
    hours = sum((e.hours for e in items if e.applies(day, subsector, shifts)), _ZERO)
    divisor = ctx.contract.ccnl.parameters.hourly_divisor.value_at(day)
    amount = money(hours * gross / divisor)
    if amount <= _ZERO:
        return ExtraMonthSettlement()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"permit_monetised_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    item = FixedAllowanceEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=hours,
        amount=amount,
        source="CCNL permit hours paid with the thirteenth",
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
