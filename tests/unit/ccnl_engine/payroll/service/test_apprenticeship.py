"""Apprenticeship period, track and pay chain selection."""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.contract.domain.identity._ccnl import CCNL
from ccnl_engine.payroll.domain.employment import Apprentice
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


def _allowance(level: dict[str, Any], code: str, value: str) -> dict[str, Any]:
    monthly = copy.deepcopy(level["base_salary"])
    monthly["periods"][0]["value"] = value
    return {
        "code": code,
        "description": code,
        "monthly": monthly,
        "provenance": level["provenance"],
    }


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
        """The midpoint averages the whole pay of the pay and destination levels.

        Pay level 3: base 800.00, A 10.01, B 5.00 (total 815.01).
        Destination 4: base 1000.00, A 20.00, C 3.01 (total 1023.01).
        Mean of the totals: 919.01.  Allowances: A 15.005 -> 15.01,
        B 5.00 / 2 = 2.50, C 3.01 / 2 = 1.505 -> 1.51.  The base takes the
        rest: 919.01 - 19.02 = 899.99 (not the rounded 900.00, which would
        pay one cent over the mean).
        """
        raw = make_ccnl_dict(app_type="under_classification")
        raw["apprenticeship"][0]["periods"][0]["midpoint_to_destination"] = True
        levels = {level["code"]: level for level in raw["levels"]}
        levels["3"]["fixed_allowances"] = [
            _allowance(levels["3"], "A", "10.01"),
            _allowance(levels["3"], "B", "5.00"),
        ]
        levels["4"]["fixed_allowances"] = [
            _allowance(levels["4"], "A", "20.00"),
            _allowance(levels["4"], "C", "3.01"),
        ]
        ccnl = CCNL.model_validate(raw)
        chain, _pct, _code = _apprentice_chain(
            ccnl,
            ccnl.level_by_code("4"),
            Apprentice(months_elapsed=0, track=None),
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        assert chain.base == Decimal("899.99")
        assert [(a.code, v) for a, v in chain.allowances] == [
            ("A", Decimal("15.01")),
            ("B", Decimal("2.50")),
            ("C", Decimal("1.51")),
        ]
        assert chain.limitations == (
            f"{ccnl.meta.ccnl_id}/apprenticeship_midpoint_components",
        )

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
