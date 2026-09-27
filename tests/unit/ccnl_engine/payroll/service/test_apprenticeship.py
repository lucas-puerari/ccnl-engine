"""Apprenticeship period, track and pay chain selection."""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.identity._ccnl import CCNL
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.apprenticeship import (
    _apprentice_chain,
    _find_period_index,
    _select_track,
)
from ccnl_engine.shared.domain.errors import OutOfScopeError
from tests.helpers import make_ccnl_dict, make_minimal_ccnl

_AS_OF = date(2026, 6, 1)


def _ccnl_two_tracks_same_level() -> CCNL:
    """Build a CCNL with two percentage tracks both covering level 4.

    Returns:
        A :class:`CCNL` instance with ambiguous apprenticeship tracks.
    """
    raw = make_ccnl_dict(app_type="percentage")
    second_track = copy.deepcopy(raw["apprenticeship"][0])
    second_track["name"] = "alternative"
    raw["apprenticeship"].append(second_track)
    return CCNL.model_validate(raw)


class TestFindPeriodIndex:
    """_find_period_index error paths."""

    def test_no_period_covers_months_elapsed_raises(self) -> None:
        """Raises OutOfScopeError when no period covers months_elapsed."""

        class _P:
            months_from: int = 0
            months_until: int | None = 12

        with pytest.raises(OutOfScopeError, match="no apprenticeship period"):
            _find_period_index([_P()], 24)

    def test_empty_periods_raises(self) -> None:
        """Raises OutOfScopeError when periods list is empty."""
        with pytest.raises(OutOfScopeError, match="no apprenticeship period"):
            _find_period_index([], 0)


class TestSelectTrack:
    """_select_track error and success paths."""

    def test_explicit_named_track_returns_track(self) -> None:
        """Named track matching the level is returned directly."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track="standard")
        track = _select_track(ccnl, level, employment)
        assert track.name == "standard"

    def test_explicit_wrong_level_raises(self) -> None:
        """Named track not covering the destination level raises OutOfScopeError."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level_2 = ccnl.level_by_code("2")
        employment = Apprentice(months_elapsed=0, track="standard")
        with pytest.raises(OutOfScopeError, match="does not cover destination level"):
            _select_track(ccnl, level_2, employment)

    def test_no_track_for_level_raises(self) -> None:
        """Level with no applicable track raises OutOfScopeError."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level_2 = ccnl.level_by_code("2")
        employment = Apprentice(months_elapsed=0, track=None)
        with pytest.raises(OutOfScopeError, match="has no apprenticeship track"):
            _select_track(ccnl, level_2, employment)

    def test_ambiguous_tracks_raises(self) -> None:
        """Level with multiple tracks raises OutOfScopeError when track is None."""
        ccnl = _ccnl_two_tracks_same_level()
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        with pytest.raises(
            OutOfScopeError, match="covered by several apprenticeship tracks"
        ):
            _select_track(ccnl, level, employment)


class TestApprenticeChain:
    """_apprentice_chain underclass and percentage track paths."""

    def test_underclass_track(self) -> None:
        """Under-classification track sets pct=None and code to pay level."""
        ccnl = make_minimal_ccnl(app_type="under_classification")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, pct, code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        assert pct is None
        assert code is not None
        assert chain.base > Decimal(0)

    def test_underclass_midpoint_to_destination(self) -> None:
        """midpoint_to_destination=True sets base to average of pay and dest level."""
        raw = make_ccnl_dict(app_type="under_classification")
        raw["apprenticeship"][0]["periods"][0]["midpoint_to_destination"] = True
        ccnl = CCNL.model_validate(raw)
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, _pct, _code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        pay_level = ccnl.level_by_code("3")
        dest_base = level.base_salary.value_at(_AS_OF)
        pay_base = pay_level.base_salary.value_at(_AS_OF)
        expected = money((pay_base + dest_base) / Decimal(2))
        assert chain.base == expected

    def test_percentage_track(self) -> None:
        """Percentage track sets pct to the period percentage and code=None."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, pct, code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        assert pct is not None
        assert code is None
        assert chain.base > Decimal(0)
