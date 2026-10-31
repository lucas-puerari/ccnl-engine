"""Sickness of a fixed-term contract, D.L. 463/1983 art. 5.

- c. 1: sickness is paid for no more days than those of work in the 12
  months before the episode;
- c. 3: with 30 days of work or fewer, for at most 30 days in the calendar
  year, the INPS share paid by INPS directly;
- c. 5: the employer advances the INPS share only for as many days as the
  worker worked for it; INPS pays the others directly.

INPS rules of the tests: waiting period of three days, 50% from day 4.
Every count is read off the calendar by hand.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
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

_HALF = Decimal("0.50")
_ONE = Decimal(1)
_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[SickPayBand(day_from=4, day_to=180, rate=_HALF)],
    annual_max_days=180,
    coverage=(SickPayCoverage(covered=True, source="test: every worker"),),
    fixed_term=FixedTermSickLimit(short_work_days=30),
)
_FULL = SicknessRules(carenza_integration_rate=_ONE, full_pay_integration_rate=_ONE)


def _rules(*, fixed_term: bool = True, hired_on: date | None = None) -> SickPayRules:
    return SickPayRules(
        inps=_INPS,
        inps_cover=True,
        ccnl=_FULL,
        worker=SicknessWorker(hired_on=hired_on),
        fixed_term=fixed_term,
    )


def _kinds(
    episode: SicknessEpisode, rules: SickPayRules
) -> list[tuple[date, date, SickDayKind, bool]]:
    span = (episode.started_on, episode.ended_on)
    return [
        (s.first, s.last, s.kind, s.inps_direct)
        for s in classify_days(episode, span, SicknessHistory(), rules)
    ]


def test_days_beyond_the_days_of_work_are_unpaid() -> None:
    """40 days of work: an episode of 45 days pays 40, then nothing."""
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 4, 14), prior_worked_days=40
    )
    assert _kinds(episode, _rules()) == [
        (date(2026, 3, 1), date(2026, 3, 3), SickDayKind.CARENZA, False),
        (date(2026, 3, 4), date(2026, 4, 9), SickDayKind.INDEMNIFIED, False),
        (date(2026, 4, 10), date(2026, 4, 14), SickDayKind.FIXED_TERM_LIMIT, False),
    ]


def test_inps_pays_directly_beyond_the_days_with_this_employer() -> None:
    """Hired on 21 February: 8 days with this employer before 1 March.

    Days 1-3 are carenza, 4-8 advanced by the employer, from day 9 (9
    March) INPS pays its share directly.
    """
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 3, 12), prior_worked_days=200
    )
    assert _kinds(episode, _rules(hired_on=date(2026, 2, 21))) == [
        (date(2026, 3, 1), date(2026, 3, 3), SickDayKind.CARENZA, False),
        (date(2026, 3, 4), date(2026, 3, 8), SickDayKind.INDEMNIFIED, False),
        (date(2026, 3, 9), date(2026, 3, 12), SickDayKind.INDEMNIFIED, True),
    ]


def test_a_regime_paid_directly_has_inps_pay_every_day() -> None:
    """Operai agricoli a tempo determinato: no days of work stated, INPS pays.

    Days 1-3 are carenza; from day 4 INPS pays its share directly, the
    days of c. 1 not applying.
    """
    direct = _INPS.model_copy(
        update={
            "fixed_term": FixedTermSickLimit(short_work_days=30, paid_directly=True)
        }
    )
    rules = replace(_rules(hired_on=date(2026, 2, 21)), inps=direct)
    episode = SicknessEpisode("a", date(2026, 3, 1), date(2026, 3, 12))

    assert _kinds(episode, rules) == [
        (date(2026, 3, 1), date(2026, 3, 3), SickDayKind.CARENZA, False),
        (date(2026, 3, 4), date(2026, 3, 12), SickDayKind.INDEMNIFIED, True),
    ]


def test_thirty_days_a_year_paid_by_inps_when_work_was_short() -> None:
    """20 days of work: 30 days of 2026 paid, every INPS day directly."""
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 4, 5), prior_worked_days=20
    )
    assert _kinds(episode, _rules(hired_on=date(2025, 1, 1))) == [
        (date(2026, 3, 1), date(2026, 3, 3), SickDayKind.CARENZA, False),
        (date(2026, 3, 4), date(2026, 3, 30), SickDayKind.INDEMNIFIED, True),
        (date(2026, 3, 31), date(2026, 4, 5), SickDayKind.FIXED_TERM_LIMIT, False),
    ]


@pytest.mark.parametrize(
    ("fixed_term", "worked"), [(False, 10), (True, None)], ids=["open", "unstated"]
)
def test_no_limit_without_a_fixed_term_or_the_fact(
    fixed_term: bool, worked: int | None
) -> None:
    """An open-ended contract, or an unstated fact, keeps every day paid."""
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 3, 20), prior_worked_days=worked
    )
    kinds = _kinds(episode, _rules(fixed_term=fixed_term))
    assert SickDayKind.FIXED_TERM_LIMIT not in {k for _, _, k, _ in kinds}


def test_hire_date_unknown_keeps_the_advance() -> None:
    """Without the hire date the employer advances every INPS day."""
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 3, 10), prior_worked_days=200
    )
    assert not any(direct for *_, direct in _kinds(episode, _rules()))


@pytest.mark.parametrize("worked", [-1, 367])
def test_days_of_work_are_bounded(worked: int) -> None:
    """The days of work of 12 months lie in [0, 366]."""
    with pytest.raises(InvalidInputError, match="prior_worked_days"):
        SicknessEpisode(
            "a", date(2026, 3, 1), date(2026, 3, 2), prior_worked_days=worked
        )


def test_a_table_without_the_rule_applies_no_limit() -> None:
    """The limit is the bundle's record: a table without it applies none."""
    rules = _rules()
    bare = rules.inps.model_copy(update={"fixed_term": None})
    episode = SicknessEpisode(
        "a", date(2026, 3, 1), date(2026, 4, 14), prior_worked_days=10
    )
    kinds = _kinds(episode, replace(rules, inps=bare))
    assert SickDayKind.FIXED_TERM_LIMIT not in {k for _, _, k, _ in kinds}
