"""Builders for individual work-event pay items and ledger entries."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BonusEarning,
    CompetencePeriod,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    SicknessItem,
)
from ccnl_engine.payroll.domain.policy import (
    PolicyContext,
    PolicyResolution,
    PolicyResolver,
)
from ccnl_engine.payroll.domain.treatment import EventTreatment
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

_MAX_MONTHLY_HOURS = Decimal(240)

_CashEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | BonusEvent
)


def _check_event_date(
    event: WorkEvent, date_ctx: EffectiveDateContext, idx: int
) -> None:
    """Raise InvalidInputError if event is invalid for the competence period.

    Raises:
        InvalidInputError: When any validation fails.
    """
    if isinstance(event, ArrearsEvent):
        return
    if not date_ctx.contains(event.event_date):
        msg = (
            f"event {idx} ({type(event).__name__}) event_date {event.event_date} "
            f"is outside period [{date_ctx.period_start}, {date_ctx.period_end}]"
        )
        raise InvalidInputError(msg)
    if isinstance(event, AbsenceEvent) and (
        event.hours <= _ZERO or event.hours > _MAX_MONTHLY_HOURS
    ):
        msg = (
            f"event {idx} (AbsenceEvent) hours={event.hours} is invalid: "
            f"must be > 0 and <= {_MAX_MONTHLY_HOURS} per period"
        )
        raise InvalidInputError(msg)


def _standard_event_gross(event: _CashEvent) -> Decimal:
    """Compute the gross amount for a standard work event.

    Returns:
        Rounded gross amount in EUR (negative for absence deductions).
    """
    if isinstance(event, OvertimeEvent):
        return money(event.hours * event.hourly_rate * event.multiplier)
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent)):
        return event.supplement_amount
    if isinstance(event, AbsenceEvent):
        return -money(event.hours * event.hourly_rate)
    if isinstance(event, SickLeaveEvent):
        if event.waiting_period_days > 0:
            daily = money(event.amount / Decimal(event.sick_days))
            return event.amount - money(daily * event.waiting_period_days)
        return event.amount
    return event.amount  # BonusEvent


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
    if isinstance(event, OvertimeEvent):
        return (
            OvertimeEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
            ),
            "overtime_earning",
        )
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent)):
        return (
            NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            ),
            "night_holiday_shift_earning",
        )
    if isinstance(event, AbsenceEvent):
        return (
            AbsenceDeduction(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=-gross,
                absence_days=event.hours / Decimal(8),
            ),
            "absence_deduction",
        )
    if isinstance(event, SickLeaveEvent):
        return (
            SicknessItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
                sick_days=Decimal(event.sick_days),
            ),
            "sickness_item",
        )
    is_pdr_kind = event.kind == "productivity_bonus"
    kind = "productivity_bonus_earning" if is_pdr_kind else "bonus_earning"
    return (
        BonusEarning(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=gross,
        ),
        kind,
    )


def _treatment_deltas(
    treatment: EventTreatment, gross: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_delta, tfr_delta, irpef_delta) for a standard event.

    Returns:
        A triple of gross or zero for each axis per the treatment policy.
    """
    return (
        gross if treatment.inps else _ZERO,
        gross if treatment.tfr else _ZERO,
        gross if treatment.irpef else _ZERO,
    )


def _fringe_bases(
    amount: Decimal,
    cumulative_fringe: Decimal,
    threshold: Decimal,
    cumulative_taxed: Decimal = _ZERO,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_base, irpef_base, new_cumulative) for a fringe event.

    Returns:
        ``(inps_base, irpef_base, new_cumulative)`` where the first two
        are the retroactive taxable base or zero depending on cumulative taxability.
    """
    new_cumulative = cumulative_fringe + amount
    if new_cumulative > threshold:
        retroactive = new_cumulative - cumulative_taxed
        return retroactive, retroactive, new_cumulative
    return _ZERO, _ZERO, new_cumulative


def _make_standard_event_entry(
    event: _CashEvent,
    gross: Decimal,
    evt_id: str,
    kind: str,
    cp: CompetencePeriod,
    payment_date: date,
    resolution: PolicyResolution,
) -> LedgerEntry:
    """Build the ledger entry for a standard cash or absence event.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.ledger.LedgerEntry` posted
        to ``EMPLOYEE_DEDUCTIONS`` for absences and ``CASH_EARNINGS`` otherwise.
    """
    if isinstance(event, AbsenceEvent):
        return _make_entry(
            f"deduction_{evt_id}",
            evt_id,
            kind,
            cp,
            payment_date,
            AccountKind.EMPLOYEE_DEDUCTIONS,
            -gross,
            policy_id=resolution.policy_id,
        )
    return _make_entry(
        f"cash_{evt_id}",
        evt_id,
        kind,
        cp,
        payment_date,
        AccountKind.CASH_EARNINGS,
        gross,
        policy_id=resolution.policy_id,
    )


def _process_sickness_case_event(
    event: SicknessCaseEvent,
    evt_id: str,
    cp: CompetencePeriod,
    payment_date: date,
    resolver: PolicyResolver,
    context: PolicyContext,
) -> tuple[list[PayItem], list[LedgerEntry], Decimal, Decimal, Decimal]:
    """Decompose a SicknessCaseEvent into absence + sickness integration components.

    Returns:
        ``(items, entries, delta_inps, delta_tfr, delta_irpef)`` where the deltas
        are the net contribution to the INPS/TFR/IRPEF bases for the period.
    """
    case = event.case
    resolution = _require_resolution(resolver, "sickness_item", context)
    treatment = _treatment_from_resolution(resolution)

    absence = money(case.gross_daily * case.working_days)
    inps_indemnity = money(
        case.gross_daily * case.inps_daily_rate * case.indemnifiable_days
    )
    top_up_factor = (
        case.integration_rate - case.inps_daily_rate
    ) * case.indemnifiable_days
    employer_integration = (
        money(case.gross_daily * top_up_factor) if top_up_factor > _ZERO else _ZERO
    )
    carenza = money(
        case.gross_daily * case.carenza_integration_rate * case.waiting_period_days
    )

    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    di_total = dt_total = dirpef_total = _ZERO

    abs_id = f"{evt_id}_abs"
    items.append(
        AbsenceDeduction(
            item_id=abs_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(case.working_days),
            amount=absence,
            absence_days=Decimal(case.working_days),
        )
    )
    entries.append(
        _make_entry(
            f"deduction_{abs_id}",
            abs_id,
            "absence_deduction",
            cp,
            payment_date,
            AccountKind.EMPLOYEE_DEDUCTIONS,
            absence,
            policy_id=resolution.policy_id,
        )
    )
    di, dt, dirpef = _treatment_deltas(treatment, -absence)
    di_total += di
    dt_total += dt
    dirpef_total += dirpef

    for component_id, amount in (
        (f"{evt_id}_inps", inps_indemnity),
        (f"{evt_id}_intg", employer_integration),
        (f"{evt_id}_crnz", carenza),
    ):
        if amount <= _ZERO:
            continue
        sick_days = (
            Decimal(case.indemnifiable_days)
            if "inps" in component_id or "intg" in component_id
            else Decimal(case.waiting_period_days)
        )
        items.append(
            SicknessItem(
                item_id=component_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amount,
                sick_days=sick_days,
            )
        )
        entries.append(
            _make_entry(
                f"cash_{component_id}",
                component_id,
                "sickness_item",
                cp,
                payment_date,
                AccountKind.CASH_EARNINGS,
                amount,
                policy_id=resolution.policy_id,
            )
        )
        di, dt, dirpef = _treatment_deltas(treatment, amount)
        di_total += di
        dt_total += dt
        dirpef_total += dirpef

    return items, entries, di_total, dt_total, dirpef_total
