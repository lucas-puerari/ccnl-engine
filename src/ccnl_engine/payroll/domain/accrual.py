"""Extra-month accrual: the qualifying months of a window and the rateo they give.

A tredicesima or quattordicesima accrues one twelfth (rateo) for each month
of its 12-month :class:`~ccnl_engine.payroll.domain.extra_month_schedule.AccrualWindow`
that qualifies for the employment.  The months are counted from dates, never
from the number of payroll runs already closed:

- the window starts at the hire date when the worker was hired inside it;
- it stops at the termination date when the employment ends inside it;
- days of an absence that suspends accrual are not accruing days;
- a calendar month qualifies when its accruing days compare with
  :attr:`MonthAccrualRule.min_days` as :attr:`MonthAccrualRule.comparison`
  says: the CCNL clause when the bundle has one, otherwise the engine
  default (at least 15 days).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.compensation import AccrualComparison

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.extra_month_schedule import (
        AccrualWindow,
        ExtraMonthKind,
        ExtraMonthSchedule,
    )
    from ccnl_engine.provenance.domain.chain import RuleProvenance

__all__ = [
    "DEFAULT_ACCRUAL_RULE_ID",
    "DEFAULT_MONTH_ACCRUAL_RULE",
    "ExtraMonthAccrual",
    "MonthAccrualRule",
    "absence_days",
    "partial_months",
]

_MONTHS_PER_WINDOW = 12
_SHORTEST_MONTH_DAYS = 28
_DEFAULT_MIN_DAYS = 15
#: Rule identifier of the engine default threshold.
DEFAULT_ACCRUAL_RULE_ID = "engine:default_month_accrual_rule"
_DEFAULT_SOURCE = (
    "Engine default, not read from CCNL data: a calendar month with at least "
    "15 accruing days counts as a whole month and a shorter fraction is not "
    "counted. This follows the usual CCNL wording on tredicesima and "
    "quattordicesima ratei; CCNLs differ (some count only fractions above "
    "15 days), so a CCNL whose clause is in the bundle uses that clause."
)


@dataclass(frozen=True)
class MonthAccrualRule:
    """When a calendar month of an accrual window counts as a whole month.

    Attributes:
        min_days: Threshold in accruing calendar days.
        comparison: ``at_least`` counts a month whose days reach
            ``min_days``; ``more_than`` one whose days exceed it.
        source: Where the rule comes from, in words.
        rule: Identifier of the rule: ``<ruleset>:parameters.accrual_rule``
            for a CCNL rule, :data:`DEFAULT_ACCRUAL_RULE_ID` for the default.
        provenance: Provenance of the rule, ``None`` when the caller built
            it or it is the bare engine default.

    Raises:
        ValueError: When a full 28-day month would not count or the
            threshold is below one day.
    """

    min_days: int = _DEFAULT_MIN_DAYS
    source: str = _DEFAULT_SOURCE
    comparison: AccrualComparison = AccrualComparison.AT_LEAST
    rule: str = DEFAULT_ACCRUAL_RULE_ID
    provenance: RuleProvenance | None = None

    def __post_init__(self) -> None:  # noqa: D105
        more_than = self.comparison is AccrualComparison.MORE_THAN
        lowest, highest = (0, 27) if more_than else (1, _SHORTEST_MONTH_DAYS)
        if not lowest <= self.min_days <= highest:
            msg = (
                f"min_days must be between {lowest} and {highest} for "
                f"{self.comparison.value!r}; got {self.min_days}"
            )
            raise ValueError(msg)

    def counts(self, days: int) -> bool:
        """Return whether a month with ``days`` accruing days counts.

        Returns:
            ``days >= min_days`` for ``at_least``, ``days > min_days`` for
            ``more_than``.
        """
        if self.comparison is AccrualComparison.MORE_THAN:
            return days > self.min_days
        return days >= self.min_days

    def qualifying_months(
        self,
        window: AccrualWindow,
        *,
        ended_on: date | None = None,
        non_accruing_days: frozenset[date] = frozenset(),
    ) -> int:
        """Return how many months of ``window`` qualify for the rateo.

        Each of the 12 calendar months from ``window.nominal_start`` is
        intersected with ``[window.start, min(window.end, ended_on)]``; the
        days of ``non_accruing_days`` in it are removed, and the month
        counts when the remaining days pass :meth:`counts`.

        Args:
            window: The accrual window, its start clipped to the hire date.
            ended_on: Last day of employment, or ``None`` when open-ended.
            non_accruing_days: Days of absences that suspend accrual.

        Returns:
            Qualifying months, from 0 to 12.
        """
        months = _month_days(window, ended_on, non_accruing_days)
        return sum(1 for days, _ in months if self.counts(days))


def _month_days(
    window: AccrualWindow, ended_on: date | None, excluded: frozenset[date]
) -> Iterator[tuple[int, int]]:
    """Yield the accruing days and the length of each month of ``window``.

    Yields:
        ``(accruing days, calendar days of the month)`` for the 12 months.
    """
    last_day = window.end if ended_on is None else min(window.end, ended_on)
    year, month = window.nominal_start.year, window.nominal_start.month
    for _ in range(_MONTHS_PER_WINDOW):
        length = calendar.monthrange(year, month)[1]
        first = max(date(year, month, 1), window.start)
        last = min(date(year, month, length), last_day)
        yield _accruing_days(first, last, excluded), length
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def partial_months(
    window: AccrualWindow,
    *,
    ended_on: date | None = None,
    non_accruing_days: frozenset[date] = frozenset(),
) -> int:
    """Return the months of ``window`` accrued for part of their days.

    Only these months depend on the threshold of a :class:`MonthAccrualRule`:
    a month with every day accruing counts and one with none does not,
    whatever the rule.

    Returns:
        Months with at least one accruing day and fewer than all of them.
    """
    months = _month_days(window, ended_on, non_accruing_days)
    return sum(1 for days, length in months if 0 < days < length)


def _accruing_days(first: date, last: date, excluded: frozenset[date]) -> int:
    """Return the days from ``first`` to ``last`` not in ``excluded``.

    Returns:
        Day count, zero when ``last`` precedes ``first``.
    """
    if last < first:
        return 0
    span = (last - first).days + 1
    return span - sum(1 for d in excluded if first <= d <= last)


DEFAULT_MONTH_ACCRUAL_RULE = MonthAccrualRule()


@dataclass(frozen=True)
class ExtraMonthAccrual:
    """Rateo of one extra month accrued by an employment.

    Attributes:
        kind: Which extra month accrues.
        window: Accrual window, its start clipped to the hire date.
        months: Qualifying months of the window, 0 to 12.
        max_fraction: Share of a monthly pay the extra month is worth at
            full accrual (``0.5`` for half a quattordicesima).
        ended_on: Last day of employment when it ends inside the window,
            otherwise ``None``.
        rule: The month-qualification rule the months were counted with.
        partial_months: Months of the window accrued for part of their
            days, whose counting the threshold of ``rule`` decided.

    Raises:
        ValueError: When ``months`` is outside ``[0, 12]`` or
            ``max_fraction`` outside ``(0, 1]``.
    """

    kind: ExtraMonthKind
    window: AccrualWindow
    months: int
    max_fraction: Decimal = field(default_factory=lambda: Decimal(1))
    ended_on: date | None = None
    rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE
    partial_months: int = 0

    def __post_init__(self) -> None:  # noqa: D105
        if not 0 <= self.months <= _MONTHS_PER_WINDOW:
            msg = f"accrued months must be 0-12; got {self.months}"
            raise ValueError(msg)
        if not Decimal(0) < self.max_fraction <= Decimal(1):
            msg = f"max_fraction must be in (0, 1]; got {self.max_fraction}"
            raise ValueError(msg)

    @property
    def fraction(self) -> Decimal:
        """Share of a monthly pay due: ``months / 12 * max_fraction``."""
        return Decimal(self.months) / _MONTHS_PER_WINDOW * self.max_fraction

    @classmethod
    def of(
        cls,
        schedule: ExtraMonthSchedule,
        payment_year: int,
        employment: EmploymentPeriod | None = None,
        *,
        non_accruing_days: frozenset[date] = frozenset(),
        rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
    ) -> ExtraMonthAccrual:
        """Count the rateo of ``schedule`` paid in ``payment_year``.

        Args:
            schedule: The extra month and its window.
            payment_year: Year in which the extra month is (or would be) paid.
            employment: Employment period, or ``None`` for a worker employed
                over the whole window.
            non_accruing_days: Days of absences that suspend accrual.
            rule: Month-qualification rule.

        Returns:
            The accrual, with the window clipped to the hire date and
            counted up to the termination date.
        """
        started_on = employment.started_on if employment is not None else None
        ended_on = employment.ended_on if employment is not None else None
        window = schedule.accrual_window(payment_year, started_on)
        if ended_on is not None and ended_on >= window.end:
            ended_on = None
        return cls(
            kind=schedule.kind,
            window=window,
            months=rule.qualifying_months(
                window, ended_on=ended_on, non_accruing_days=non_accruing_days
            ),
            max_fraction=schedule.max_fraction,
            ended_on=ended_on,
            rule=rule,
            partial_months=partial_months(
                window, ended_on=ended_on, non_accruing_days=non_accruing_days
            ),
        )


def absence_days(first: date, last: date) -> frozenset[date]:
    """Return every calendar day from ``first`` to ``last`` inclusive.

    Returns:
        The days of the range, empty when ``last`` precedes ``first``.
    """
    span = (last - first).days + 1
    return frozenset(first + timedelta(days=i) for i in range(max(0, span)))
