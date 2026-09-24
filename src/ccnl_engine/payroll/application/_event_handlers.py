"""Typed event handlers and dispatch registry for variable work events.

Each handler is a pure function: it takes an event and a context object, and
returns an :class:`EventEffect` that carries accounting items, ledger entries,
and contribution-base deltas.  The fringe handler additionally returns updated
accumulator values.

The registry ``_HANDLER_REGISTRY`` maps each concrete event type to its handler.
A companion test asserts that the registry covers every member of ``WorkEvent``,
providing the same exhaustiveness guarantee as the ``assert_never`` it replaces.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from ccnl_engine.payroll.application._event_items import (
    _fringe_bases,
    _make_standard_event_entry,
    _process_sickness_case_event,
    _standard_event_gross,
    _standard_event_item,
    _treatment_deltas,
)
from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    CompetencePeriod,
    ContractRenewalArrears,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FringeBenefitItem,
    PayItem,
    TfrSettlementItem,
    WelfareItem,
)
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


@dataclass(frozen=True)
class _EventHandlerCtx:
    """Immutable context passed to every event handler.

    Carries all inputs that are invariant across loop iterations, plus the
    current fringe accumulators which may change after each FringeEvent.
    """

    evt_id: str
    cp: CompetencePeriod
    payment_date: date
    resolver: PolicyResolver
    context: PolicyContext
    fringe_threshold: Decimal
    cumulative_fringe: Decimal
    cumulative_taxed: Decimal


@dataclass
class EventEffect:
    """Accounting outputs and contribution-base deltas from one event.

    Attributes:
        items: Pay items created by the handler.
        entries: Ledger entries posted by the handler.
        inps_delta: Increase in the INPS contribution base.
        tfr_delta: Increase in the TFR accrual base.
        irpef_delta: Increase in the IRPEF taxable base.
        substitute_delta: Increase in the substitute-tax base (PdR only).
        fringe_value: Total fringe benefit value (FringeEvent only).
        fringe_inps: Fringe INPS-taxable portion (FringeEvent only).
        fringe_irpef: Fringe IRPEF-taxable portion (FringeEvent only).
        new_cumulative_fringe: Updated cumulative fringe YTD (FringeEvent only).
        new_cumulative_taxed: Updated cumulative taxed fringe (FringeEvent only).
    """

    items: list[PayItem] = field(default_factory=list)
    entries: list[LedgerEntry] = field(default_factory=list)
    inps_delta: Decimal = _ZERO
    tfr_delta: Decimal = _ZERO
    irpef_delta: Decimal = _ZERO
    substitute_delta: Decimal = _ZERO
    fringe_value: Decimal = _ZERO
    fringe_inps: Decimal = _ZERO
    fringe_irpef: Decimal = _ZERO
    new_cumulative_fringe: Decimal | None = None
    new_cumulative_taxed: Decimal | None = None


def _handle_standard(
    event: OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | BonusEvent,
    ctx: _EventHandlerCtx,
) -> EventEffect:
    """Handle standard work-time and bonus events.

    Returns:
        Handler result with pay item, ledger entry, and INPS/TFR/IRPEF deltas.
    """
    gross = _standard_event_gross(event)
    item, kind = _standard_event_item(
        event, gross, ctx.evt_id, ctx.cp, ctx.payment_date
    )
    resolution = _require_resolution(ctx.resolver, kind, ctx.context)
    treatment = _treatment_from_resolution(resolution)
    di, dt, dirpef = _treatment_deltas(treatment, gross)
    result = EventEffect(
        items=[item],
        entries=[
            _make_standard_event_entry(
                event,
                gross,
                ctx.evt_id,
                kind,
                ctx.cp,
                ctx.payment_date,
                resolution,
            )
        ],
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
    )
    if treatment.substitute:
        result.substitute_delta = gross
    return result


def _handle_welfare(event: WelfareEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle welfare benefit events.

    Returns:
        Handler result with WelfareItem posted to NON_CASH_BENEFITS.
    """
    gross = event.amount
    welfare_resolution = _require_resolution(ctx.resolver, "welfare_item", ctx.context)
    item = WelfareItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        entries=[
            _make_entry(
                f"ncb_{ctx.evt_id}",
                ctx.evt_id,
                "welfare_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.NON_CASH_BENEFITS,
                gross,
                policy_id=welfare_resolution.policy_id,
            )
        ],
    )


def _handle_fringe(event: FringeEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle fringe benefit events (with running accumulator update).

    Returns:
        Handler result with fringe item, ledger entry, contribution-base deltas,
        and updated ``new_cumulative_fringe`` / ``new_cumulative_taxed`` values.
    """
    gross = event.amount
    fringe_inps, fringe_irpef, new_cumulative_fringe = _fringe_bases(
        gross, ctx.cumulative_fringe, ctx.fringe_threshold, ctx.cumulative_taxed
    )
    new_cumulative_taxed = ctx.cumulative_taxed + fringe_inps
    fringe_resolution = _require_resolution(
        ctx.resolver, "fringe_benefit_item", ctx.context
    )
    item = FringeBenefitItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        entries=[
            _make_entry(
                f"ncb_{ctx.evt_id}",
                ctx.evt_id,
                "fringe_benefit_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.NON_CASH_BENEFITS,
                gross,
                policy_id=fringe_resolution.policy_id,
            )
        ],
        inps_delta=fringe_inps,
        irpef_delta=fringe_irpef,
        fringe_value=gross,
        fringe_inps=fringe_inps,
        fringe_irpef=fringe_irpef,
        new_cumulative_fringe=new_cumulative_fringe,
        new_cumulative_taxed=new_cumulative_taxed,
    )


def _handle_arrears(event: ArrearsEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle contract-renewal arrears (tassazione separata).

    Returns:
        Handler result with arrears item posted to CASH_EARNINGS and SEPARATE_TAX.
    """
    gross = event.amount
    sep_tax = money(gross * event.separate_tax_rate)
    arrears_resolution = _require_resolution(
        ctx.resolver, "contract_renewal_arrears", ctx.context
    )
    item = ContractRenewalArrears(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        entries=[
            _make_entry(
                f"cash_{ctx.evt_id}",
                ctx.evt_id,
                "contract_renewal_arrears",
                ctx.cp,
                ctx.payment_date,
                AccountKind.CASH_EARNINGS,
                gross,
                policy_id=arrears_resolution.policy_id,
            ),
            _make_entry(
                f"sep_tax_{ctx.evt_id}",
                ctx.evt_id,
                "contract_renewal_arrears",
                ctx.cp,
                ctx.payment_date,
                AccountKind.SEPARATE_TAX,
                sep_tax,
                policy_id=arrears_resolution.policy_id,
            ),
        ],
        inps_delta=gross,
    )


def _handle_bilateral_fund(
    event: BilateralFundEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle bilateral or health fund contribution events.

    Returns:
        Handler result with employee and employer items posted to the
        BILATERAL_FUND_EMPLOYEE and BILATERAL_FUND_EMPLOYER accounts.
    """
    emp_id = f"{ctx.evt_id}_emp"
    er_id = f"{ctx.evt_id}_er"
    emp_resolution = _require_resolution(
        ctx.resolver, "employee_withholding_item", ctx.context
    )
    er_resolution = _require_resolution(
        ctx.resolver, "employer_contribution_item", ctx.context
    )
    emp_item = EmployeeWithholdingItem(
        item_id=emp_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=event.employee_amount,
    )
    er_item = EmployerContributionItem(
        item_id=er_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=event.employer_amount,
    )
    return EventEffect(
        items=[emp_item, er_item],
        entries=[
            _make_entry(
                f"bilat_emp_{ctx.evt_id}",
                emp_id,
                "employee_withholding_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.BILATERAL_FUND_EMPLOYEE,
                event.employee_amount,
                policy_id=emp_resolution.policy_id,
            ),
            _make_entry(
                f"bilat_er_{ctx.evt_id}",
                er_id,
                "employer_contribution_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.BILATERAL_FUND_EMPLOYER,
                event.employer_amount,
                policy_id=er_resolution.policy_id,
            ),
        ],
    )


def _handle_termination_tfr(
    event: TerminationTFREvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle TFR settlement at cessazione.

    Returns:
        Handler result with TFR item posted to TFR_SETTLEMENT and SEPARATE_TAX.
    """
    gross = event.amount
    sep_tax = money(gross * event.separate_tax_rate)
    tfr_settle_resolution = _require_resolution(
        ctx.resolver, "tfr_settlement_item", ctx.context
    )
    item = TfrSettlementItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        entries=[
            _make_entry(
                f"tfr_settle_{ctx.evt_id}",
                ctx.evt_id,
                "tfr_settlement_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.TFR_SETTLEMENT,
                gross,
                policy_id=tfr_settle_resolution.policy_id,
            ),
            _make_entry(
                f"sep_tax_{ctx.evt_id}",
                ctx.evt_id,
                "tfr_settlement_item",
                ctx.cp,
                ctx.payment_date,
                AccountKind.SEPARATE_TAX,
                sep_tax,
                policy_id=tfr_settle_resolution.policy_id,
            ),
        ],
    )


def _handle_sickness_case(
    event: SicknessCaseEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle structured sick-leave episodes.

    Returns:
        Handler result with sickness items, ledger entries, and INPS/TFR/IRPEF deltas.
    """
    sc_items, sc_entries, di, dt, dirpef = _process_sickness_case_event(
        event, ctx.evt_id, ctx.cp, ctx.payment_date, ctx.resolver, ctx.context
    )
    return EventEffect(
        items=list(sc_items),
        entries=list(sc_entries),
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
    )


# ---------------------------------------------------------------------------
# Handler registry — one entry per concrete WorkEvent type.
# The test suite asserts this dict covers every get_args(WorkEvent) member,
# providing the same exhaustiveness guarantee as the isinstance chain.
# ---------------------------------------------------------------------------

_EventHandlerFn = Callable[[Any, _EventHandlerCtx], EventEffect]

_HANDLER_REGISTRY: dict[type, _EventHandlerFn] = {
    OvertimeEvent: _handle_standard,
    NightShiftEvent: _handle_standard,
    HolidayWorkEvent: _handle_standard,
    AbsenceEvent: _handle_standard,
    SickLeaveEvent: _handle_standard,
    BonusEvent: _handle_standard,
    WelfareEvent: _handle_welfare,
    FringeEvent: _handle_fringe,
    ArrearsEvent: _handle_arrears,
    BilateralFundEvent: _handle_bilateral_fund,
    TerminationTFREvent: _handle_termination_tfr,
    SicknessCaseEvent: _handle_sickness_case,
}
