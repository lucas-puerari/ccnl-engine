"""Concia art. 60 B (renewal of 7 March 2024): special cases of the comporto.

Up to 3 years of seniority the comporto is 240 days within 36 months.  An
invalidating disease extends it by 2 months (300 days); hospital stays of
more than 5 consecutive days are left out of it, 60 days at most.
Every count is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.comporto.models import HospitalComportoRule
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.integration.condition.models import SeriousIllnessRule
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_ONE = Decimal(1)
_CUMULATION = SicknessCumulation(
    window_years=3,
    reset_after_days=120,
    reduced_integration_rate=Decimal("0.5"),
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0,
            full_pay_days=90,
            comporto_days=240,
            serious_comporto_days=300,
        ),
    ),
    serious_illness=SeriousIllnessRule(),
    hospital_comporto=HospitalComportoRule(more_than_days=5, max_days=60),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)
_WORKER = SicknessWorker(
    seniority=SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP)
)
_START = date(2026, 1, 1)


def _beyond(day: int, **facts: object) -> bool:
    episode = SicknessEpisode(
        "e",
        _START,
        _START + timedelta(days=399),
        **facts,  # type: ignore[arg-type]
    )
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, (), _WORKER)
    return treatment.day(day, _START + timedelta(days=day - 1)).beyond_comporto


def test_the_comporto_is_240_days() -> None:
    """Day 240 is within, day 241 past."""
    assert not _beyond(240)
    assert _beyond(241)


def test_an_invalidating_disease_extends_it_to_300() -> None:
    """With serious_illness the comporto is 300 days."""
    assert not _beyond(300, serious_illness=True)
    assert _beyond(301, serious_illness=True)


def test_long_hospital_stays_leave_it_up_to_60_days() -> None:
    """A 30-day stay moves the end by 30 days; a 90-day one by 60 only."""
    thirty = ((_START, _START + timedelta(days=29)),)
    assert not _beyond(270, hospital_stays=thirty)
    assert _beyond(271, hospital_stays=thirty)
    ninety = ((_START, _START + timedelta(days=89)),)
    assert not _beyond(300, hospital_stays=ninety)
    assert _beyond(301, hospital_stays=ninety)


def test_short_stays_count() -> None:
    """A stay of 5 days is not more than 5: it stays in the count."""
    five = ((_START, _START + timedelta(days=4)),)
    assert _beyond(241, hospital_stays=five)


_RESTART = _CUMULATION.model_copy(update={"hospital_restart_day": 16})
_RESTART_RULES = _RULES.model_copy(update={"cumulation": _RESTART})


def _rate(day: int, stays: tuple[tuple[date, date], ...] | None) -> Decimal:
    episode = SicknessEpisode(
        "e", _START, _START + timedelta(days=399), hospital_stays=stays
    )
    treatment = CumulativeTreatment(_RESTART_RULES, _RESTART, episode, (), _WORKER)
    return treatment.day(day, _START + timedelta(days=day - 1)).rate


def test_the_treatment_restarts_on_the_16th_day_of_a_stay() -> None:
    """Day 100 is at half; a stay from day 80 restarts the count on day 95.

    Day 95 counts 1 again, so day 100 (6th day of the new count) is in full;
    without the stay it is the 100th, past the 90 days in full.
    """
    stay = ((_START + timedelta(days=79), _START + timedelta(days=129)),)
    assert _rate(100, None) == Decimal("0.5")
    assert _rate(100, stay) == _ONE
    assert _rate(94, stay) == Decimal("0.5")  # day 15 of the stay: not yet


_RESTART12 = _CUMULATION.model_copy(
    update={
        "restart_after_full_pay_months": 12,
        "periodic_checks_outside_comporto": True,
    }
)
_RULES12 = _RULES.model_copy(update={"cumulation": _RESTART12})


def test_a_long_chain_restarts_twelve_months_after_the_full_pay() -> None:
    """The chain restarts 12 months after the full pay ended.

    Sick from 1 January 2025 for 100 days: the 90 days in full end on
    1 April 2025 (the 91st day).  Episodes linked by short returns keep the
    chain; one starting on 1 April 2026, 12 months later, starts it anew.
    """
    earlier = (
        SicknessEpisode("a", date(2025, 1, 1), date(2025, 4, 10)),
        SicknessEpisode("b", date(2025, 7, 1), date(2025, 7, 10)),
        SicknessEpisode("c", date(2025, 10, 1), date(2025, 10, 10)),
        SicknessEpisode("d", date(2026, 1, 1), date(2026, 1, 10)),
    )
    late = SicknessEpisode("e", date(2026, 4, 1), date(2026, 4, 30))
    treatment = CumulativeTreatment(_RULES12, _RESTART12, late, earlier, _WORKER)
    assert treatment.chain == (0, date(2026, 4, 1))
    early = SicknessEpisode("e", date(2026, 3, 31), date(2026, 4, 30))
    treatment = CumulativeTreatment(_RULES12, _RESTART12, early, earlier, _WORKER)
    assert treatment.chain[0] == 130


def test_periodic_checks_leave_the_comporto() -> None:
    """A periodic check is not summed into the comporto."""
    check = SicknessEpisode(
        "chk", date(2025, 6, 1), date(2025, 6, 3), periodic_check=True
    )
    episode = SicknessEpisode("e", _START, _START)
    treatment = CumulativeTreatment(_RULES12, _RESTART12, episode, (check,), _WORKER)
    assert treatment.window_days(_START) == 1


def test_an_earlier_restart_counts_from_its_episode() -> None:
    """The episode of 1 April 2026 restarted the chain: a later one counts from it."""
    earlier = (
        SicknessEpisode("a", date(2025, 1, 1), date(2025, 4, 10)),
        SicknessEpisode("b", date(2025, 7, 1), date(2025, 7, 10)),
        SicknessEpisode("c", date(2025, 10, 1), date(2025, 10, 10)),
        SicknessEpisode("d", date(2026, 1, 1), date(2026, 1, 10)),
        SicknessEpisode("e", date(2026, 4, 1), date(2026, 4, 30)),
    )
    later = SicknessEpisode("f", date(2026, 6, 1), date(2026, 6, 5))
    treatment = CumulativeTreatment(_RULES12, _RESTART12, later, earlier, _WORKER)
    assert treatment.chain == (30, date(2026, 4, 1))
