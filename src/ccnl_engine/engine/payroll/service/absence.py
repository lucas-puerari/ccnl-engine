"""Absence deduction service — assenza non retribuita."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import AbsenceRules, DailyDivisorMethod
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays

_DIVISORE_STANDARD = Decimal(26)


def compute_absence_deduction(
    absence_input: AbsenceDays,
    absence_rules: AbsenceRules,
    gross_monthly: Decimal,
    hourly_rate: Decimal,
) -> Decimal:
    """Compute the monthly absence deduction for unpaid absent days.

    The returned value is a *positive* amount representing how much would
    be deducted from gross for ``absence_input.unpaid_days`` absent days.
    It is informational and does not alter ``gross_annual`` or ``net_annual``;
    callers should subtract it from ``gross_monthly`` themselves when building
    effective-pay figures.

    Two daily-rate methods are supported:

    * ``by_26``: ``gross_monthly / 26 * unpaid_days`` — the standard
      industria divisore giornaliero.
    * ``by_hourly``: ``hourly_rate * daily_hours * unpaid_days`` — for
      contracts that specify a daily working-hours figure.

    Args:
        absence_input: Caller-supplied absent-day count.
        absence_rules: CCNL absence rules specifying the divisor method.
        gross_monthly: The contractual gross monthly pay (pre-absence).
        hourly_rate: The contractual hourly rate (``gross_monthly /
            hourly_divisor``), used only for the ``by_hourly`` method.

    Returns:
        The rounded monthly absence deduction (>= 0).

    Raises:
        ValueError: If ``daily_hours`` is ``None`` when the method is
            ``by_hourly``, or if ``daily_hours`` is not positive.
    """
    if absence_input.unpaid_days == Decimal(0):
        return Decimal(0)

    if absence_rules.daily_divisor_method == DailyDivisorMethod.BY_HOURLY:
        daily_hours = absence_rules.daily_hours
        if daily_hours is None:
            msg = "AbsenceRules.daily_hours is required for by_hourly method"
            raise ValueError(msg)
        if daily_hours <= Decimal(0):
            msg = f"AbsenceRules.daily_hours must be > 0, got {daily_hours}"
            raise ValueError(msg)
        daily_rate = money(hourly_rate * daily_hours)
    else:
        # BY_26: standard industria divisore giornaliero
        daily_rate = money(gross_monthly / _DIVISORE_STANDARD)

    return money(daily_rate * absence_input.unpaid_days)
