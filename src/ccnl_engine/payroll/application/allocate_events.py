"""Aggregate variable work events into accounting entries and totals."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, assert_never

from ccnl_engine.payroll.application._event_items import (
    _check_event_date,
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
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
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
    WorkEvent,
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
class _EventTotals:
    """Aggregated INPS/TFR/IRPEF bases from variable work events."""

    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal
    fringe_value: Decimal
    fringe_inps: Decimal
    fringe_irpef: Decimal
    substitute_base: Decimal


def _process_events(
    events: tuple[WorkEvent, ...],
    cp: CompetencePeriod,
    payment_date: date,
    tag: str,
    date_ctx: EffectiveDateContext,
    resolver: PolicyResolver,
    context: PolicyContext,
    fringe_threshold: Decimal = _ZERO,
    opening_fringe_ytd: Decimal = _ZERO,
    opening_fringe_taxed: Decimal = _ZERO,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    total_inps = _ZERO
    total_tfr = _ZERO
    total_irpef = _ZERO
    total_substitute = _ZERO
    total_fringe_value = _ZERO
    total_fringe_inps = _ZERO
    total_fringe_irpef = _ZERO
    cumulative_fringe = opening_fringe_ytd
    cumulative_taxed = opening_fringe_taxed
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []

    for i, event in enumerate(events):
        evt_id = f"{tag}_evt{i}"
        _check_event_date(event, date_ctx, i)

        if isinstance(
            event,
            (
                OvertimeEvent,
                NightShiftEvent,
                HolidayWorkEvent,
                AbsenceEvent,
                SickLeaveEvent,
                BonusEvent,
            ),
        ):
            gross = _standard_event_gross(event)
            item, kind = _standard_event_item(event, gross, evt_id, cp, payment_date)
            resolution = _require_resolution(resolver, kind, context)
            treatment = _treatment_from_resolution(resolution)
            di, dt, dirpef = _treatment_deltas(treatment, gross)
            total_inps += di
            total_tfr += dt
            total_irpef += dirpef
            if treatment.substitute:
                total_substitute += gross
            items.append(item)
            entries.append(
                _make_standard_event_entry(
                    event, gross, evt_id, kind, cp, payment_date, resolution
                )
            )
        elif isinstance(event, WelfareEvent):
            gross = event.amount
            welfare_resolution = _require_resolution(resolver, "welfare_item", context)
            item = WelfareItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            items.append(item)
            entries.append(
                _make_entry(
                    f"ncb_{evt_id}",
                    evt_id,
                    "welfare_item",
                    cp,
                    payment_date,
                    AccountKind.NON_CASH_BENEFITS,
                    gross,
                    policy_id=welfare_resolution.policy_id,
                )
            )
        elif isinstance(event, FringeEvent):
            gross = event.amount
            fringe_inps, fringe_irpef, cumulative_fringe = _fringe_bases(
                gross, cumulative_fringe, fringe_threshold, cumulative_taxed
            )
            cumulative_taxed += fringe_inps
            fringe_resolution = _require_resolution(
                resolver, "fringe_benefit_item", context
            )
            item = FringeBenefitItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_inps += fringe_inps
            total_irpef += fringe_irpef
            total_fringe_value += gross
            total_fringe_inps += fringe_inps
            total_fringe_irpef += fringe_irpef
            items.append(item)
            entries.append(
                _make_entry(
                    f"ncb_{evt_id}",
                    evt_id,
                    "fringe_benefit_item",
                    cp,
                    payment_date,
                    AccountKind.NON_CASH_BENEFITS,
                    gross,
                    policy_id=fringe_resolution.policy_id,
                )
            )
        elif isinstance(event, ArrearsEvent):
            gross = event.amount
            sep_tax = money(gross * event.separate_tax_rate)
            arrears_resolution = _require_resolution(
                resolver, "contract_renewal_arrears", context
            )
            item = ContractRenewalArrears(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            items.append(item)
            entries.extend([
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "contract_renewal_arrears",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                    policy_id=arrears_resolution.policy_id,
                ),
                _make_entry(
                    f"sep_tax_{evt_id}",
                    evt_id,
                    "contract_renewal_arrears",
                    cp,
                    payment_date,
                    AccountKind.SEPARATE_TAX,
                    sep_tax,
                    policy_id=arrears_resolution.policy_id,
                ),
            ])
        elif isinstance(event, BilateralFundEvent):
            emp_id = f"{evt_id}_emp"
            er_id = f"{evt_id}_er"
            emp_resolution = _require_resolution(
                resolver, "employee_withholding_item", context
            )
            er_resolution = _require_resolution(
                resolver, "employer_contribution_item", context
            )
            emp_item = EmployeeWithholdingItem(
                item_id=emp_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=event.employee_amount,
            )
            er_item = EmployerContributionItem(
                item_id=er_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=event.employer_amount,
            )
            items.extend((emp_item, er_item))
            entries.extend([
                _make_entry(
                    f"bilat_emp_{evt_id}",
                    emp_id,
                    "employee_withholding_item",
                    cp,
                    payment_date,
                    AccountKind.BILATERAL_FUND_EMPLOYEE,
                    event.employee_amount,
                    policy_id=emp_resolution.policy_id,
                ),
                _make_entry(
                    f"bilat_er_{evt_id}",
                    er_id,
                    "employer_contribution_item",
                    cp,
                    payment_date,
                    AccountKind.BILATERAL_FUND_EMPLOYER,
                    event.employer_amount,
                    policy_id=er_resolution.policy_id,
                ),
            ])
        elif isinstance(event, TerminationTFREvent):
            gross = event.amount
            sep_tax = money(gross * event.separate_tax_rate)
            tfr_settle_resolution = _require_resolution(
                resolver, "tfr_settlement_item", context
            )
            item = TfrSettlementItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            items.append(item)
            entries.extend([
                _make_entry(
                    f"tfr_settle_{evt_id}",
                    evt_id,
                    "tfr_settlement_item",
                    cp,
                    payment_date,
                    AccountKind.TFR_SETTLEMENT,
                    gross,
                    policy_id=tfr_settle_resolution.policy_id,
                ),
                _make_entry(
                    f"sep_tax_{evt_id}",
                    evt_id,
                    "tfr_settlement_item",
                    cp,
                    payment_date,
                    AccountKind.SEPARATE_TAX,
                    sep_tax,
                    policy_id=tfr_settle_resolution.policy_id,
                ),
            ])
        elif isinstance(event, SicknessCaseEvent):
            sc_items, sc_entries, di, dt, dirpef = _process_sickness_case_event(
                event, evt_id, cp, payment_date, resolver, context
            )
            items.extend(sc_items)
            entries.extend(sc_entries)
            total_inps += di
            total_tfr += dt
            total_irpef += dirpef
        else:
            assert_never(event)

    return (
        _EventTotals(
            inps_base=total_inps,
            tfr_base=total_tfr,
            irpef_base=total_irpef,
            fringe_value=total_fringe_value,
            fringe_inps=total_fringe_inps,
            fringe_irpef=total_fringe_irpef,
            substitute_base=total_substitute,
        ),
        tuple(items),
        tuple(entries),
    )
