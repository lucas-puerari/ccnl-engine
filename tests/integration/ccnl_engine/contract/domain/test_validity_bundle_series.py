"""Data contract of every rule series of the bundle.

For each series of each bundled CCNL: the day before its first period has
no value and names the first date; the first supported date returns its
value; at every tranche boundary the day before returns the previous
period, the boundary and the day after the new one; a declared gap raises
its kind and the date the values resume; a date long after the last start
returns the last period.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from itertools import pairwise
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from ccnl_engine.contract.domain.validity import (
    SalaryGapKind,
    SeriesGapError,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.contract.service.discovery import list_contracts
from ccnl_engine.contract.service.loaders import load_ccnl

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.contract.domain.identity import CCNL

_ALL_CCNL: list[CCNL] = [load_ccnl(c.ccnl_id + ".json") for c in list_contracts()]
_DAY = timedelta(days=1)
_LATER = timedelta(days=3 * 365)

#: What a series returns on a date: a value, or a gap with its kind (``None``
#: before the series) and the date the values resume.
type Reading = Decimal | tuple[SalaryGapKind | None, date | None]


def _series_of(node: object, path: str) -> Iterator[tuple[str, TimeSeries]]:
    """Yield every time series reachable from ``node`` with its path.

    Yields:
        The dotted path of each series and the series.
    """
    if isinstance(node, TimeSeries):
        yield path, node
    elif isinstance(node, BaseModel):
        for name in type(node).model_fields:
            yield from _series_of(getattr(node, name), f"{path}.{name}")
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _series_of(value, f"{path}[{key}]")
    elif isinstance(node, tuple | list):
        for i, value in enumerate(node):
            yield from _series_of(value, f"{path}[{i}]")


def _read(series: TimeSeries, day: date) -> Reading:
    try:
        return series.value_at(day)
    except SeriesGapError as gap:
        return gap.gap_kind, gap.resumes_on


def _expected(period: ValidityPeriod) -> Reading:
    if period.value is not None:
        return period.value
    return period.gap_kind, period.valid_until


def _violations(path: str, series: TimeSeries) -> Iterator[str]:
    """Yield each date on which ``series`` breaks its data contract.

    Yields:
        A description of each violation.
    """
    periods = series.periods
    first = periods[0]
    checks: list[tuple[date, Reading]] = [
        (first.valid_from - _DAY, (None, first.valid_from)),
        (first.valid_from, _expected(first)),
        (periods[-1].valid_from + _LATER, _expected(periods[-1])),
    ]
    for before, after in pairwise(periods):
        boundary = after.valid_from
        checks += [(boundary - _DAY, _expected(before)), (boundary, _expected(after))]
        following = boundary + _DAY
        if after.valid_until is None or following < after.valid_until:
            checks.append((following, _expected(after)))
    for day, expected in checks:
        found = _read(series, day)
        if found != expected:
            yield f"{path} on {day}: {found!r}, expected {expected!r}"


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
def test_every_series_honours_its_dates(ccnl: CCNL) -> None:
    """First date, tranche boundaries, gaps and later dates of each series."""
    found = list(_series_of(ccnl, ccnl.meta.ccnl_id))
    assert found, "a CCNL has at least its base salary series"
    assert [v for path, s in found for v in _violations(path, s)] == []


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
def test_every_series_has_a_supported_date(ccnl: CCNL) -> None:
    """No series of the bundle is made of gaps only."""
    empty = [
        path
        for path, series in _series_of(ccnl, ccnl.meta.ccnl_id)
        if all(period.is_gap for period in series.periods)
    ]
    assert empty == []
