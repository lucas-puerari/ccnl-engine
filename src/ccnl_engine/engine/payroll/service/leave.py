"""Leave accrual service — ferie e permessi maturati."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import LeaveRules
    from ccnl_engine.engine.payroll.domain.supplements import LeaveInput

_MONTHS_PER_YEAR = Decimal(12)


def _resolve_annual_days(
    leave_rules: LeaveRules,
    service_months: int | None,
) -> Decimal:
    """Return the applicable annual leave entitlement in days.

    When ``service_months`` is known and ``leave_rules.entitlement_tiers``
    is non-empty, the tier with the highest ``service_months_min`` that
    the worker has satisfied wins. Falls back to
    ``leave_rules.default_annual_days`` when no tier matches or seniority
    is unknown.

    Returns:
        Annual entitlement in days (>= 0).
    """
    if service_months is not None and leave_rules.entitlement_tiers:
        eligible = [
            t
            for t in leave_rules.entitlement_tiers
            if service_months >= t.service_months_min
        ]
        if eligible:
            best = max(eligible, key=lambda t: t.service_months_min)
            return best.annual_days
    return leave_rules.default_annual_days


def compute_leave(
    leave_input: LeaveInput,
    leave_rules: LeaveRules,
    service_months: int | None,
) -> tuple[Decimal, Decimal, Decimal]:
    """Compute monthly leave accrual, taken days, and balance.

    The accrual is ``annual_entitlement / 12``, rounded to two decimal
    places. The balance is ``accrued - taken``; it may be negative when the
    worker took more days than accrued in the period.

    None of the returned values mutates ``gross_annual`` or ``net_annual``;
    they are purely informational.

    Args:
        leave_input: Caller-supplied taken-day count for the period.
        leave_rules: CCNL leave rules (annual entitlement and tiers).
        service_months: Worker's total months of service, or ``None`` when
            expressed only as an increment count.

    Returns:
        A 3-tuple of
        ``(leave_accrued_days_monthly, leave_taken_days_monthly,
        leave_balance_days)``.
    """
    annual_days = _resolve_annual_days(leave_rules, service_months)
    accrued_monthly = money(annual_days / _MONTHS_PER_YEAR)
    taken = leave_input.taken_days
    balance = money(accrued_monthly - taken)
    return accrued_monthly, taken, balance
