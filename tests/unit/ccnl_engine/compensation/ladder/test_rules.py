"""The ladders of the levels, ordinary and by sub-sector."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.compensation.ladder.rules import level_below, levels_for, pay_ladders
from ccnl_engine.compensation.models import Level
from tests.unit.ccnl_engine.builders import _level, _series_with_prov


def _make(code: str, order: int, salary: str, **extra: Any) -> Level:  # noqa: ANN401
    return Level.model_validate({**_level(code, order, salary), **extra})


#: 4 and 5 of every sub-sector, 4s of pelli and occhiali only, X of giocattoli.
_FOUR = _make(
    "4", 1, "100.00", base_salary_by_subsector={"pelli": _series_with_prov("90.00")}
)
_FOUR_S = _make("4s", 2, "120.00", subsectors=("pelli", "occhiali"))
_FIVE = _make(
    "5", 3, "110.00", base_salary_by_subsector={"pelli": _series_with_prov("130.00")}
)
_X = _make("X", 4, "50.00", subsectors=("giocattoli",))
_LEVELS = (_FOUR, _FOUR_S, _FIVE, _X)


@pytest.mark.parametrize(
    ("subsector", "codes"),
    [
        (None, ["4", "5"]),
        ("pelli", ["4", "4s", "5"]),
        ("occhiali", ["4", "4s", "5"]),
        ("giocattoli", ["4", "5", "X"]),
        ("calzature", ["4", "5"]),
    ],
)
def test_a_run_keeps_the_common_levels_and_those_of_its_subsector(
    subsector: str | None, codes: list[str]
) -> None:
    """A level of other sub-sectors, or of any without one stated, is dropped."""
    assert [lv.code for lv in levels_for(_LEVELS, subsector)] == codes


def test_the_levels_below_are_counted_by_rank_on_the_ladder() -> None:
    """On the pelli ladder 5 is one above 4s; on the ordinary one above 4."""
    assert level_below(levels_for(_LEVELS, "pelli"), _FIVE, 1).code == "4s"
    assert level_below(levels_for(_LEVELS, None), _FIVE, 1).code == "4"
    assert level_below(_LEVELS, _FIVE, 0).code == "5"


def test_below_the_lowest_level_raises_unless_clamped() -> None:
    """Two below 5 on the ordinary ladder does not exist; clamped it is 4."""
    ladder = levels_for(_LEVELS, None)
    with pytest.raises(ValueError, match="no level 2 below '5'"):
        level_below(ladder, _FIVE, 2)
    assert level_below(ladder, _FIVE, 2, clamp=True).code == "4"


def test_a_level_off_the_ladder_raises() -> None:
    """4s is not on the ordinary ladder."""
    with pytest.raises(ValueError, match="'4s' is not on the ladder"):
        level_below(levels_for(_LEVELS, None), _FOUR_S, 0, clamp=True)


def test_the_pay_ladders_hold_the_levels_on_the_table_of_each_subsector() -> None:
    """The pelli ladder pays the pelli table; X and 4s stay off the ordinary one."""
    ladders = pay_ladders(_LEVELS)
    assert set(ladders) == {None, "pelli", "occhiali", "giocattoli"}
    assert [lv.code for lv in ladders[None]] == ["4", "5"]
    pelli = ladders["pelli"]
    assert [lv.code for lv in pelli] == ["4", "4s", "5"]
    assert [lv.base_salary.periods[0].value for lv in pelli] == [
        Decimal("90.00"),
        Decimal("120.00"),
        Decimal("130.00"),
    ]
    assert [lv.code for lv in ladders["occhiali"]] == ["4s"]
    assert [lv.code for lv in ladders["giocattoli"]] == ["X"]
