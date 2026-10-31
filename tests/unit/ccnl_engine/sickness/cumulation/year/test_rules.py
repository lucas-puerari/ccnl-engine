"""Sick pay counted over the calendar year: comporto and carenza by event."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.comporto.models import ComportoBand, ComportoWindow
from ccnl_engine.sickness.cumulation.rules import SicknessWorker
from ccnl_engine.sickness.cumulation.year.rules import YearTreatment
from ccnl_engine.sickness.integration.models import CarenzaByEvent, SicknessRules
from ccnl_engine.sickness.models import SicknessEpisode

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
    seniority: SeniorityFact | None = None,
    offset: int = 0,
) -> YearTreatment:
    worker = SicknessWorker(seniority=seniority, known_from=known_from)
    return YearTreatment(rules, episode, earlier, worker, lambda _i: _ONE, offset)


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


_ANCE = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    max_duration_days=365,
    comporto_windows=(
        ComportoWindow(seniority_months_from=0, window_months=20, comporto_days=270),
        ComportoWindow(seniority_months_from=42, window_months=24, comporto_days=365),
    ),
)


@pytest.mark.parametrize(
    ("hired", "earlier_start", "last_kept", "first_past"),
    [
        # Three years: 270 days in the 20 months to the day.  The 200 days
        # from 1 Feb 2025 fall in the window of 1 Jun 2026 (from 2 Oct
        # 2024): 70 days more, to 9 Aug, are kept, 10 Aug is past them.
        (date(2023, 6, 1), date(2025, 2, 1), date(2026, 8, 9), date(2026, 8, 10)),
        # Earlier days that left the 20 months no longer count: from
        # 1 Feb 2024 (to 18 Aug 2024) none lie in the window of 1 Jun 2026,
        # and 270 days of the episode run to 25 Feb 2027.
        (date(2023, 6, 1), date(2024, 2, 1), date(2027, 2, 25), date(2027, 2, 26)),
        # Five years: 365 days in the 24 months.  The 200 days from
        # 1 Feb 2025 (to 19 Aug 2025) are in the window: 165 days more,
        # to 12 Nov 2026, are kept.
        (date(2021, 6, 1), date(2025, 2, 1), date(2026, 11, 12), date(2026, 11, 13)),
    ],
    ids=["window-of-20-months", "days-out-of-the-window", "window-of-24-months"],
)
def test_the_window_comporto_sums_the_sick_days_of_its_months(
    hired: date, earlier_start: date, last_kept: date, first_past: date
) -> None:
    """Edilizia ANCE Art. 26: nine months in 20, twelve in 24 past 3.5 years."""
    seniority = SeniorityFact.since(hired, SenioritySource.PAYSLIP)
    earlier = _episode("before", earlier_start, 200)
    year = _year(
        _episode("now", date(2026, 6, 1), 400),
        earlier,
        rules=_ANCE,
        seniority=seniority,
    )
    index = (last_kept - date(2026, 6, 1)).days + 1
    assert not year.day(index, last_kept).beyond_comporto
    assert year.day(index + 1, first_past).beyond_comporto


def test_the_illness_limit_holds_under_a_longer_window() -> None:
    """Metalmeccanico artigianato Art. 61: 9 months for one illness, 10 in 24."""
    rules = _ANCE.model_copy(
        update={
            "max_duration_days": 270,
            "comporto_windows": (
                ComportoWindow(
                    seniority_months_from=0, window_months=24, comporto_days=300
                ),
            ),
        }
    )
    year = _year(_episode("now", date(2026, 6, 1), 300), rules=rules)
    assert not year.day(270, date(2027, 2, 25)).beyond_comporto
    assert year.day(271, date(2027, 2, 26)).beyond_comporto


def test_a_history_known_within_the_window_could_change_the_count() -> None:
    """The 20 months before 1 Jun 2026 start on 2 Oct 2024."""
    episode = _episode("now", date(2026, 6, 1), 3)
    assert _year(episode, rules=_ANCE, known_from=date(2024, 10, 3)).history_reach
    assert not _year(episode, rules=_ANCE, known_from=date(2024, 10, 2)).history_reach


def test_windows_must_start_at_no_seniority_and_increase() -> None:
    """A first window from 12 months is refused."""
    window = ComportoWindow(
        seniority_months_from=12, window_months=20, comporto_days=270
    )
    with pytest.raises(ValidationError, match="comporto windows must start at 0"):
        SicknessRules(
            carenza_integration_rate=_ONE,
            full_pay_integration_rate=_ONE,
            comporto_windows=(window,),
        )


_ABI = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    comporto_bands=(
        ComportoBand(seniority_months_from=0, comporto_days=180),
        ComportoBand(seniority_months_from=61, comporto_days=240),
        ComportoBand(seniority_months_from=301, comporto_days=660),
    ),
)


@pytest.mark.parametrize(
    ("hired", "offset", "last_kept", "reach"),
    [
        # Three years, 6 months of 30 days: days 1-180, to 28 Nov 2026.
        (date(2023, 6, 1), 0, 180, False),
        # A relapse after 100 days of the illness it continues: 80 more.
        (date(2023, 6, 1), 100, 80, False),
        # Over 25 years (301 months): 22 months, 660 days.
        (date(2000, 1, 1), 0, 660, False),
        # Unknown seniority: the first band, and a later one could keep
        # the 700 days of the episode longer.
        (None, 0, 180, True),
    ],
    ids=["first-band", "relapse", "last-band", "unknown-seniority"],
)
def test_the_comporto_of_one_illness_follows_the_seniority(
    hired: date | None, offset: int, last_kept: int, reach: bool
) -> None:
    """ABI Art. 66 c. 1: 6 to 22 months of one illness by seniority."""
    start = date(2026, 6, 1)
    seniority = (
        None if hired is None else SeniorityFact.since(hired, SenioritySource.PAYSLIP)
    )
    year = _year(
        _episode("now", start, 700),
        rules=_ABI,
        seniority=seniority,
        offset=offset,
        known_from=date(2026, 5, 1),
    )
    kept = date.fromordinal(start.toordinal() + last_kept - 1)
    after = date.fromordinal(kept.toordinal() + 1)
    assert not year.day(offset + last_kept, kept).beyond_comporto
    assert year.day(offset + last_kept + 1, after).beyond_comporto
    assert year.seniority_reach is reach
    assert not year.history_reach
