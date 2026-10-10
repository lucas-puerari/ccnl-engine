"""Sickness episodes and the episodes earlier runs recorded."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.sickness import SicknessEpisode, SicknessHistory

_A = SicknessEpisode("a", date(2026, 2, 2), date(2026, 2, 11))


class TestEpisode:
    """An episode is an interval of illness with a stable id."""

    @pytest.mark.parametrize(
        ("kwargs", "field"),
        [
            ({"episode_id": " "}, "SicknessEpisode.episode_id"),
            (
                {"started_on": datetime(2026, 2, 2, tzinfo=UTC)},
                "SicknessEpisode.started_on",
            ),
            ({"ended_on": date(2026, 2, 1)}, "SicknessEpisode.ended_on"),
            ({"relapse_of": "a"}, "SicknessEpisode.relapse_of"),
            ({"relapse_of": ""}, "SicknessEpisode.relapse_of"),
            ({"short_absence_exempt": 1}, "SicknessEpisode.short_absence_exempt"),
        ],
    )
    def test_invalid_episode_is_rejected(
        self, kwargs: dict[str, object], field: str
    ) -> None:
        """Blank id, datetime, reversed days, a relapse of itself, a non-bool."""
        values: dict[str, object] = {
            "episode_id": "a",
            "started_on": date(2026, 2, 2),
            "ended_on": date(2026, 2, 11),
            **kwargs,
        }
        with pytest.raises(InvalidInputError) as raised:
            SicknessEpisode(**values)  # type: ignore[arg-type]
        assert raised.value.field == field

    def test_days_and_event_date(self) -> None:
        """2 to 11 February is ten days; the event date is the first."""
        assert _A.days == 10
        assert _A.event_date == date(2026, 2, 2)

    def test_within_clips_to_the_interval(self) -> None:
        """The days of February 2026, and none of March."""
        assert _A.within(date(2026, 2, 5), date(2026, 2, 28)) == (
            date(2026, 2, 5),
            date(2026, 2, 11),
        )
        assert _A.within(date(2026, 3, 1), date(2026, 3, 31)) is None

    def test_through_and_before_cut_the_episode(self) -> None:
        """Cut at 5 February, before 5 February, before its start."""
        assert _A.through(date(2026, 2, 5)).ended_on == date(2026, 2, 5)
        assert _A.through(date(2026, 2, 28)) is _A
        before = _A.before(date(2026, 2, 5))
        assert before is not None
        assert before.ended_on == date(2026, 2, 4)
        assert _A.before(date(2026, 2, 2)) is None


class TestHistory:
    """Recorded episodes chain relapses and reject contradictions."""

    def test_relapse_offset_is_the_chain_length(self) -> None:
        """Episode b continues a (10 days), c continues b (3 days): offset 13."""
        b = SicknessEpisode("b", date(2026, 3, 2), date(2026, 3, 4), "a")
        c = SicknessEpisode("c", date(2026, 3, 20), date(2026, 3, 21), "b")
        history = SicknessHistory((_A, b))
        assert history.offset(_A) == 0
        assert history.offset(c) == 13

    def test_relapse_of_an_unrecorded_episode_is_rejected(self) -> None:
        """The episode it continues must be recorded and earlier."""
        orphan = SicknessEpisode("b", date(2026, 3, 2), date(2026, 3, 4), "z")
        earlier = SicknessEpisode("b", date(2026, 1, 2), date(2026, 1, 4), "a")
        for episode in (orphan, earlier):
            with pytest.raises(InvalidInputError, match="no earlier run recorded"):
                SicknessHistory((_A,)).offset(episode)

    def test_check_rejects_a_moved_start_or_an_overlap(self) -> None:
        """The same id from another day, or another episode on its days."""
        history = SicknessHistory((_A,))
        moved = SicknessEpisode("a", date(2026, 2, 3), date(2026, 2, 11))
        overlap = SicknessEpisode("b", date(2026, 2, 10), date(2026, 2, 20))
        with pytest.raises(InvalidInputError, match="was recorded from"):
            history.check(moved)
        with pytest.raises(InvalidInputError, match="overlaps"):
            history.check(overlap)
        history.check(SicknessEpisode("a", date(2026, 2, 2), date(2026, 2, 20)))

    def test_check_rejects_days_already_paid(self) -> None:
        """Recorded through 11 February, the episode cannot pay 11 February."""
        history = SicknessHistory((_A,))
        longer = SicknessEpisode("a", date(2026, 2, 2), date(2026, 2, 20))
        with pytest.raises(InvalidInputError, match="already paid through"):
            history.check(longer, date(2026, 2, 11))
        history.check(longer, date(2026, 2, 12))

    def test_with_episode_replaces_and_orders(self) -> None:
        """An extended episode replaces its record; episodes stay in order."""
        early = SicknessEpisode("z", date(2026, 1, 5), date(2026, 1, 6))
        longer = SicknessEpisode("a", date(2026, 2, 2), date(2026, 2, 20))
        history = SicknessHistory((_A,))
        assert history.with_episode(longer) == (longer,)
        assert history.with_episode(early) == (early, _A)
        assert SicknessHistory((early, _A)).earlier(_A) == (early,)
