"""Sickness of an operaio agricolo a tempo determinato, its elenchi days stated.

INPS, Guida alla tutela previdenziale della malattia (September 2024, p.
4): with 51 days in the elenchi of the year before, as many days as those
of registration, at most 180 in the calendar year; with 51 days of the
current year instead, at most 30; INPS pays them directly.

INPS rules of the tests: waiting period of three days, 50% from day 4, 180
days a year.  Every count is read off the calendar by hand.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.sickness.agricultural.inputs import AgriculturalDays
from ccnl_engine.sickness.cumulation.rules import SicknessWorker
from ccnl_engine.sickness.day.models import SickPayRules
from ccnl_engine.sickness.day.rules import SickDayKind, classify_days
from ccnl_engine.sickness.indemnity.models import (
    FixedTermSickLimit,
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)
from ccnl_engine.sickness.integration.models import SicknessRules
from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory

_C, _I, _L = (
    SickDayKind.CARENZA,
    SickDayKind.INDEMNIFIED,
    SickDayKind.FIXED_TERM_LIMIT,
)
_RULES = SickPayRules(
    inps=InpsSickPayRates(
        carenza_days=3,
        bands=[SickPayBand(day_from=4, day_to=180, rate=Decimal("0.50"))],
        annual_max_days=180,
        coverage=(SickPayCoverage(covered=True, source="test: every worker"),),
        fixed_term=FixedTermSickLimit(short_work_days=30, paid_directly=True),
    ),
    inps_cover=True,
    ccnl=SicknessRules(
        carenza_integration_rate=Decimal(1), full_pay_integration_rate=Decimal(1)
    ),
    worker=SicknessWorker(hired_on=date(2025, 1, 1)),
    fixed_term=True,
)


def _kinds(
    episode: SicknessEpisode, history: SicknessHistory | None = None
) -> list[tuple[date, date, SickDayKind, bool]]:
    span = (episode.started_on, episode.ended_on)
    return [
        (s.first, s.last, s.kind, s.inps_direct)
        for s in classify_days(episode, span, history or SicknessHistory(), _RULES)
    ]


def _episode(
    first: date, last: date, days: AgriculturalDays | None, name: str = "a"
) -> SicknessEpisode:
    return SicknessEpisode(name, first, last, agricultural_days=days)


def test_the_days_of_the_year_before_are_paid() -> None:
    """60 days in the elenchi of 2025: days 4-63 paid, 4 March to 2 May."""
    episode = _episode(date(2026, 3, 1), date(2026, 5, 15), AgriculturalDays(60, 0))

    assert _kinds(episode) == [
        (date(2026, 3, 1), date(2026, 3, 3), _C, False),
        (date(2026, 3, 4), date(2026, 5, 2), _I, True),
        (date(2026, 5, 3), date(2026, 5, 15), _L, False),
    ]


def test_51_days_of_the_current_year_pay_30() -> None:
    """10 days of 2025, 51 of 2026: 4 March to 2 April paid."""
    episode = _episode(date(2026, 3, 1), date(2026, 4, 10), AgriculturalDays(10, 51))

    assert _kinds(episode) == [
        (date(2026, 3, 1), date(2026, 3, 3), _C, False),
        (date(2026, 3, 4), date(2026, 4, 2), _I, True),
        (date(2026, 4, 3), date(2026, 4, 10), _L, False),
    ]


def test_fewer_than_51_days_pay_nothing() -> None:
    """51 days in neither year: no indemnified day."""
    episode = _episode(date(2026, 3, 1), date(2026, 3, 12), AgriculturalDays(50, 50))

    assert _kinds(episode) == [
        (date(2026, 3, 1), date(2026, 3, 3), _C, False),
        (date(2026, 3, 4), date(2026, 3, 12), _L, False),
    ]


def test_the_days_are_counted_over_the_calendar_year() -> None:
    """60 days: January takes 28 after its carenza, March the other 32."""
    days = AgriculturalDays(60, 0)
    january = _episode(date(2026, 1, 1), date(2026, 1, 31), days, "j")
    march = _episode(date(2026, 3, 1), date(2026, 4, 15), days, "m")

    assert _kinds(march, SicknessHistory((january,))) == [
        (date(2026, 3, 1), date(2026, 3, 3), _C, False),
        (date(2026, 3, 4), date(2026, 4, 4), _I, True),
        (date(2026, 4, 5), date(2026, 4, 15), _L, False),
    ]


def test_without_the_days_the_year_maximum_applies() -> None:
    """Not stated: INPS pays directly, the 180 days of the year alone."""
    episode = _episode(date(2026, 3, 1), date(2026, 3, 12), None)

    assert _kinds(episode) == [
        (date(2026, 3, 1), date(2026, 3, 3), _C, False),
        (date(2026, 3, 4), date(2026, 3, 12), _I, True),
    ]


def test_an_open_ended_operaio_is_not_limited() -> None:
    """The elenchi days of a permanent contract are not read."""
    rules = replace(_RULES, fixed_term=False)
    episode = _episode(date(2026, 3, 1), date(2026, 3, 12), AgriculturalDays(0, 0))
    span = (episode.started_on, episode.ended_on)
    kinds = {s.kind for s in classify_days(episode, span, SicknessHistory(), rules)}

    assert _L not in kinds
