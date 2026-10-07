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
  episodes (:mod:`~ccnl_engine.payroll.domain.sick_pay_rules`).

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

from ccnl_engine.payroll.domain.proration import payable_days

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.contract.domain.absence import DailyDivisorMethod
    from ccnl_engine.payroll.domain.sick_cumulation import CcnlDay
    from ccnl_engine.payroll.domain.sick_pay_rules import DayTreatment, SickPayRules
    from ccnl_engine.payroll.domain.sickness import SicknessEpisode, SicknessHistory

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
    """

    CARENZA = "carenza"
    INDEMNIFIED = "indemnified"
    BEYOND_COMPORTO = "beyond_comporto"


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
    """

    first: date
    last: date
    first_index: int
    kind: SickDayKind
    inps_rate: Decimal
    worker_rate: Decimal

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


@dataclass
class _InpsDays:
    """INPS days paid per calendar year, counted as days are walked."""

    used: dict[int, int] = field(default_factory=dict)

    def take(self, day: date, limit: int) -> bool:
        """Count ``day`` as paid when the year has room left.

        Returns:
            Whether INPS pays ``day``.
        """
        count = self.used.get(day.year, 0)
        if count >= limit:
            return False
        self.used[day.year] = count + 1
        return True


def _classify(
    index: int, day: date, rules: SickPayRules, inps: _InpsDays, ccnl: CcnlDay
) -> _Day:
    """Return the treatment of the sick day ``day`` of episode index ``index``.

    Returns:
        The kind, INPS rate and worker rate of the day.
    """
    if ccnl.beyond_comporto:
        return _Day(SickDayKind.BEYOND_COMPORTO, _ZERO, _ZERO)
    if index <= rules.inps.carenza_days:
        return _Day(SickDayKind.CARENZA, _ZERO, ccnl.carenza_rate)
    band = rules.inps.band_rate(index) if rules.inps_cover else _ZERO
    paid = band > _ZERO and inps.take(day, rules.inps.annual_max_days)
    rate = band if paid else _ZERO
    return _Day(SickDayKind.INDEMNIFIED, rate, max(ccnl.rate, rate))


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
    first, last = span
    for step in range((last - first).days + 1):
        day = first + timedelta(days=step)
        index = offset + (day - episode.started_on).days + 1
        yield day, index, _classify(index, day, rules, inps, ccnl(index, day))


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
        ):
            segments[-1] = SickDaySegment(
                last.first,
                day,
                last.first_index,
                last.kind,
                last.inps_rate,
                last.worker_rate,
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
    (:func:`~ccnl_engine.payroll.domain.proration.payable_days`), from the
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
