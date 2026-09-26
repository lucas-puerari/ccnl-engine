"""Walk every date-indexed rule of a CCNL, in the order the diff reports it.

Each rule is a :class:`~ccnl_engine.contract.domain.validity.TimeSeries`
with the path, label and unit :func:`~ccnl_engine.diff.service.compute\
.diff_ccnl` reports a change of it under.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.contract.domain.seniority import (
        SeniorityIncrements,
        SeniorityTier,
    )
    from ccnl_engine.contract.domain.validity import TimeSeries

__all__ = ["DatedRule", "dated_rules"]


@dataclass(frozen=True)
class DatedRule:
    """One date-indexed rule of a CCNL.

    Attributes:
        path: Location of the rule in the CCNL tree.
        label: Human-readable name of the rule.
        unit: Unit of its values, e.g. ``"EUR/month"``.
        series: Values of the rule over time.
    """

    path: str
    label: str
    unit: str
    series: TimeSeries


def dated_rules(ccnl: CCNL) -> Iterator[DatedRule]:
    """Yield every date-indexed rule of *ccnl*.

    Salary tranches, allowances, hourly divisor, additional months,
    seniority amounts, employer-fund rates and overtime bands, in this order.

    Yields:
        One :class:`DatedRule` per time series.
    """
    for level in ccnl.levels:
        yield DatedRule(
            f"levels[{level.code}].base_salary",
            f"Level {level.code} - base salary",
            "EUR/month",
            level.base_salary,
        )
        for allowance in level.fixed_allowances:
            yield DatedRule(
                f"levels[{level.code}].fixed_allowances[{allowance.code}].monthly",
                f"Allowance {allowance.code} - monthly (Level {level.code})",
                "EUR/month",
                allowance.monthly,
            )
    params = ccnl.parameters
    yield DatedRule(
        "parameters.hourly_divisor",
        "Parameter - hourly divisor",
        "hours",
        params.hourly_divisor,
    )
    yield DatedRule(
        "parameters.additional_months",
        "Parameter - additional months",
        "months",
        params.additional_months,
    )
    yield from _seniority_rules(params.seniority_increments)
    for fund in params.employer_funds:
        yield DatedRule(
            f"parameters.employer_funds[{fund.code}].rate",
            f"Employer fund {fund.code} - rate",
            "%",
            fund.rate,
        )
    work_rules = ccnl.work_rules
    if work_rules is not None and work_rules.time_supplements is not None:
        for band in work_rules.time_supplements.overtime_bands:
            yield DatedRule(
                f"work_rules.time_supplements.overtime_bands[{band.code}].rate",
                f"Overtime/supplement band {band.code} - rate",
                "%",
                band.rate,
            )


def _seniority_rules(si: SeniorityIncrements) -> Iterator[DatedRule]:
    """Yield every time series inside a SeniorityIncrements block.

    Yields:
        One :class:`DatedRule` per amount.
    """
    for level_code, ts in si.amount_by_level.items():
        yield DatedRule(
            f"parameters.seniority_increments.amount_by_level[{level_code}]",
            f"Seniority increment - Level {level_code}",
            "EUR/month",
            ts,
        )
    for i, tier in enumerate(si.tiers):
        yield from _tier_rules(tier, i)
    for cat, by_level in si.amount_by_level_by_category.items():
        yield from _category_rules(cat, by_level)
    if si.apprentice_amount is not None:
        yield DatedRule(
            "parameters.seniority_increments.apprentice_amount",
            "Seniority increment - apprentice amount",
            "EUR/month",
            si.apprentice_amount,
        )


def _tier_rules(tier: SeniorityTier, index: int) -> Iterator[DatedRule]:
    for level_code, ts in tier.amount_by_level.items():
        yield DatedRule(
            (
                f"parameters.seniority_increments"
                f".tiers[{index}].amount_by_level[{level_code}]"
            ),
            f"Seniority increment - tier {index + 1}, Level {level_code}",
            "EUR/month",
            ts,
        )


def _category_rules(
    category: WorkerCategory, by_level: Mapping[str, TimeSeries]
) -> Iterator[DatedRule]:
    for level_code, ts in by_level.items():
        yield DatedRule(
            (
                f"parameters.seniority_increments"
                f".amount_by_level_by_category[{category}][{level_code}]"
            ),
            f"Seniority increment - {category}, Level {level_code}",
            "EUR/month",
            ts,
        )
