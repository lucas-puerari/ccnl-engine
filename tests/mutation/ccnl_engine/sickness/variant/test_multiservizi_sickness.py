"""CNEL 105782 art. 51 (pp. 67-68), replaced by CNEL 139292 pp. 22-24."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.sickness.day.models import SickPayRules
from ccnl_engine.sickness.day.rules import SickDayKind, classify_days
from ccnl_engine.sickness.indemnity.models import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)
from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory
from ccnl_engine.sickness.pay.handlers import episode_pay
from ccnl_engine.sickness.term.rules import DailyQuota, SicknessTerms
from ccnl_engine.sickness.variant.rules import with_sickness_variant

_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[SickPayBand(day_from=4, day_to=180, rate=Decimal("0.5"))],
    annual_max_days=180,
    coverage=(SickPayCoverage(covered=True, source="test: insured"),),
)


def _rules(category: WorkerCategory) -> SickPayRules:
    agreement = with_sickness_variant(
        load_ccnl("multiservizi-anip"), category, Permanent()
    )
    assert agreement.work_rules is not None
    rule = agreement.work_rules.sickness_rules
    assert rule is not None
    return SickPayRules(inps=_INPS, inps_cover=True, ccnl=rule)


@pytest.mark.parametrize(
    ("category", "integration", "net_basis"),
    [
        (WorkerCategory.OPERAIO, Decimal("44.44"), True),
        (WorkerCategory.IMPIEGATO, Decimal("50.00"), False),
    ],
)
def test_four_day_episode_by_category(
    category: WorkerCategory, integration: Decimal, net_basis: bool
) -> None:
    """EUR 2600/26 = 100/day: 3 waiting days = 300, day 4 INPS = 50.

    Operai: net target 100 minus INPS grossed up at 10% (55.56) = 44.44.
    Impiegati: gross target 100 minus INPS 50 = 50.00. Before both
    categories used the gross default and paid 50.00 integration.
    """
    rules = _rules(category)
    assert rules.ccnl.net_basis is net_basis
    episode = SicknessEpisode("ill", date(2026, 3, 2), date(2026, 3, 5))
    paid = episode_pay(
        episode,
        (episode.started_on, episode.ended_on),
        SicknessTerms(
            rules=rules,
            quota=DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
            chain=MonthlyPayChain(Decimal(2600), Decimal(0), ()),
            employee_rate=Decimal("0.10"),
        ),
    )
    assert paid is not None
    assert paid.absence == Decimal("400.00")
    assert paid.carenza == Decimal("300.00")
    assert paid.inps == Decimal("50.00")
    assert paid.integration == integration


@pytest.mark.parametrize(
    ("category", "last_full", "first_half", "last_half"),
    [
        (WorkerCategory.OPERAIO, 180, 181, 270),
        (WorkerCategory.IMPIEGATO, 150, 151, 360),
    ],
)
def test_episode_band_boundaries(
    category: WorkerCategory, last_full: int, first_half: int, last_half: int
) -> None:
    """A EUR 100 gross daily quota: full = EUR 100, half = EUR 50.

    The rolling 36-month window keeps the job for 360 days independently
    of the end of the operai integration at day 270.
    """
    rules = _rules(category)
    first = date(2026, 1, 1)
    episode = SicknessEpisode("ill", first, first + timedelta(days=360))
    for index, rate in (
        (last_full, 1),
        (first_half, Decimal("0.5")),
        (last_half, Decimal("0.5")),
    ):
        day = first + timedelta(days=index - 1)
        segments = classify_days(episode, (day, day), SicknessHistory(), rules)
        assert len(segments) == 1
        assert segments[0].worker_rate == rate
    day = first + timedelta(days=last_half)
    segments = classify_days(episode, (day, day), SicknessHistory(), rules)
    assert segments[0].worker_rate == 0
    if category is WorkerCategory.OPERAIO:
        assert segments[0].kind is not SickDayKind.BEYOND_COMPORTO
        last_day = first + timedelta(days=359)
        assert (
            classify_days(episode, (last_day, last_day), SicknessHistory(), rules)[
                0
            ].kind
            is not SickDayKind.BEYOND_COMPORTO
        )
    beyond_day = first + timedelta(days=360)
    assert (
        classify_days(episode, (beyond_day, beyond_day), SicknessHistory(), rules)[
            0
        ].kind
        is SickDayKind.BEYOND_COMPORTO
    )
    assert rules.ccnl.comporto_windows[0].comporto_days == 360
