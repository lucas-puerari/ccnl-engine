"""Art. 41: hand-computed daily fixed pay of EUR 100.

An ordinary 502-day episode uses 502 full-pay days; on the next day ordinary
pay is EUR 0, while a documented qualifying condition pays EUR 100. Both
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
from ccnl_engine.sickness.models import SeriousIllnessKind, SicknessEpisode

_START = date(2025, 1, 1)
_KINDS = frozenset({
    SeriousIllnessKind.CERTIFIED_LISTED_GRAVE_PATHOLOGY,
    SeriousIllnessKind.CERTIFIED_L68_99_DISABILITY,
    SeriousIllnessKind.CERTIFIED_RELATED_LIFE_SAVING_THERAPY,
})
_CUMULATION = SicknessCumulation(
    window_years=4,
    reduced_integration_rate=Decimal(0),
    qualifying_kinds=_KINDS,
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
    ("kind", "daily_amount"),
    [
        (None, Decimal(0)),
        (SeriousIllnessKind.ONCOLOGICAL, Decimal(0)),
        *[(kind, Decimal(100)) for kind in sorted(_KINDS)],
    ],
)
def test_qualifying_episode_after_ordinary_days(
    kind: SeriousIllnessKind | None, daily_amount: Decimal
) -> None:
    """On cumulative day 503, ordinary EUR 0 becomes qualifying EUR 100."""
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, serious_illness_kind=kind)
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER)
    result = treatment.day(1, day)
    assert result.rate * Decimal(100) == daily_amount
    assert result.beyond_comporto is False
    assert treatment.window_days(day) == 503
    assert cumulation_report(treatment, (day, day)).reduced is (kind not in _KINDS)


@pytest.mark.parametrize(
    ("kind", "offset", "amount", "beyond"),
    [
        (None, 609, Decimal(0), True),
        (SeriousIllnessKind.ONCOLOGICAL, 609, Decimal(0), True),
        (SeriousIllnessKind.CERTIFIED_LISTED_GRAVE_PATHOLOGY, 609, Decimal(100), False),
        (SeriousIllnessKind.CERTIFIED_LISTED_GRAVE_PATHOLOGY, 729, Decimal(100), False),
        (SeriousIllnessKind.CERTIFIED_LISTED_GRAVE_PATHOLOGY, 730, Decimal(0), True),
    ],
)
def test_retention_boundary(
    kind: SeriousIllnessKind | None, offset: int, amount: Decimal, beyond: bool
) -> None:
    """Day 610: ordinary EUR 0, qualifying EUR 100; day 730 EUR 100, 731 EUR 0."""
    first = _START + timedelta(days=502)
    last = _START + timedelta(days=offset)
    episode = SicknessEpisode("new", first, last, serious_illness_kind=kind)
    treatment = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER)
    result = treatment.day(offset - 501, last)
    assert result.rate * Decimal(100) == amount
    assert result.beyond_comporto is beyond


def test_general_serious_illness_does_not_assert_listed_eligibility() -> None:
    """A general serious-illness flag alone leaves day 503 at EUR 0."""
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, serious_illness=True)
    result = CumulativeTreatment(_RULES, _CUMULATION, episode, _EARLIER).day(1, day)
    assert result.rate * Decimal(100) == Decimal(0)


def test_agreement_uses_verified_special_limits() -> None:
    """The loaded agreement pays EUR 100 on cumulative day 503, not EUR 0."""
    agreement = load_ccnl("poste-italiane-k700")
    assert agreement.work_rules is not None
    rules = agreement.work_rules.sickness_rules
    assert rules is not None
    cumulation = rules.cumulation
    assert cumulation is not None
    assert cumulation.qualifying_kinds == _KINDS
    assert cumulation.bands[0].serious_comporto_days == 730
    assert cumulation.bands[0].serious_full_pay_days == 730
    day = _START + timedelta(days=502)
    episode = SicknessEpisode(
        "new",
        day,
        day,
        serious_illness_kind=SeriousIllnessKind.CERTIFIED_L68_99_DISABILITY,
    )
    result = CumulativeTreatment(rules, cumulation, episode, _EARLIER).day(1, day)
    assert result.rate * Decimal(100) == Decimal(100)


def test_kind_requires_enum() -> None:
    """An unvalidated string cannot activate the extended EUR 100 rate."""
    with pytest.raises(InvalidInputError, match="serious_illness_kind"):
        SicknessEpisode("bad", _START, _START, serious_illness_kind="yes")  # type: ignore[arg-type]


def test_empty_kinds_preserve_general_serious_illness_behavior() -> None:
    """Without a kind filter, the existing flag still pays EUR 100 on day 503."""
    cumulation = _CUMULATION.model_copy(update={"qualifying_kinds": frozenset()})
    day = _START + timedelta(days=502)
    episode = SicknessEpisode("new", day, day, serious_illness=True)
    result = CumulativeTreatment(_RULES, cumulation, episode, _EARLIER).day(1, day)
    assert result.rate * Decimal(100) == Decimal(100)
