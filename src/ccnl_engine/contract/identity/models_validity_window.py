"""Validity window of a CCNL: the dates on which every rule has a value.

A rule of the bundle is a :class:`~ccnl_engine.contract.identity.rules_validity\
.TimeSeries`.  It has no value before its first period and in a ``missing``
or ``unknown`` gap period; a run that reads it on such a date raises
:class:`~ccnl_engine.errors.MissingRuleError`.  A
``not_applicable`` gap is not a hole: the rule is not in force and a run
does not read it.  The window of a CCNL is the last span of dates on which
every one of its rules is covered, so no run inside it meets a bundle gap.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

from pydantic import BaseModel

from ccnl_engine.contract.identity.rules_validity import SalaryGapKind, TimeSeries

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.rules_validity import ValidityPeriod

__all__ = ["ValidityWindow", "model_window", "rules_window", "series_window"]

_ONE_DAY = timedelta(days=1)


@dataclass(frozen=True, slots=True)
class ValidityWindow:
    """A span of dates, both ends included.

    Attributes:
        first_day: First date of the span.
        last_day: Last date of the span; ``None`` when it is open-ended.
    """

    first_day: date
    last_day: date | None = None

    def covers(self, day: date) -> bool:
        """Return whether ``day`` falls within the span.

        Returns:
            ``True`` from :attr:`first_day` to :attr:`last_day` included.
        """
        return self.first_day <= day and (self.last_day is None or day <= self.last_day)

    def intersect(self, other: ValidityWindow) -> ValidityWindow | None:
        """Return the dates both spans cover.

        Returns:
            The common span, ``None`` when the spans do not overlap.
        """
        first = max(self.first_day, other.first_day)
        ends = [d for d in (self.last_day, other.last_day) if d is not None]
        last = min(ends) if ends else None
        if last is not None and last < first:
            return None
        return ValidityWindow(first, last)


def _covered(period: ValidityPeriod) -> bool:
    return period.gap_kind in {None, SalaryGapKind.NOT_APPLICABLE}


def series_window(series: TimeSeries) -> ValidityWindow | None:
    """Return the last span of dates on which ``series`` is covered.

    A date is covered when its period carries a value or a
    ``not_applicable`` gap.

    Returns:
        The last run of covered periods, ``None`` when every period is a
        ``missing`` or ``unknown`` gap.
    """
    window: ValidityWindow | None = None
    start: date | None = None
    for period in series.periods:
        if _covered(period):
            start = period.valid_from if start is None else start
            continue
        if start is not None:
            window = ValidityWindow(start, period.valid_from - _ONE_DAY)
        start = None
    return window if start is None else ValidityWindow(start)


def rules_window(rules: Iterable[TimeSeries]) -> ValidityWindow | None:
    """Return the dates on which every series of ``rules`` is covered.

    Returns:
        The intersection of the window of each series; ``None`` when one
        series has no window or two windows do not overlap, and the
        open-ended window from :attr:`date.min` when ``rules`` is empty.
    """
    window: ValidityWindow | None = ValidityWindow(date.min)
    for series in rules:
        own = series_window(series)
        if window is None or own is None:
            return None
        window = window.intersect(own)
    return window


def model_window(model: BaseModel) -> ValidityWindow | None:
    """Return the dates on which every rule of ``model`` has a value.

    Every series reachable from the model is read; for a CCNL, the pay of
    each level, the parameters and the work rules.  A run inside the window
    never meets a gap of the bundle; a run outside it raises
    :class:`~ccnl_engine.errors.MissingRuleError` when it
    reads a rule not covered on its date.

    Returns:
        The window, ``None`` when no date covers every rule.
    """
    return rules_window(_series_in(model))


def _series_in(node: object) -> Iterator[TimeSeries]:
    """Yield every :class:`TimeSeries` reachable from ``node``.

    Yields:
        The series held by the fields, mappings and sequences of ``node``.
    """
    if isinstance(node, TimeSeries):
        yield node
        return
    children: Iterable[object]
    if isinstance(node, BaseModel):
        children = (getattr(node, name) for name in type(node).model_fields)
    elif isinstance(node, Mapping):
        children = node.values()
    elif isinstance(node, tuple | list):
        children = node
    else:
        return
    for child in children:
        yield from _series_in(child)
