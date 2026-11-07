"""The comporto counting an employer chooses (ABI Art. 66 c. 2)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import EmployerProfile, Headcount
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.counting.rules import with_window_counting

if TYPE_CHECKING:
    from ccnl_engine.sickness.integration.models import SicknessRules

_ABI = load_ccnl("bancari-abi")


def _sickness(chosen: bool) -> SicknessRules:
    work = with_window_counting(_ABI, chosen).work_rules
    assert work is not None
    assert work.sickness_rules is not None
    return work.sickness_rules


def test_the_counting_of_each_illness_is_kept_by_default() -> None:
    """Art. 66 c. 1: 6 to 22 months of each illness, no window."""
    assert with_window_counting(_ABI, False) is _ABI


def test_the_48_months_replace_the_bands_of_each_illness() -> None:
    """Art. 66 c. 2: 8 to 24 months over the 48 before the last day."""
    rules = _sickness(True)

    assert [(w.window_months, w.comporto_days) for w in rules.comporto_windows] == [
        (48, 240),
        (48, 300),
        (48, 420),
        (48, 540),
        (48, 660),
        (48, 720),
    ]
    assert [
        (b.seniority_months_from, b.comporto_days) for b in rules.comporto_bands
    ] == [(w.seniority_months_from, w.comporto_days) for w in rules.comporto_windows]


def test_a_ccnl_without_the_alternative_rejects_the_choice() -> None:
    """Commercio counts the calendar year only."""
    with pytest.raises(InvalidInputError, match="no alternative comporto window") as e:
        with_window_counting(load_ccnl("commercio-confcommercio"), True)

    assert (e.value.field, e.value.feature) == (
        "EmployerProfile.sickness_window_counting",
        "sickness",
    )


def test_a_ccnl_without_sickness_rules_rejects_the_choice() -> None:
    """No sickness rules, no window to choose."""
    work = _ABI.work_rules
    assert work is not None
    bare = _ABI.model_copy(
        update={"work_rules": work.model_copy(update={"sickness_rules": None})}
    )
    with pytest.raises(InvalidInputError, match="no alternative comporto window"):
        with_window_counting(bare, True)


def test_a_ccnl_without_work_rules_rejects_the_choice() -> None:
    """No work rules at all."""
    with pytest.raises(InvalidInputError, match="no alternative comporto window"):
        with_window_counting(_ABI.model_copy(update={"work_rules": None}), True)


def test_the_flag_must_be_a_bool() -> None:
    """A string is not a choice."""
    with pytest.raises(InvalidInputError, match="sickness_window_counting"):
        EmployerProfile(headcount=Headcount(10), sickness_window_counting="yes")  # type: ignore[arg-type]


def test_a_run_reads_the_choice() -> None:
    """The run of an ABI employer that counts by c. 2 loads its windows."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(100), sickness_window_counting=True
            ),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="bancari-abi",
            level_code=next(lv.code for lv in _ABI.levels),
            opening_state=PeriodState.zero(),
            roles=frozenset(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
