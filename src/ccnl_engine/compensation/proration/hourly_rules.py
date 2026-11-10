"""Hourly divisor rule and absent-hours guard for hour-based workers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import AbsenceEvent

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.compensation.hourly.models import HourlyPay, HourlyRate
    from ccnl_engine.employment.fact.inputs import WeeklyHours
    from ccnl_engine.period.requests import PeriodCalculationRequest


def hourly_rule(ccnl: CCNL, name: str, day: date) -> tuple[Decimal | None, Rule]:
    """Return the hourly divisor in force on ``day`` and its rule.

    Returns:
        The divisor, ``None`` when the series has no value on ``day``.
    """
    period = ccnl.parameters.hourly_divisor.period_at(day)
    if period is None:
        return None, (f"{name}:hourly_divisor", None)
    rule: Rule = (f"{name}:hourly_divisor[{period.valid_from}]", period.provenance)
    return period.value, rule


def selected_hourly_rate(
    spec: HourlyPay, roles: frozenset[str] | None, level: str
) -> HourlyRate | None:
    """Select a rate only when its generic role and level were both stated.

    Returns:
        The matching row or ``None`` if the caller has not selected it.
    """
    return next(
        (
            rate
            for rate in spec.rates
            if roles and rate.role in roles and rate.level == level
        ),
        None,
    )


def hourly_ratio(weekly: WeeklyHours | None, full: WeeklyHours | None) -> Decimal:
    """Return the part-time share used by the hourly divisor.

    Returns:
        Contracted weekly hours divided by full-time hours, or one.
    """
    if weekly is not None and full is not None and weekly.value < full.value:
        return weekly.value / full.value
    return Decimal(1)


def reject_hourly_absences(request: PeriodCalculationRequest) -> None:
    """Reject an absence event of a worker paid by the hour.

    Raises:
        InvalidInputError: When the request carries an ``AbsenceEvent``: its
            hours are not among the hours worked, so it would deduct them
            twice.
    """
    for i, event in enumerate(request.events):
        if isinstance(event, AbsenceEvent):
            msg = (
                "the CCNL pays the worker by the hour: the absent hours are "
                "already excluded from PeriodFacts.ordinary_hours_worked, an "
                "AbsenceEvent would deduct them a second time"
            )
            raise InvalidInputError(
                msg, field=f"PeriodFacts.events[{i}]", feature="base_salary"
            )
