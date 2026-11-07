"""Metalmeccanico artigianato, art. 73: sickness of the impiegati.

CCNL 17 December 2021 (PDF p. 147): the whole gross pay for 2 months and
half for the next 4 up to 5 years of seniority, the whole for 3 and half
for the next 5 above; job kept 6 or 8 months for one illness and 10 months
in the 24 before.  Months of 30 days.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.sickness.variant.rules import with_sickness_variant

_CCNL = with_sickness_variant(
    load_ccnl("metalmeccanico-artigianato"), WorkerCategory.IMPIEGATO, Permanent()
)
_START = date(2026, 1, 1)


def _treatment(
    seniority: int, *earlier: SicknessEpisode, start: date = _START
) -> CumulativeTreatment:
    work = _CCNL.work_rules
    assert work is not None
    rules = work.sickness_rules
    assert rules is not None
    assert rules.cumulation is not None
    worker = SicknessWorker(
        seniority=SeniorityFact(seniority, start, SenioritySource.PAYSLIP)
    )
    episode = SicknessEpisode("e", start, start + timedelta(days=399))
    return CumulativeTreatment(rules, rules.cumulation, episode, earlier, worker)


def _day(treatment: CumulativeTreatment, nth: int) -> tuple[bool, Decimal]:
    result = treatment.day(nth, treatment.episode.started_on + timedelta(days=nth - 1))
    return result.beyond_comporto, result.rate


@pytest.mark.parametrize(
    ("seniority", "nth", "beyond", "rate"),
    [
        (12, 60, False, "1"),
        (12, 61, False, "0.5"),
        (12, 180, False, "0.5"),
        (12, 181, True, "0"),
        (72, 90, False, "1"),
        (72, 91, False, "0.5"),
        (72, 240, False, "0.5"),
        (72, 241, True, "0"),
    ],
)
def test_one_illness(seniority: int, nth: int, beyond: bool, rate: str) -> None:
    """2 + 4 months up to 5 years, 3 + 5 above; kept 6 or 8 months."""
    got_beyond, got_rate = _day(_treatment(seniority), nth)
    assert got_beyond is beyond
    if not beyond:
        assert got_rate == Decimal(rate)


def test_the_comporto_of_several_illnesses_is_ten_months_in_24() -> None:
    """160 days in 2025 and a new illness from 1 January 2026: 300 at day 140."""
    earlier = SicknessEpisode("a", date(2025, 3, 1), date(2025, 8, 7))
    treatment = _treatment(72, earlier)
    assert not _day(treatment, 140)[0]
    assert _day(treatment, 141)[0]


def test_a_new_illness_starts_the_full_pay_anew() -> None:
    """Each illness after a day of work pays the whole pay from its first day."""
    earlier = SicknessEpisode("a", date(2025, 3, 1), date(2025, 8, 7))
    assert _day(_treatment(12, earlier), 1) == (False, Decimal(1))
