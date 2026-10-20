"""Gross, pay item and posting intent of a standard work or bonus event."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.event.facade import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
)
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import (
    AbsenceDeduction,
    BonusEarning,
    CompetencePeriod,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    SicknessItem,
)
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.pay_item.policies import PolicyResolution

_WorkTimeEvent = (
    OvertimeEvent | NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent | AbsenceEvent
)

_CashEvent = _WorkTimeEvent | SickLeaveEvent | BonusEvent

_BONUS_KINDS: dict[str, str] = {
    "productivity_bonus": "productivity_bonus_earning",
    "contract_renewal": "contract_renewal_earning",
}


def _standard_event_gross(event: _CashEvent) -> Decimal:
    """Compute the gross amount for a standard work event.

    A work-time event must carry the values it is paid with, resolved
    against the CCNL by
    :func:`~ccnl_engine.working_time.services.resolve_work_event`.

    Returns:
        Rounded gross amount in EUR (negative for absence deductions).

    Raises:
        ValueError: When a rate, multiplier or supplement is not resolved.
    """
    if isinstance(event, OvertimeEvent):
        if event.multiplier is None or event.hourly_rate is None:
            msg = "the overtime rate must be resolved before the gross"
            raise ValueError(msg)
        return money(event.hours * event.hourly_rate * event.multiplier)
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent, ShiftWorkEvent)):
        if event.supplement_amount is None:
            msg = "the supplement must be resolved before the gross"
            raise ValueError(msg)
        return event.supplement_amount
    if isinstance(event, AbsenceEvent):
        if event.hourly_rate is None:
            msg = "the absence rate must be resolved before the gross"
            raise ValueError(msg)
        return -money(event.hours * event.hourly_rate)
    if isinstance(event, SickLeaveEvent):
        if event.waiting_period_days > 0:
            daily = money(event.amount / Decimal(event.sick_days))
            return event.amount - money(daily * event.waiting_period_days)
        return event.amount
    return event.amount  # BonusEvent


def _work_time_item(
    event: _WorkTimeEvent,
    gross: Decimal,
    evt_id: str,
    cp: CompetencePeriod,
    payment_date: date,
) -> tuple[PayItem, str]:
    """Create the pay item and kind string of an overtime, supplement or absence.

    Returns:
        ``(item, pay_item_kind)``.
    """
    if isinstance(event, OvertimeEvent):
        overtime = OvertimeEarning(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=event.hours,
            amount=gross,
            hours=event.hours,
        )
        return overtime, "overtime_earning"
    if isinstance(event, AbsenceEvent):
        absence = AbsenceDeduction(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=event.hours,
            amount=-gross,
            absence_days=event.hours / Decimal(8),
        )
        return absence, "absence_deduction"
    supplement = NightHolidayShiftEarning(
        item_id=evt_id,
        competence_period=cp,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return supplement, "night_holiday_shift_earning"


def _standard_event_item(
    event: _CashEvent,
    gross: Decimal,
    evt_id: str,
    cp: CompetencePeriod,
    payment_date: date,
) -> tuple[PayItem, str]:
    """Create the pay item and kind string for a standard work event.

    Returns:
        ``(item, pay_item_kind)`` where *pay_item_kind* is the string used in
        the corresponding ledger entry.
    """
    if isinstance(event, SickLeaveEvent):
        sickness = SicknessItem(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=gross,
            sick_days=Decimal(event.sick_days),
        )
        return sickness, "sickness_item"
    if isinstance(event, BonusEvent):
        bonus = BonusEarning(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=gross,
        )
        return bonus, _BONUS_KINDS.get(event.kind, "bonus_earning")
    return _work_time_item(event, gross, evt_id, cp, payment_date)


def _make_standard_event_intent(
    event: _CashEvent,
    gross: Decimal,
    evt_id: str,
    kind: str,
    resolution: PolicyResolution,
) -> PostingIntent:
    """Build the posting intent for a standard cash or absence event.

    Returns:
        A :class:`~ccnl_engine.ledger.models.PostingIntent` targeting
        ``EMPLOYEE_DEDUCTIONS`` for absences and ``CASH_EARNINGS`` otherwise.
    """
    if isinstance(event, AbsenceEvent):
        return PostingIntent(
            entry_id=f"deduction_{evt_id}",
            source_item_id=evt_id,
            pay_item_kind=kind,
            account=AccountKind.EMPLOYEE_DEDUCTIONS,
            amount=-gross,
            policy_decision_id=resolution.policy_id,
        )
    return PostingIntent(
        entry_id=f"cash_{evt_id}",
        source_item_id=evt_id,
        pay_item_kind=kind,
        account=AccountKind.CASH_EARNINGS,
        amount=gross,
        policy_decision_id=resolution.policy_id,
    )
