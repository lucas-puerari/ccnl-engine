"""Poste Art. 41: hand-computed daily fixed pay of EUR 100.

An ordinary 502-day episode uses 502 full-pay days; on the next day ordinary
pay is EUR 0, while documented special eligibility pays EUR 100. Both
histories count toward the 609/730-day retention limits in 48 months.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.cumulation.results import cumulation_report
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_START = date(2025, 1, 1)
_CUMULATION = SicknessCumulation(
    window_years=4,
    reduced_integration_rate=Decimal(0),
    poste_special_eligibility=True,
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0,
            full_pay_days=502,
            comporto_days=609,
            serious_comporto_days=730,
            serious_full_pay_days=730,
        ),
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=Decimal(1),
    full_pay_integration_rate=Decimal(1),
    cumulation=_CUMULATION,
)
_EARLIER = (SicknessEpisode("ordinary", _START, _START + timedelta(days=501)),)


@pytest.mark.parametrize(
    ("eligible", "daily_amount", "beyond"),
    [
        (None, Decimal(0), False),
        (False, Decimal(0), False),
        (True, Decimal(100), False),
    ],
)
def test_qualifying_episode_after_ordinary_days(
    eligible: bool | None, daily_amount: Decimal, beyond: bool
) -> None:
    """On cumulative day 503, ordinary EUR 0 becomes special EUR 100."""
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, poste_special_eligible=eligible)
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER)
    result = treatment.day(1, day)
    assert result.rate * Decimal(100) == daily_amount
    assert result.beyond_comporto is beyond
    assert treatment.window_days(day) == 503
    assert cumulation_report(treatment, (day, day)).reduced is not (eligible is True)


@pytest.mark.parametrize(
    ("eligible", "offset", "amount", "beyond"),
    [
        (False, 609, Decimal(0), True),
        (True, 609, Decimal(100), False),
        (True, 729, Decimal(100), False),
        (True, 730, Decimal(0), True),
    ],
)
def test_retention_boundary(
    eligible: bool, offset: int, amount: Decimal, beyond: bool
) -> None:
    """Day 610: ordinary EUR 0, special EUR 100; day 731 exceeds 730."""
    first = _START + timedelta(days=502)
    last = _START + timedelta(days=offset)
    episode = SicknessEpisode("new", first, last, poste_special_eligible=eligible)
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER)
    result = treatment.day(offset - 501, last)
    assert result.rate * Decimal(100) == amount
    assert result.beyond_comporto is beyond


def test_general_serious_illness_does_not_assert_poste_eligibility() -> None:
    """A general serious-illness flag alone does not qualify Art. 41 II."""
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, serious_illness=True)
    result = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER).day(1, day)
    assert result.rate * Decimal(100) == Decimal(0)


def test_agreement_uses_verified_special_limits() -> None:
    """Poste agreement pays EUR 100 on cumulative day 503, not EUR 0."""
    agreement = load_ccnl("poste-italiane-k700")
    assert agreement.work_rules is not None
    rules = agreement.work_rules.sickness_rules
    assert rules is not None
    cumulation = rules.cumulation
    assert cumulation is not None
    assert cumulation.poste_special_eligibility
    assert cumulation.bands[0].serious_comporto_days == 730
    assert cumulation.bands[0].serious_full_pay_days == 730
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, poste_special_eligible=True)
    result = CumulativeTreatment(rules, cumulation, episode, _EARLIER).day(1, day)
    assert result.rate * Decimal(100) == Decimal(100)


def test_eligibility_requires_boolean() -> None:
    """Invalid certificate facts cannot activate the special limit."""
    with pytest.raises(InvalidInputError, match="poste_special_eligible"):
        SicknessEpisode("bad", _START, _START, poste_special_eligible="yes")  # type: ignore[arg-type]
