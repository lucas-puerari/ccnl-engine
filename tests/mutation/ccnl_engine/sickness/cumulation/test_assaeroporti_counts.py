"""Hand-computed G34 sick-pay on a EUR 100 contractual daily wage.

After 182 ordinary days and a two-day hospital stay, the next convalescence
sick day is count 183: EUR 100 rather than the former count 185 (EUR 50).
Convalescence itself still counts until certification is supported. After 365
ordinary days, a documented oncological day 366 pays EUR 50 rather than EUR 0.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment
from ccnl_engine.sickness.integration.models import SicknessCumulation, SicknessRules
from ccnl_engine.sickness.models import SeriousIllnessKind, SicknessEpisode

_START = date(2025, 1, 1)


def _rules() -> tuple[SicknessRules, SicknessCumulation]:
    agreement = load_ccnl("trasporto-aereo-assaeroporti")
    assert agreement.work_rules is not None
    rules = agreement.work_rules.sickness_rules
    assert rules is not None
    assert rules.cumulation is not None
    return rules, rules.cumulation


def test_hospital_and_following_convalescence_count() -> None:
    """After 182 days + 2 excluded stay days, day 185 pays EUR 100, not 50."""
    rules, cumulation = _rules()
    earlier = (SicknessEpisode("prior", _START, _START + timedelta(days=181)),)
    first = _START + timedelta(days=182)
    convalescence = first + timedelta(days=2)
    episode = SicknessEpisode(
        "stay-and-recovery",
        first,
        convalescence,
        hospital_stays=((first, first + timedelta(days=1)),),
    )
    treatment = CumulativeTreatment(rules, cumulation, episode, earlier)
    assert treatment.window_days(first + timedelta(days=1)) == 182
    assert treatment.window_days(convalescence) == 183
    result = treatment.day(3, convalescence)
    assert result.rate * Decimal(100) == Decimal(100)
    assert not result.beyond_comporto
    ordinary = cumulation.model_copy(update={"hospital_excluded_from_counts": False})
    old = CumulativeTreatment(rules, ordinary, episode, earlier).day(3, convalescence)
    assert old.rate * Decimal(100) == Decimal(50)


def test_hospital_does_not_exhaust_comporto() -> None:
    """At 365 prior days, an excluded hospital day pays EUR 50, not EUR 0."""
    rules, cumulation = _rules()
    previous = (SicknessEpisode("prior", _START, _START + timedelta(days=364)),)
    day = _START + timedelta(days=365)
    episode = SicknessEpisode("admission", day, day, hospital_stays=((day, day),))
    treatment = CumulativeTreatment(rules, cumulation, episode, previous)
    result = treatment.day(1, day)
    assert treatment.comporto_count(day) == 365
    assert not result.beyond_comporto
    assert result.rate * Decimal(100) == Decimal(50)
    ordinary = cumulation.model_copy(update={"hospital_excluded_from_counts": False})
    assert (
        CumulativeTreatment(rules, ordinary, episode, previous)
        .day(1, day)
        .beyond_comporto
    )


@pytest.mark.parametrize(
    "kind",
    [
        SeriousIllnessKind.ONCOLOGICAL,
        SeriousIllnessKind.MULTIPLE_SCLEROSIS,
        SeriousIllnessKind.MUSCULAR_DYSTROPHY,
    ],
)
def test_documented_illness_extends_overall_limit(kind: SeriousIllnessKind) -> None:
    """Day 366 of a documented condition pays EUR 50, versus EUR 0 ordinary."""
    rules, cumulation = _rules()
    previous = (SicknessEpisode("prior", _START, _START + timedelta(days=364)),)
    day = _START + timedelta(days=365)
    special = SicknessEpisode("special", day, day, serious_illness_kind=kind)
    treatment = CumulativeTreatment(rules, cumulation, special, previous)
    result = treatment.day(1, day)
    assert treatment.comporto_limit() == 1095
    assert result.rate * Decimal(100) == Decimal(50)
    assert not result.beyond_comporto
    ordinary = SicknessEpisode("ordinary", day, day)
    assert (
        CumulativeTreatment(rules, cumulation, ordinary, previous)
        .day(1, day)
        .beyond_comporto
    )
