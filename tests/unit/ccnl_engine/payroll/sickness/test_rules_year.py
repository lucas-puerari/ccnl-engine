"""Sick pay counted over the calendar year: comporto and carenza by event."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.sickness.models import CarenzaByEvent, SicknessRules
from ccnl_engine.payroll.sickness.models import SicknessEpisode
from ccnl_engine.payroll.sickness.rules_year import YearTreatment

_ONE = Decimal(1)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    max_duration_days=180,
    comporto_calendar_year=True,
    carenza_by_event=CarenzaByEvent(
        from_event=3, rates=(Decimal("0.66"), Decimal("0.50"), Decimal(0))
    ),
)


def _episode(
    name: str,
    start: date,
    days: int,
    *,
    exempt: bool | None = False,
    relapse_of: str | None = None,
) -> SicknessEpisode:
    return SicknessEpisode(
        name,
        start,
        date.fromordinal(start.toordinal() + days - 1),
        relapse_of=relapse_of,
        short_absence_exempt=exempt,
    )


def _year(
    episode: SicknessEpisode,
    *earlier: SicknessEpisode,
    rules: SicknessRules = _RULES,
    known_from: date | None = None,
) -> YearTreatment:
    return YearTreatment(rules, episode, earlier, known_from, lambda _i: _ONE)


def _earlier(count: int, **kwargs: object) -> tuple[SicknessEpisode, ...]:
    return tuple(
        _episode(f"e{n}", date(2026, 1 + n, 5), 2, **kwargs)  # type: ignore[arg-type]
        for n in range(count)
    )


@pytest.mark.parametrize(
    ("before", "rate"),
    [(0, "1"), (1, "1"), (2, "0.66"), (3, "0.50"), (4, "0"), (6, "0")],
)
def test_the_carenza_falls_with_the_events_of_the_year(before: int, rate: str) -> None:
    """Art. 187: 100% for two events, then 66%, 50% and nothing."""
    year = _year(_episode("now", date(2026, 6, 1), 3), *_earlier(before))
    assert year.carenza_rate == Decimal(rate)
    assert not year.exemption_reach


def test_exempt_relapses_and_other_years_are_not_counted() -> None:
    """An exempt event, a relapse and an event of 2025 leave the rank at 1."""
    earlier = (
        _episode("x", date(2026, 1, 5), 2, exempt=True),
        _episode("r", date(2026, 2, 5), 2, relapse_of="x"),
        _episode("old", date(2025, 3, 5), 2),
    )
    year = _year(_episode("now", date(2026, 6, 1), 3), *earlier)
    assert year.carenza_rate == _ONE


def test_an_exempt_or_relapse_episode_keeps_the_full_carenza() -> None:
    """Its own exemption or relapse makes the episode's carenza unreduced."""
    exempt = _year(_episode("now", date(2026, 6, 1), 3, exempt=True), *_earlier(4))
    relapse = _year(_episode("now", date(2026, 6, 1), 3, relapse_of="e3"), *_earlier(4))
    assert exempt.carenza_rate == relapse.carenza_rate == _ONE
    assert not exempt.exemption_reach
    assert not relapse.exemption_reach


@pytest.mark.parametrize(
    ("own", "earlier_exempt"),
    [(None, False), (False, None)],
    ids=["own-unknown", "earlier-unknown"],
)
def test_an_unstated_exemption_pays_the_higher_carenza(
    own: bool | None, earlier_exempt: bool | None
) -> None:
    """The rank is unsure: the higher carenza is paid and the fact named."""
    year = _year(
        _episode("now", date(2026, 6, 1), 3, exempt=own),
        *_earlier(2, exempt=earlier_exempt),
    )
    assert year.exemption_reach
    assert year.carenza_rate == (_ONE if earlier_exempt is None else Decimal("0.66"))


def test_the_comporto_sums_the_sick_days_of_the_year() -> None:
    """180 days in the calendar year: 150 earlier days leave 30 to the episode."""
    earlier = _episode("long", date(2026, 1, 1), 150)
    year = _year(_episode("now", date(2026, 7, 1), 40), earlier)
    assert not year.day(30, date(2026, 7, 30)).beyond_comporto
    assert year.day(31, date(2026, 7, 31)).beyond_comporto
    assert year.year_days(date(2026, 7, 31)) == 181


def test_a_per_episode_comporto_reads_the_index() -> None:
    """Without the calendar-year count the index of the episode decides."""
    rules = _RULES.model_copy(update={"comporto_calendar_year": False})
    earlier = _episode("long", date(2026, 1, 1), 150)
    year = _year(_episode("now", date(2026, 7, 1), 40), earlier, rules=rules)
    assert not year.day(40, date(2026, 8, 9)).beyond_comporto


def test_a_history_known_after_new_year_could_change_the_count() -> None:
    """Days before the known history may hold events or sick days of the year."""
    episode = _episode("now", date(2026, 6, 1), 3)
    assert _year(episode, known_from=date(2026, 3, 1)).history_reach
    assert not _year(episode, known_from=date(2026, 1, 1)).history_reach
    assert not _year(episode).history_reach


def test_without_events_the_carenza_is_the_rule_rate() -> None:
    """A calendar-year comporto alone leaves the carenza at its rate."""
    rules = _RULES.model_copy(update={"carenza_by_event": None})
    year = _year(_episode("now", date(2026, 6, 1), 3), *_earlier(4), rules=rules)
    assert year.carenza_rate == _ONE
    assert not year.exemption_reach
