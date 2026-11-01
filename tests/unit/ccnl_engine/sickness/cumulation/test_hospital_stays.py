"""Hospital stays paid in full within the reduced days.

Federmeccanica Sez. Quarta Titolo VI art. 2: stays of more than 10
consecutive days are paid with the whole pay "fino ad un massimo di 61
giorni di calendario".  A worker up to three years of seniority has 122
days in full, then 80%.  Every count is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.integration.condition.models import HospitalStayRule
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_ONE = Decimal(1)
_REDUCED = Decimal("0.8")
_CUMULATION = SicknessCumulation(
    window_years=3,
    reset_after_days=61,
    reduced_integration_rate=_REDUCED,
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0, full_pay_days=122, comporto_days=183
        ),
    ),
    hospital_stay=HospitalStayRule(more_than_days=10, max_full_days=61),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)
_WORKER = SicknessWorker(
    seniority=SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP)
)
#: 1 January 2026 + 121 days: day 122 is 2 May, day 123 (80%) is 3 May.
_START = date(2026, 1, 1)


def _rate(stays: tuple[tuple[date, date], ...] | None, day: date) -> Decimal:
    episode = SicknessEpisode("e", _START, date(2026, 6, 30), hospital_stays=stays)
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, (), _WORKER)
    return treatment.day(0, day).rate


@pytest.mark.parametrize(
    ("stays", "day", "rate"),
    [
        (None, date(2026, 5, 3), _REDUCED),  # first reduced day
        (((date(2026, 5, 1), date(2026, 5, 11)),), date(2026, 5, 3), _ONE),  # 11 days
        (((date(2026, 5, 1), date(2026, 5, 10)),), date(2026, 5, 3), _REDUCED),  # 10
        # 1 May - 30 June, 61 days: 30 June is the 61st, still in full.
        (((date(2026, 5, 1), date(2026, 6, 30)),), date(2026, 6, 30), _ONE),
        # From 2 March: 3 May is the 63rd day of the stay, past the 61.
        (((date(2026, 3, 2), date(2026, 6, 30)),), date(2026, 5, 3), _REDUCED),
    ],
    ids=["no_stay", "eleven_days", "ten_days", "sixty_first", "past_61"],
)
def test_long_stays_are_paid_in_full(
    stays: tuple[tuple[date, date], ...] | None, day: date, rate: Decimal
) -> None:
    """A reduced day of a stay over 10 days is paid in full, 61 days at most."""
    assert _rate(stays, day) == rate


def test_a_stay_outside_the_episode_is_rejected() -> None:
    """A stay lies within the days of its episode."""
    with pytest.raises(InvalidInputError, match="hospital_stays"):
        SicknessEpisode(
            "e",
            date(2026, 3, 1),
            date(2026, 3, 10),
            hospital_stays=((date(2026, 3, 5), date(2026, 3, 12)),),
        )


def test_cutting_the_episode_cuts_its_stays() -> None:
    """A stay past the day processed is cut with the episode."""
    episode = SicknessEpisode(
        "e",
        date(2026, 3, 1),
        date(2026, 4, 30),
        hospital_stays=(
            (date(2026, 3, 10), date(2026, 4, 5)),
            (date(2026, 4, 20), date(2026, 4, 25)),
        ),
    )

    cut = episode.through(date(2026, 3, 31))

    assert cut.hospital_stays == ((date(2026, 3, 10), date(2026, 3, 31)),)
    assert episode.through(date(2026, 5, 1)) is episode
