"""Withholding plan of a period: its slots, the pay still to come, per-slot shares.

The IRPEF projection and the year-end conguaglio run on the
:class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`, one slot per
payslip.  The CCNL ``additional_months`` parameter is an equivalent-months
entitlement (13.5 for Cooperative Sociali) and is never used as a slot count.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._calendar import standard_calendar
from ccnl_engine.payroll.application._period_utils import _apply_extra_month_policy
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)


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
    calendar = standard_calendar(ccnl, fiscal_year, competence)
    return WithholdingSchedule.from_calendar(calendar)


def upcoming_recurring_gross(
    regular_chain: MonthlyPayChain,
    schedule: WithholdingSchedule,
    slots_closed: int,
) -> Decimal:
    """Project the recurring gross of the slots after the current one.

    Each upcoming slot is valued with the pay chain its run kind would pay:
    the regular chain for a regular month, the extra-month chain scaled by
    the slot's ``pay_fraction`` for a tredicesima or quattordicesima.  Future
    extra months are projected at full accrual; a lower rateo on the
    employment period is settled by the conguaglio of the last slot.

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
            regular_chain, slot.run.run_kind, slot.pay_fraction
        )
        total += money(chain.base + chain.seniority + chain.allowances_total)
    return total


def slot_share(annual: Decimal, schedule: WithholdingSchedule) -> Decimal:
    """Split an annual amount evenly over the payslips of the year.

    Returns:
        ``annual / run_count`` rounded to cents.
    """
    return money(annual / schedule.run_count.value)
