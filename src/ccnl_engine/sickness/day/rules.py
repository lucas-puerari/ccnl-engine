"""Classify the sick days of a month: waiting period, INPS bands, CCNL tiers.

Every calendar day of an episode has an index: its day in the episode,
counted on from the episode it continues for a relapse.  The index
decides, for that day:

- the waiting period (*carenza*): the first ``carenza_days`` days, which
  INPS does not pay and the CCNL integrates at its ``carenza`` rate;
- the INPS band and rate, while INPS covers the worker and has paid fewer
  than its annual maximum of days in the calendar year of the day;
- the CCNL treatment: the integration rate of the day and whether it is
  past the comporto, from the index or from the sickness of several
  episodes (:mod:`~ccnl_engine.sickness.day.models`);
- for a fixed-term contract (D.L. 463/1983 art. 5), whether the day is
  within the days of work of the 12 months before the episode (c. 1), or
  within 30 days in the calendar year when they were 30 or fewer (c. 3),
  and whether INPS pays its share directly: always in the second case,
  beyond the days with this employer in the first (c. 5).

The worker receives the higher of the CCNL target rate and the INPS rate;
the employer pays what INPS does not.  Consecutive days with the same
treatment form a :class:`SickDaySegment`; how many of its days are payable
is the CCNL daily-divisor count (:func:`segment_units`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.compensation.proration.rules import payable_days
from ccnl_engine.sickness.cumulation.rules import window_start

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.absence.models import DailyDivisorMethod
    from ccnl_engine.sickness.cumulation.rules import CcnlDay
    from ccnl_engine.sickness.day.models import DayTreatment, SickPayRules
    from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory

__all__ = [
    "SickDayKind",
    "SickDaySegment",
    "classify_days",
    "segment_units",
]

_ZERO = Decimal(0)


class SickDayKind(StrEnum):
    """Treatment of a sick day.

    Attributes:
        CARENZA: Waiting period: no INPS indemnity.
        INDEMNIFIED: After the waiting period, within the comporto.
        BEYOND_COMPORTO: Past the days the CCNL integrates.
        FIXED_TERM_LIMIT: Past the days a fixed-term contract pays (D.L.
            463/1983 art. 5): unpaid.
    """

    CARENZA = "carenza"
    INDEMNIFIED = "indemnified"
    BEYOND_COMPORTO = "beyond_comporto"
    FIXED_TERM_LIMIT = "fixed_term_limit"


@dataclass(frozen=True)
class SickDaySegment:
    """Consecutive sick days of a month with the same treatment.

    Attributes:
        first: First day of the segment.
        last: Last day of the segment.
        first_index: Episode day index of :attr:`first`.
        kind: Treatment of the days.
        inps_rate: Share of the daily pay INPS pays.
        worker_rate: Share of the daily pay the worker receives.
        inps_direct: Whether INPS pays its share to the worker directly,
            so the employer does not advance it.
    """

    first: date
    last: date
    first_index: int
    kind: SickDayKind
    inps_rate: Decimal
    worker_rate: Decimal
    inps_direct: bool = False

    @property
    def employer_rate(self) -> Decimal:
        """Share of the daily pay the employer pays on top of INPS."""
        return self.worker_rate - self.inps_rate


@dataclass(frozen=True)
class _Day:
    """Treatment of one sick day."""

    kind: SickDayKind
    inps_rate: Decimal
    worker_rate: Decimal
    inps_direct: bool = False


@dataclass
class _InpsDays:
    """Days paid per calendar year, counted as days are walked.

    ``used`` counts the INPS days, ``short_term`` the days a fixed-term
    worker with 30 days of work or fewer is paid (D.L. 463/1983 art. 5
    c. 3).
    """

    used: dict[int, int] = field(default_factory=dict)
    short_term: dict[int, int] = field(default_factory=dict)

    def take(self, day: date, limit: int) -> bool:
        """Count ``day`` as paid when the year has room left.

        Returns:
            Whether INPS pays ``day``.
        """
        return _take(self.used, day, limit)


def _take(used: dict[int, int], day: date, limit: int) -> bool:
    count = used.get(day.year, 0)
    if count >= limit:
        return False
    used[day.year] = count + 1
    return True


@dataclass(frozen=True)
class _FixedTermLimit:
    """Days of an episode a fixed-term contract pays (D.L. 463/1983 art. 5).

    Attributes:
        days: Days of the episode paid at most (c. 1); ``None`` under the
            days of the calendar year of c. 3.
        direct_after: Episode day after which INPS pays its share directly
            (c. 3 and c. 5); ``None`` when the employer advances every day.
        short_days: Days of the calendar year of c. 3.
    """

    days: int | None
    direct_after: int | None
    short_days: int

    def allows(self, index: int, day: date, inps: _InpsDays) -> bool:
        if self.days is not None:
            return index <= self.days
        return _take(inps.short_term, day, self.short_days)


def _fixed_term_limit(
    episode: SicknessEpisode, rules: SickPayRules
) -> _FixedTermLimit | None:
    """Return the limit of a fixed-term episode, ``None`` without one.

    The days with this employer are the calendar days of the employment in
    the 12 months before the episode.

    Returns:
        The limit; ``None`` for an open-ended contract or when the days of
        work are not stated.
    """
    worked = episode.prior_worked_days
    statute = rules.inps.fixed_term
    if not rules.fixed_term or worked is None or statute is None:
        return None
    short = statute.short_work_days
    if worked <= short:
        return _FixedTermLimit(None, 0, short)
    hired = rules.worker.hired_on
    start = episode.started_on
    if hired is None:
        return _FixedTermLimit(worked, None, short)
    year_before = window_start(start - timedelta(days=1), 1)
    employed = (start - max(hired, year_before)).days
    return _FixedTermLimit(worked, max(employed, 0), short)


def _classify(
    index: int,
    day: date,
    rules: SickPayRules,
    inps: _InpsDays,
    days: tuple[CcnlDay, _FixedTermLimit | None],
) -> _Day:
    """Return the treatment of the sick day ``day`` of episode index ``index``.

    Returns:
        The kind, INPS rate and worker rate of the day.
    """
    ccnl, limit = days
    if ccnl.beyond_comporto:
        return _Day(SickDayKind.BEYOND_COMPORTO, _ZERO, _ZERO)
    if limit is not None and not limit.allows(index, day, inps):
        return _Day(SickDayKind.FIXED_TERM_LIMIT, _ZERO, _ZERO)
    if index <= rules.inps.carenza_days:
        return _Day(SickDayKind.CARENZA, _ZERO, ccnl.carenza_rate)
    band = rules.inps.band_rate(index) if rules.inps_cover else _ZERO
    paid = band > _ZERO and inps.take(day, rules.inps.annual_max_days)
    rate = band if paid else _ZERO
    direct = (
        paid
        and limit is not None
        and limit.direct_after is not None
        and index > limit.direct_after
    )
    return _Day(SickDayKind.INDEMNIFIED, rate, max(ccnl.rate, rate), direct)


def _walk(
    episode: SicknessEpisode,
    span: tuple[date, date],
    history: SicknessHistory,
    rules: SickPayRules,
    inps: _InpsDays,
) -> Iterator[tuple[date, int, _Day]]:
    """Yield each day of ``span`` with its index and treatment.

    Yields:
        ``(day, index, treatment)`` in day order.
    """
    offset = history.offset(episode)
    ccnl: DayTreatment = rules.treatment(episode, history)
    limit = _fixed_term_limit(episode, rules)
    first, last = span
    for step in range((last - first).days + 1):
        day = first + timedelta(days=step)
        index = offset + (day - episode.started_on).days + 1
        yield day, index, _classify(index, day, rules, inps, (ccnl(index, day), limit))


def _used_before(
    episode: SicknessEpisode,
    first: date,
    history: SicknessHistory,
    rules: SickPayRules,
) -> _InpsDays:
    """Return the INPS days paid before ``first``, walking every earlier day.

    Returns:
        The days paid per calendar year by the earlier episodes and by the
        days of ``episode`` before ``first``.
    """
    inps = _InpsDays()
    for earlier in history.earlier(episode):
        span = (earlier.started_on, earlier.ended_on)
        for _ in _walk(earlier, span, history, rules, inps):
            pass
    head = episode.before(first)
    if head is not None:
        span = (head.started_on, head.ended_on)
        for _ in _walk(episode, span, history, rules, inps):
            pass
    return inps


def classify_days(
    episode: SicknessEpisode,
    span: tuple[date, date],
    history: SicknessHistory,
    rules: SickPayRules,
) -> tuple[SickDaySegment, ...]:
    """Return the sick days of ``span`` grouped by treatment.

    Args:
        episode: The episode; ``span`` lies within it.
        span: First and last sick day the run pays.
        history: Episodes recorded by earlier runs.
        rules: INPS and CCNL rules.

    Returns:
        The segments in day order.
    """
    history.check(episode, span[0])
    inps = _used_before(episode, span[0], history, rules)
    segments: list[SickDaySegment] = []
    for day, index, treatment in _walk(episode, span, history, rules, inps):
        last = segments[-1] if segments else None
        if (
            last is not None
            and last.kind is treatment.kind
            and last.inps_rate == treatment.inps_rate
            and last.worker_rate == treatment.worker_rate
            and last.inps_direct == treatment.inps_direct
        ):
            segments[-1] = SickDaySegment(
                last.first,
                day,
                last.first_index,
                last.kind,
                last.inps_rate,
                last.worker_rate,
                last.inps_direct,
            )
            continue
        segments.append(
            SickDaySegment(
                day,
                day,
                index,
                treatment.kind,
                treatment.inps_rate,
                treatment.worker_rate,
                treatment.inps_direct,
            )
        )
    return tuple(segments)


def segment_units(
    segments: tuple[SickDaySegment, ...],
    method: DailyDivisorMethod,
    divisor: Decimal,
    daily_hours: Decimal | None = None,
) -> tuple[Decimal, ...]:
    """Return the payable units of each segment under the CCNL divisor.

    Days are counted as the CCNL counts a partial month
    (:func:`~ccnl_engine.compensation.proration.rules.payable_days`), from the
    first sick day; hours for ``by_hourly``.  The running total never
    exceeds ``divisor``: a month of sickness is worth one monthly pay.

    Returns:
        One unit count per segment, in segment order.
    """
    if not segments:
        return ()
    start = segments[0].first
    per_day = daily_hours or Decimal(1)

    def cumulative(last: date) -> Decimal:
        if last < start:
            return _ZERO
        return min(Decimal(payable_days(method, start, last)) * per_day, divisor)

    return tuple(
        cumulative(s.last) - cumulative(s.first - timedelta(days=1)) for s in segments
    )
