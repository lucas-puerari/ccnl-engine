"""Pay items and ledger intents of the days of an insured absence.

A line of an absence is its deduction (a negative amount, treated like the
employer pay), the insurer share or the employer pay; each becomes one pay
item, one posting intent and its deltas on the INPS, TFR and IRPEF bases.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.event.handlers import EventEffect, _treatment_deltas
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import (
    AbsenceDeduction,
    AbsenceIntegrationItem,
    MaternityItem,
    PayItem,
    WorkInjuryItem,
)
from ccnl_engine.pay_item.services import (
    _ZERO,
    _require_resolution,
    _treatment_from_resolution,
)

if TYPE_CHECKING:
    from ccnl_engine.event.handlers import _EventHandlerCtx
    from ccnl_engine.pay_item.policies import PolicyResolution

__all__ = ["post_lines"]


def _item(
    kind: str, item_id: str, amount: Decimal, units: Decimal, ctx: _EventHandlerCtx
) -> tuple[PayItem, AccountKind]:
    cp, day = ctx.cp, ctx.payment_date
    if amount < _ZERO:
        return (
            AbsenceDeduction(
                item_id=item_id,
                competence_period=cp,
                payment_date=day,
                quantity=units,
                amount=-amount,
                absence_days=units,
            ),
            AccountKind.EMPLOYEE_DEDUCTIONS,
        )
    cls = {
        "maternity_item": MaternityItem,
        "work_injury_item": WorkInjuryItem,
    }.get(kind, AbsenceIntegrationItem)
    item = cls(
        item_id=item_id,
        competence_period=cp,
        payment_date=day,
        quantity=Decimal(1),
        amount=amount,
        absence_days=units,
    )
    return item, AccountKind.CASH_EARNINGS


def post_lines(
    lines: tuple[tuple[str, Decimal, str, Decimal], ...], ctx: _EventHandlerCtx
) -> EventEffect:
    """Return the items, intents and base deltas of ``lines``.

    Each line is ``(suffix, amount, kind, units)``; a negative amount is
    the deduction of the days, treated as ``kind`` says: like the employer
    pay (``absence_integration_item``) or like an unpaid absence
    (``absence_deduction``).

    Returns:
        The effect with its items, intents and deltas.
    """
    effect = EventEffect()
    resolutions: dict[str, PolicyResolution] = {}
    deltas = [_ZERO, _ZERO, _ZERO]
    for suffix, amount, kind, units in lines:
        if amount == _ZERO:
            continue
        if kind not in resolutions:
            resolutions[kind] = _require_resolution(ctx.resolver, kind, ctx.context)
        resolution = resolutions[kind]
        item_id = f"{ctx.evt_id}_{suffix}"
        item, account = _item(kind, item_id, amount, units, ctx)
        effect.items.append(item)
        prefix = "deduction" if amount < _ZERO else "cash"
        effect.intents.append(
            PostingIntent(
                entry_id=f"{prefix}_{item_id}",
                source_item_id=item_id,
                pay_item_kind=item.kind,
                account=account,
                amount=abs(amount),
                policy_decision_id=resolution.policy_id,
            )
        )
        treatment = _treatment_from_resolution(resolution)
        for axis, delta in enumerate(_treatment_deltas(treatment, amount)):
            deltas[axis] += delta
    effect.inps_delta, effect.tfr_delta, effect.irpef_delta = deltas
    return effect
