"""Withholding plan of a period: its slots, the pay still to come, per-slot shares.

The IRPEF projection and the year-end conguaglio run on the
:class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`, one slot per
payslip.  The CCNL ``additional_months`` parameter is an equivalent-months
entitlement (13.5 for Cooperative Sociali) and is never used as a slot count.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _apply_extra_month_policy,
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.domain.calendar import ExtraMonthEntitlement, WorkCalendar
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import PayItem, TaxCreditItem
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.domain.tax import TaxComputation
    from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)
# Future extra months are projected at full accrual; proration of the rateo on
# the employment period is not anticipated by the projection.
_FULL_ACCRUAL_MONTHS = 12


def resolve_withholding_schedule(
    requested: WithholdingSchedule | None,
    ccnl: CCNL,
    competence: date,
    fiscal_year: int,
) -> WithholdingSchedule:
    """Return the withholding schedule the period must use.

    Args:
        requested: Schedule supplied with the request (the year orchestrator
            passes the one it runs), or ``None`` for a standalone period.
        ccnl: The contract, whose ``additional_months`` gives the standard
            calendar when no schedule is supplied.
        competence: Competence date used to read ``additional_months``.
        fiscal_year: Tax year of the period.

    Returns:
        ``requested`` when given; otherwise one slot per payslip of the
        standard calendar built from the CCNL entitlement.
    """
    if requested is not None:
        return requested
    entitlement = ExtraMonthEntitlement.of(
        ccnl.parameters.additional_months.value_at(competence)
    )
    calendar = WorkCalendar.from_additional_months(fiscal_year, entitlement)
    return WithholdingSchedule.from_calendar(calendar)


def upcoming_recurring_gross(
    regular_chain: MonthlyPayChain,
    schedule: WithholdingSchedule,
    slots_closed: int,
) -> Decimal:
    """Project the recurring gross of the slots after the current one.

    Each upcoming slot is valued with the pay chain its run kind would pay:
    the regular chain for a regular month, the extra-month chain scaled by
    the slot's ``pay_fraction`` for a tredicesima or quattordicesima.

    Args:
        regular_chain: Pay chain of a regular month, before any extra-month
            adjustment of the current run.
        schedule: Withholding schedule of the year.
        slots_closed: Withholding slots already closed this tax year.

    Returns:
        Sum of the projected gross of the upcoming slots, zero on the last.
    """
    total = _ZERO
    for slot in schedule.upcoming(slots_closed):
        chain = _apply_extra_month_policy(
            regular_chain,
            slot.run.run_kind,
            _FULL_ACCRUAL_MONTHS,
            max_fraction=slot.pay_fraction,
        )
        total += money(chain.base + chain.seniority + chain.allowances_total)
    return total


def slot_share(annual: Decimal, schedule: WithholdingSchedule) -> Decimal:
    """Split an annual amount evenly over the payslips of the year.

    Returns:
        ``annual / run_count`` rounded to cents.
    """
    return money(annual / schedule.run_count.value)


def somma_esente_credit(
    tax_computation: TaxComputation,
    schedule: WithholdingSchedule,
    resolver: PolicyResolver,
    policy_context: PolicyContext,
    competence_period: CompetencePeriod,
    payment_date: date,
    run_id: str,
) -> tuple[Decimal, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return this run's share of the somma esente (L. 207/2024) and its postings.

    Returns:
        ``(amount, pay_items, ledger_entries)``; empty postings and zero when
        no somma esente is due on the projected annual income.
    """
    annual = next(
        (c.amount for c in tax_computation.components if c.name == "somma_esente"),
        _ZERO,
    )
    amount = slot_share(annual, schedule) if annual > _ZERO else _ZERO
    if amount <= _ZERO:
        return _ZERO, (), ()
    credit_pid = _require_resolution(
        resolver, "tax_credit_item", policy_context
    ).policy_id
    item_id = f"somma_esente_{run_id}"
    item = TaxCreditItem(
        item_id=item_id,
        competence_period=competence_period,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        "tax_credit_item",
        competence_period,
        payment_date,
        AccountKind.CREDITS,
        amount,
        policy_id=credit_pid,
    )
    return amount, (item,), (entry,)
