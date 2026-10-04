"""Classification of sick days: waiting period, INPS bands, CCNL tiers.

INPS rules of the tests: waiting period of three days, 50% on days 4-20,
66.66% on days 21-180, at most 180 paid days per calendar year.  Every
expected segment is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.absence import DailyDivisorMethod
from ccnl_engine.contract.domain.sickness import SicknessRules, SicknessTier
from ccnl_engine.payroll.domain.sick_days import (
    SickDayKind,
    SickDaySegment,
    SickPayRules,
    classify_days,
    segment_units,
)
from ccnl_engine.payroll.domain.sickness import SicknessEpisode, SicknessHistory
from ccnl_engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand

_HALF = Decimal("0.50")
_TWO_THIRDS = Decimal("0.6666")
_ONE = Decimal(1)
_ZERO = Decimal(0)
_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[
        SickPayBand(day_from=4, day_to=20, rate=_HALF),
        SickPayBand(day_from=21, day_to=180, rate=_TWO_THIRDS),
    ],
    annual_max_days=180,
)
_FULL = SicknessRules(carenza_integration_rate=_ONE, full_pay_integration_rate=_ONE)


def _rules(ccnl: SicknessRules = _FULL, *, cover: bool | None = True) -> SickPayRules:
    return SickPayRules(inps=_INPS, inps_cover=cover, ccnl=ccnl)


def _shape(
    segments: tuple[SickDaySegment, ...],
) -> list[tuple[date, date, SickDayKind, Decimal, Decimal]]:
    return [(s.first, s.last, s.kind, s.inps_rate, s.worker_rate) for s in segments]


def _episode(
    episode_id: str, first: date, last: date, relapse_of: str | None = None
) -> SicknessEpisode:
    return SicknessEpisode(episode_id, first, last, relapse_of)


def test_days_of_a_later_month_continue_the_episode_index() -> None:
    """From Friday 20 February, 1 March is day 10 and 12 March day 21."""
    episode = _episode("a", date(2026, 2, 20), date(2026, 3, 13))
    segments = classify_days(
        episode, (date(2026, 3, 1), date(2026, 3, 13)), SicknessHistory(), _rules()
    )
    assert _shape(segments) == [
        (date(2026, 3, 1), date(2026, 3, 11), SickDayKind.INDEMNIFIED, _HALF, _ONE),
        (
            date(2026, 3, 12),
            date(2026, 3, 13),
            SickDayKind.INDEMNIFIED,
            _TWO_THIRDS,
            _ONE,
        ),
    ]
    assert [s.first_index for s in segments] == [10, 21]
    assert segments[1].employer_rate == Decimal("0.3334")


def test_first_days_are_the_waiting_period() -> None:
    """Days 1-3 are carenza, integrated at the CCNL carenza rate."""
    rules = SicknessRules(
        carenza_integration_rate=_HALF, full_pay_integration_rate=_ONE
    )
    episode = _episode("a", date(2026, 3, 9), date(2026, 3, 13))
    segments = classify_days(
        episode, (date(2026, 3, 9), date(2026, 3, 13)), SicknessHistory(), _rules(rules)
    )
    assert _shape(segments) == [
        (date(2026, 3, 9), date(2026, 3, 11), SickDayKind.CARENZA, _ZERO, _HALF),
        (date(2026, 3, 12), date(2026, 3, 13), SickDayKind.INDEMNIFIED, _HALF, _ONE),
    ]


def test_a_relapse_has_no_new_waiting_period() -> None:
    """After ten days of the episode it continues, 9 March is day 11."""
    history = SicknessHistory((_episode("a", date(2026, 2, 2), date(2026, 2, 11)),))
    relapse = _episode("b", date(2026, 3, 9), date(2026, 3, 13), relapse_of="a")
    segments = classify_days(
        relapse, (date(2026, 3, 9), date(2026, 3, 13)), history, _rules()
    )
    assert _shape(segments) == [
        (date(2026, 3, 9), date(2026, 3, 13), SickDayKind.INDEMNIFIED, _HALF, _ONE)
    ]
    assert segments[0].first_index == 11


def test_inps_stops_at_its_annual_maximum() -> None:
    """A 180-day episode leaves INPS three days of the year.

    1 January - 29 June 2026 is 180 days, INPS pays days 4-180: 177.  The
    new episode of 10 July has carenza on 10-12 July, INPS on 13-15 July,
    then the employer pays the whole CCNL target.
    """
    history = SicknessHistory((_episode("a", date(2026, 1, 1), date(2026, 6, 29)),))
    episode = _episode("b", date(2026, 7, 10), date(2026, 7, 20))
    segments = classify_days(
        episode, (date(2026, 7, 10), date(2026, 7, 20)), history, _rules()
    )
    assert _shape(segments) == [
        (date(2026, 7, 10), date(2026, 7, 12), SickDayKind.CARENZA, _ZERO, _ONE),
        (date(2026, 7, 13), date(2026, 7, 15), SickDayKind.INDEMNIFIED, _HALF, _ONE),
        (date(2026, 7, 16), date(2026, 7, 20), SickDayKind.INDEMNIFIED, _ZERO, _ONE),
    ]


def test_tier_threshold_within_a_month_splits_the_days() -> None:
    """Month 10 of an episode from 1 January starts on day 271, 28 September."""
    tiered = SicknessRules(
        carenza_integration_rate=_ONE,
        full_pay_integration_rate=_ONE,
        tiers=(
            SicknessTier(month_from=1, month_until=10, integration_rate=_ONE),
            SicknessTier(
                month_from=10, month_until=13, integration_rate=Decimal("0.9")
            ),
            SicknessTier(month_from=13, integration_rate=_HALF),
        ),
        max_duration_days=540,
    )
    episode = _episode("a", date(2026, 1, 1), date(2026, 12, 31))
    segments = classify_days(
        episode,
        (date(2026, 9, 26), date(2026, 9, 30)),
        SicknessHistory(),
        _rules(tiered, cover=False),
    )
    assert _shape(segments) == [
        (date(2026, 9, 26), date(2026, 9, 27), SickDayKind.INDEMNIFIED, _ZERO, _ONE),
        (
            date(2026, 9, 28),
            date(2026, 9, 30),
            SickDayKind.INDEMNIFIED,
            _ZERO,
            Decimal("0.9"),
        ),
    ]


def test_days_past_the_comporto_are_set_apart() -> None:
    """With a 180-day comporto from 1 January, 30 June is day 181."""
    episode = _episode("a", date(2026, 1, 1), date(2026, 7, 31))
    segments = classify_days(
        episode, (date(2026, 6, 28), date(2026, 6, 30)), SicknessHistory(), _rules()
    )
    assert _shape(segments) == [
        (
            date(2026, 6, 28),
            date(2026, 6, 29),
            SickDayKind.INDEMNIFIED,
            _TWO_THIRDS,
            _ONE,
        ),
        (
            date(2026, 6, 30),
            date(2026, 6, 30),
            SickDayKind.BEYOND_COMPORTO,
            _ZERO,
            _ZERO,
        ),
    ]


def test_without_cover_the_ccnl_target_applies() -> None:
    """Unknown cover pays no INPS share; a CCNL without integration pays INPS."""
    episode = _episode("a", date(2026, 3, 9), date(2026, 3, 13))
    span = (date(2026, 3, 12), date(2026, 3, 12))
    unknown = classify_days(episode, span, SicknessHistory(), _rules(cover=None))
    bare = SicknessRules(
        carenza_integration_rate=_ZERO, full_pay_integration_rate=_ZERO
    )
    inps_only = classify_days(episode, span, SicknessHistory(), _rules(bare))
    assert (unknown[0].inps_rate, unknown[0].worker_rate) == (_ZERO, _ONE)
    assert (inps_only[0].inps_rate, inps_only[0].worker_rate) == (_HALF, _HALF)


@pytest.mark.parametrize(
    ("method", "spans", "divisor", "hours", "expected"),
    [
        (
            DailyDivisorMethod.BY_26,
            (
                (date(2026, 1, 1), date(2026, 1, 20)),
                (date(2026, 1, 21), date(2026, 1, 31)),
            ),
            Decimal(26),
            None,
            (Decimal(17), Decimal(9)),
        ),
        (
            DailyDivisorMethod.BY_30,
            ((date(2026, 2, 16), date(2026, 2, 28)),),
            Decimal(30),
            None,
            (Decimal(15),),
        ),
        (
            DailyDivisorMethod.BY_HOURLY,
            ((date(2026, 3, 9), date(2026, 3, 15)),),
            Decimal(173),
            Decimal(8),
            (Decimal(40),),
        ),
    ],
)
def test_units_follow_the_ccnl_divisor(
    method: DailyDivisorMethod,
    spans: tuple[tuple[date, date], ...],
    divisor: Decimal,
    hours: Decimal | None,
    expected: tuple[Decimal, ...],
) -> None:
    """January 2026 has 27 Mondays to Saturdays: the month is capped at 26.

    16-28 February runs to day 30 of the commercial month: 15 days; 9-15
    March is five weekdays of eight hours.
    """
    segments = tuple(
        SickDaySegment(first, last, 1, SickDayKind.INDEMNIFIED, _ZERO, _ONE)
        for first, last in spans
    )
    assert segment_units(segments, method, divisor, hours) == expected


def test_no_segment_has_no_unit() -> None:
    """An empty classification is worth nothing."""
    assert segment_units((), DailyDivisorMethod.BY_26, Decimal(26)) == ()
