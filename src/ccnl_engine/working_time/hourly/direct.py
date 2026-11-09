"""Directly quoted sub-sector hourly minima, not monthly wages / divisor."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING, NoReturn

from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from ccnl_engine.working_time.hourly.base import HourlyBase
from ccnl_engine.working_time.supplement.models import HourlyBaseMethod

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.working_time.models import TimeSupplements


def direct_hourly_base(
    supplements: TimeSupplements | None,
    level_code: str | None,
    chain: MonthlyPayChain | None,
    day: date,
    field: str,
    feature: str,
    method: HourlyBaseMethod | None,
    reject: Callable[[str, str, date, str], NoReturn],
) -> HourlyBase | None:
    """Derive a verified direct hourly floor, or defer to monthly rules.

    A floor must name the worker's level and the event date. An unsourced
    floor and individual elements of unknown treatment cannot be silently
    included in the rate. No monthly divisor is used here.

    Returns:
        The direct hourly base, or ``None`` for a CCNL without such a table.
    """
    if supplements is None or not supplements.hourly_minimum_by_level:
        return None
    record = supplements.hourly_base_provenance
    if record is None or record.status is not ProvenanceStatus.VERIFIED:
        reject(field, feature, day, "no verified hourly minimum")
    series = supplements.hourly_minimum_by_level.get(level_code or "")
    period = None if series is None else series.period_at(day)
    if period is None or period.value is None:
        reject(field, feature, day, "no hourly minimum for this level and date")
    if chain is not None and any(a.individual for a, _ in chain.allowances):
        reject(
            field,
            feature,
            day,
            "the hourly minimum does not include the worker's individual elements",
        )
    rate = period.value
    return HourlyBase(
        rate,
        rate,
        Decimal(1),
        method or supplements.hourly_base_method,
        (("hourly_minimum", rate),),
        direct=True,
    )
