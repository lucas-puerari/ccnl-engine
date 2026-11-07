"""Tabacco art. 34, impiegati: the comporto is counted over the chain.

Up to 5 years of seniority: 4 months of full pay, 4 of half pay, job kept
for 12 months; "Le interruzioni suddette non si sommano quando si
verificano alla distanza di almeno un anno dalla fine della interruzione
precedente".  Months of 30 days; every count is read off the calendar.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessDayBand,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_ONE = Decimal(1)
_CUMULATION = SicknessCumulation(
    window_years=1,
    reset_after_days=365,
    comporto_over_chain=True,
    reduced_integration_rate=Decimal(0),
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0,
            full_pay_days=120,
            comporto_days=365,
            steps=(
                SicknessDayBand(
                    day_from=121, day_until=241, integration_rate=Decimal("0.5")
                ),
            ),
        ),
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    net_basis=False,
    cumulation=_CUMULATION,
)
_WORKER = SicknessWorker(
    seniority=SeniorityFact(12, date(2024, 1, 1), SenioritySource.PAYSLIP)
)
_EARLIER = SicknessEpisode("a", date(2025, 1, 1), date(2025, 6, 29))


def _treatment(start: date, *earlier: SicknessEpisode) -> CumulativeTreatment:
    episode = SicknessEpisode("e", start, start + timedelta(days=499))
    return CumulativeTreatment(_RULES, _CUMULATION, episode, earlier, _WORKER)


def _day(treatment: CumulativeTreatment, nth: int) -> tuple[bool, Decimal]:
    day = treatment.episode.started_on + timedelta(days=nth - 1)
    result = treatment.day(nth, day)
    return result.beyond_comporto, result.rate


@pytest.mark.parametrize(
    ("nth", "rate"),
    [(120, _ONE), (121, Decimal("0.5")), (240, Decimal("0.5")), (241, Decimal(0))],
)
def test_full_then_half_then_nothing(nth: int, rate: Decimal) -> None:
    """Four months of full pay, four of half pay, then no integration."""
    assert _day(_treatment(date(2026, 1, 1)), nth) == (False, rate)


def test_one_episode_keeps_the_job_365_days() -> None:
    """Day 365 is within the comporto, day 366 past it."""
    treatment = _treatment(date(2026, 1, 1))
    assert not _day(treatment, 365)[0]
    assert _day(treatment, 366)[0]


def test_an_episode_within_a_year_sums_the_earlier_one() -> None:
    """180 days in 2025, back to work 155 days, then sick from 1 December.

    The chain holds 180 days: day 185 of the new episode is the 365th,
    day 186 the 366th, past the comporto although most of the earlier
    episode is more than a year before.
    """
    treatment = _treatment(date(2025, 12, 1), _EARLIER)
    assert not _day(treatment, 185)[0]
    assert _day(treatment, 186)[0]


def test_an_episode_a_year_later_starts_anew() -> None:
    """365 days of work after the earlier episode: a new count."""
    treatment = _treatment(date(2026, 7, 1), _EARLIER)
    assert _day(treatment, 1) == (False, _ONE)
    assert not _day(treatment, 365)[0]


def test_the_chain_count_needs_a_reset() -> None:
    """Without reset_after_days there is no chain to count over."""
    with pytest.raises(ValueError, match="comporto_over_chain needs reset_after_days"):
        SicknessCumulation(
            window_years=1,
            comporto_over_chain=True,
            reduced_integration_rate=Decimal(0),
            bands=_CUMULATION.bands,
        )
