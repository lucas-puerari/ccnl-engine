"""Daily CCNL integration targets of a work injury."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import InjuryRates, InjuryRules
    from ccnl_engine.absence.insured.rules import MonthPay
    from ccnl_engine.sickness.holiday.models import SicknessHoliday

_ZERO = Decimal(0)


def integration_target(
    rules: InjuryRules,
    pay: MonthPay,
    injury_on: date,
    first: date,
    last: date,
    indemnified_pay: Decimal,
) -> Decimal | None:
    """Return the pay the top-up reaches on the indemnified days.

    Returns:
        ``integration_rate`` of their pay, else the rate of each band on
        the pay of its days; ``None`` without a top-up.
    """
    if rules.integration_rate is not None:
        return rules.integration_rate * indemnified_pay
    if not rules.integration_bands:
        return None
    target = _ZERO
    bands = rules.integration_bands
    for band, after in zip(bands, (*bands[1:], None), strict=True):
        start = max(first, injury_on + timedelta(days=band.day_from))
        end = (
            last
            if after is None
            else min(last, injury_on + timedelta(days=after.day_from - 1))
        )
        target += band.rate * pay.deducted(start, end)[1]
    return target


def holiday_extra(
    rules: InjuryRules,
    rates: InjuryRates,
    pay: MonthPay,
    injury_on: date,
    first: date,
    last: date,
    waiting_end: date,
    daily: Decimal,
    holidays: frozenset[date],
    target: SicknessHoliday,
) -> Decimal:
    """Top each covered holiday up after the pay already due on that day.

    The injury day remains paid in full. On waiting days the employer pays
    the carenza; on later days INAIL and the ordinary CCNL integration count
    toward the target. Compute daily before summing, then round once.

    Returns:
        The employer's additional holiday integration, rounded to cents.
    """
    extra = _ZERO
    for day in sorted(holidays):
        if not first <= day <= last or day == injury_on:
            continue
        quota = pay.deducted(day, day)[1]
        if day <= waiting_end:
            rate = max(rules.carenza_rate or rates.carenza_rate, rates.carenza_rate)
            already = rate * quota
        else:
            insurer = rates.rate_on((day - injury_on).days) * daily
            ordinary = integration_target(rules, pay, injury_on, day, day, quota)
            integration = (
                _ZERO
                if ordinary is None
                else max(
                    ordinary - pay.grossed(insurer, net_basis=rules.net_basis), _ZERO
                )
            )
            already = insurer + integration
        extra += max(target.rate * quota - already, _ZERO)
    return money(extra)
