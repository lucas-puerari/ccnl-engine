"""Temporal coverage of the rule series a run reads.

A run reads the base salary of its level on the competence date, then the
other series of the level and of the CCNL on the same date.  Each of them
must therefore cover the dates of the pay table it applies to: from the
first base salary value of the level (of any level, for a CCNL-wide
series).  A range the bundle has no value for is declared with a gap
period (:class:`~ccnl_engine.contract.identity.rules_validity.SalaryGapKind`),
never left out.

The hourly divisor is not required: a run reads it only for a domestic
CCNL, and the bundle invariants already forbid a gap in it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from datetime import date

    from ccnl_engine.contract.compensation.models import CCNLParameters, Level
    from ccnl_engine.contract.identity.rules_validity import TimeSeries
    from ccnl_engine.contract.seniority.models import SeniorityIncrements

__all__ = ["assert_series_coverage", "required_series"]

#: A series a run reads: its location, the date it must cover from, itself.
type RequiredSeries = tuple[str, date, TimeSeries]


def _pay_table_start(level: Level) -> date | None:
    """Return the first date the base salary of ``level`` has a value.

    Returns:
        The start of its first period with a value, ``None`` without one.
    """
    periods = level.base_salary.periods
    return next((p.valid_from for p in periods if not p.is_gap), None)


def required_series(
    levels: Sequence[Level], parameters: CCNLParameters
) -> Iterator[RequiredSeries]:
    """Yield each series a run reads with the date it must cover from.

    Yields:
        The location of the series in the data file, the first date of the
        pay table it applies to, and the series.
    """
    starts = {level.code: _pay_table_start(level) for level in levels}
    known = [day for day in starts.values() if day is not None]
    if not known:
        return
    start = min(known)
    yield "parameters.additional_months", start, parameters.additional_months
    increments = parameters.seniority_increments
    prefix = "parameters.seniority_increments"
    if increments.apprentice_amount is not None:
        yield f"{prefix}.apprentice_amount", start, increments.apprentice_amount
    for level in levels:
        level_start = starts[level.code]
        if level_start is not None:
            yield from _level_series(level, level_start, increments)


def _level_series(
    level: Level, start: date, increments: SeniorityIncrements
) -> Iterator[RequiredSeries]:
    """Yield the allowance and seniority series of one level.

    Yields:
        Each series of the level with ``start``, the start of its pay table.
    """
    code, prefix = level.code, "parameters.seniority_increments"
    for allowance in level.fixed_allowances:
        path = f"levels[{code}].fixed_allowances[{allowance.code}].monthly"
        yield path, start, allowance.monthly
    if code in increments.amount_by_level:
        yield (
            f"{prefix}.amount_by_level[{code}]",
            start,
            increments.amount_by_level[code],
        )
    for category, amounts in increments.amount_by_level_by_category.items():
        if code in amounts:
            path = f"{prefix}.amount_by_level_by_category[{category}][{code}]"
            yield path, start, amounts[code]
    for i, tier in enumerate(increments.tiers):
        if code in tier.amount_by_level:
            path = f"{prefix}.tiers[{i}].amount_by_level[{code}]"
            yield path, start, tier.amount_by_level[code]


def assert_series_coverage(levels: Sequence[Level], parameters: CCNLParameters) -> None:
    """Reject a series a run reads that starts after its pay table.

    Raises:
        ValueError: If a required series starts after the date it must
            cover from.
    """
    for path, start, series in required_series(levels, parameters):
        first = series.periods[0].valid_from
        if first > start:
            msg = (
                f"{path} starts on {first}, after the pay table it applies to "
                f"({start}): declare the period from {start} with a gap_kind"
            )
            raise ValueError(msg)
