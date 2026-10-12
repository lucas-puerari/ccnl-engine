"""Extra-month accrual: the qualifying months of a window and the rateo they give.

A tredicesima or quattordicesima accrues one twelfth (rateo) for each month
of its 12-month
:class:`~ccnl_engine.extra_month.schedule.models.AccrualWindow`
that qualifies for the employment.  The months are counted from dates, never
from the number of payroll runs already closed:

- the window starts at the hire date when the worker was hired inside it;
- it stops at the termination date when the employment ends inside it;
- days of an absence that suspends accrual are not accruing days;
- a calendar month qualifies when its accruing days compare with
  :attr:`MonthAccrualRule.min_days` as :attr:`MonthAccrualRule.comparison`
  says: the CCNL clause when the bundle has one, otherwise the engine
  default (at least 15 days);
- under a day-based comparison the days themselves accrue
  (:attr:`ExtraMonthAccrual.day_units`): a month accruing every day
  qualifies and each other month adds its working days from Monday to
  Saturday in twenty-sixths (``working_days_26``) or its days as 365ths
  (``days_365``) or 360ths (``days_360``) of the year; under
  ``service_days_365`` no month qualifies and every accruing day adds a
  365th of the year.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.models import AccrualComparison

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.employment.fact.inputs import EmploymentPeriod
    from ccnl_engine.extra_month.schedule.models import (
        AccrualWindow,
        ExtraMonthKind,
        ExtraMonthSchedule,
    )
    from ccnl_engine.provenance.source.rule.models import RuleProvenance

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
_WORKING_DAYS = Decimal(26)
_MONTH_DAYS_360 = Decimal(30)
_YEAR_DAYS = Decimal(365)
_SUNDAY = 6
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
        min_days: Threshold in accruing calendar days; ignored by a
            day-based comparison.
        comparison: ``at_least`` counts a month whose days reach
            ``min_days``; ``more_than`` one whose days exceed it; a
            day-based comparison only a month accruing every day (none for
            ``service_days_365``), the other days accruing as
            :meth:`day_units`.
        source: Where the rule comes from, in words.
        rule: Identifier of the rule: ``<ruleset>:parameters.accrual_rule``
            for a CCNL rule, :data:`DEFAULT_ACCRUAL_RULE_ID` for the default.
        provenance: Provenance of the rule, ``None`` when the caller built
            it or it is the bare engine default.

    Raises:
        ValueError: When a full 28-day month would not count or the
            threshold is below one day.
    """

    min_days: int | None = _DEFAULT_MIN_DAYS
    source: str = _DEFAULT_SOURCE
    comparison: AccrualComparison = AccrualComparison.AT_LEAST
    rule: str = DEFAULT_ACCRUAL_RULE_ID
    provenance: RuleProvenance | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.by_working_days:
            return
        more_than = self.comparison is AccrualComparison.MORE_THAN
        lowest, highest = (0, 27) if more_than else (1, _SHORTEST_MONTH_DAYS)
        if self.min_days is None or not lowest <= self.min_days <= highest:
            msg = (
                f"min_days must be between {lowest} and {highest} for "
                f"{self.comparison.value!r}; got {self.min_days}"
            )
            raise ValueError(msg)

    @property
    def by_working_days(self) -> bool:
        """Whether the days accrue instead of a threshold deciding."""
        return self.comparison.by_days

    def counts(self, days: int, length: int = 31) -> bool:
        """Return whether a month with ``days`` accruing days counts.

        Args:
            days: Accruing days of the month.
            length: Calendar days of the month.

        Returns:
            ``days >= min_days`` for ``at_least``, ``days > min_days`` for
            ``more_than``, every day of the month for a day-based rule,
            never for ``service_days_365``.
        """
        if self.comparison is AccrualComparison.SERVICE_DAYS_365:
            return False
        if self.by_working_days or self.min_days is None:
            return days == length
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
        return sum(1 for days, length in months if self.counts(days, length))

    def day_units(
        self,
        window: AccrualWindow,
        *,
        ended_on: date | None = None,
        non_accruing_days: frozenset[date] = frozenset(),
    ) -> Decimal:
        """Return the months the days of ``window`` accrue, beyond whole months.

        Returns:
            Zero for a threshold rule; for a day-based rule the sum over
            the months of their share (:meth:`_month_units`), at most 12.
        """
        if not self.by_working_days:
            return Decimal(0)
        total = Decimal(0)
        for first, last, length in _month_spans(window, ended_on):
            total += self._month_units(first, last, length, non_accruing_days)
        return min(total, Decimal(_MONTHS_PER_WINDOW))

    def _month_units(
        self, first: date, last: date, length: int, excluded: frozenset[date]
    ) -> Decimal:
        """Return the share of a rateo one month's days accrue.

        Returns:
            ``days x 12 / 365`` for every month under ``service_days_365``;
            for a month accruing part of its days, its working days over
            26 (at most one), ``days x 12 / 365`` or ``days / 30`` (at
            most one); zero otherwise.
        """
        days = _accruing_days(first, last, excluded)
        mode = self.comparison
        if mode is AccrualComparison.SERVICE_DAYS_365:
            return days * Decimal(_MONTHS_PER_WINDOW) / _YEAR_DAYS
        if not 0 < days < length:
            return Decimal(0)
        if mode is AccrualComparison.WORKING_DAYS_26:
            worked = _working_days(first, last, excluded)
            return min(Decimal(worked) / _WORKING_DAYS, Decimal(1))
        if mode is AccrualComparison.DAYS_365:
            return days * Decimal(_MONTHS_PER_WINDOW) / _YEAR_DAYS
        return min(days / _MONTH_DAYS_360, Decimal(1))


def _month_spans(
    window: AccrualWindow, ended_on: date | None
) -> Iterator[tuple[date, date, int]]:
    """Yield the employed span and the length of each month of ``window``.

    Yields:
        ``(first day, last day, calendar days of the month)`` for the 12
        months; the last day precedes the first for a month not employed.
    """
    last_day = window.end if ended_on is None else min(window.end, ended_on)
    year, month = window.nominal_start.year, window.nominal_start.month
    for _ in range(_MONTHS_PER_WINDOW):
        length = calendar.monthrange(year, month)[1]
        first = max(date(year, month, 1), window.start)
        last = min(date(year, month, length), last_day)
        yield first, last, length
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def _month_days(
    window: AccrualWindow, ended_on: date | None, excluded: frozenset[date]
) -> Iterator[tuple[int, int]]:
    """Yield the accruing days and the length of each month of ``window``.

    Yields:
        ``(accruing days, calendar days of the month)`` for the 12 months.
    """
    for first, last, length in _month_spans(window, ended_on):
        yield _accruing_days(first, last, excluded), length


def _working_days(first: date, last: date, excluded: frozenset[date]) -> int:
    """Return the days from Monday to Saturday from ``first`` to ``last``.

    Returns:
        The days not in ``excluded`` and not a Sunday; zero when ``last``
        precedes ``first``.
    """
    span = max(0, (last - first).days + 1)
    days = (first + timedelta(days=i) for i in range(span))
    return sum(1 for d in days if d.weekday() != _SUNDAY and d not in excluded)


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
        day_units: Months accrued by days under a day-based rule, beyond
            the whole months; zero for a threshold rule.
        max_fraction: Share of a monthly pay the extra month is worth at
            full accrual (``0.5`` for half a quattordicesima).
        ended_on: Last day of employment when it ends inside the window,
            otherwise ``None``.
        rule: The month-qualification rule the months were counted with.
        partial_months: Months of the window accrued for part of their
            days, whose counting the threshold of ``rule`` decided.
        undetermined: Whether absences that may suspend accrual, their
            suspension not stated, change ``months``: ``months`` counts
            them as accruing.

    Raises:
        ValueError: When ``months`` is outside ``[0, 12]`` or
            ``max_fraction`` outside ``(0, 1]``.
    """

    kind: ExtraMonthKind
    window: AccrualWindow
    months: int
    day_units: Decimal = field(default_factory=Decimal)
    max_fraction: Decimal = field(default_factory=lambda: Decimal(1))
    ended_on: date | None = None
    rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE
    partial_months: int = 0
    undetermined: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        if not 0 <= self.months <= self.accrued <= _MONTHS_PER_WINDOW:
            msg = f"accrued months must be 0-12; got {self.months} + {self.day_units}"
            raise ValueError(msg)
        if not Decimal(0) < self.max_fraction <= Decimal(1):
            msg = f"max_fraction must be in (0, 1]; got {self.max_fraction}"
            raise ValueError(msg)

    @property
    def accrued(self) -> Decimal:
        """Months accrued: qualifying months plus the day units."""
        return self.months + self.day_units

    @property
    def fraction(self) -> Decimal:
        """Share of a monthly pay due: ``accrued / 12 * max_fraction``."""
        return self.accrued / _MONTHS_PER_WINDOW * self.max_fraction

    @classmethod
    def of(
        cls,
        schedule: ExtraMonthSchedule,
        payment_year: int,
        employment: EmploymentPeriod | None = None,
        *,
        non_accruing_days: frozenset[date] = frozenset(),
        rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
        unknown_days: frozenset[date] = frozenset(),
    ) -> ExtraMonthAccrual:
        """Count the rateo of ``schedule`` paid in ``payment_year``.

        Args:
            schedule: The extra month and its window.
            payment_year: Year in which the extra month is (or would be) paid.
            employment: Employment period, or ``None`` for a worker employed
                over the whole window.
            non_accruing_days: Days of absences that suspend accrual.
            rule: Month-qualification rule.
            unknown_days: Days of absences whose suspension of accrual is
                not stated, counted as accruing.

        Returns:
            The accrual, with the window clipped to the hire date and
            counted up to the termination date.
        """
        started_on = employment.started_on if employment is not None else None
        ended_on = employment.ended_on if employment is not None else None
        window = schedule.accrual_window(payment_year, started_on)
        if ended_on is not None and ended_on >= window.end:
            ended_on = None
        months = rule.qualifying_months(
            window, ended_on=ended_on, non_accruing_days=non_accruing_days
        )
        units = rule.day_units(
            window, ended_on=ended_on, non_accruing_days=non_accruing_days
        )
        suspended = non_accruing_days | unknown_days
        suspended_months = rule.qualifying_months(
            window, ended_on=ended_on, non_accruing_days=suspended
        )
        suspended_units = rule.day_units(
            window, ended_on=ended_on, non_accruing_days=suspended
        )
        return cls(
            kind=schedule.kind,
            window=window,
            months=months,
            day_units=units,
            max_fraction=schedule.max_fraction,
            ended_on=ended_on,
            rule=rule,
            partial_months=partial_months(
                window, ended_on=ended_on, non_accruing_days=non_accruing_days
            ),
            undetermined=(suspended_months, suspended_units) != (months, units),
        )


def absence_days(first: date, last: date) -> frozenset[date]:
    """Return every calendar day from ``first`` to ``last`` inclusive.

    Returns:
        The days of the range, empty when ``last`` precedes ``first``.
    """
    span = (last - first).days + 1
    return frozenset(first + timedelta(days=i) for i in range(max(0, span)))
