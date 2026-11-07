"""Edilizia ANCE impiegati, art. 66 (CCNL 2010, PDF p. 78), per illness.

Up to two years of seniority six months in full; from two to six years
nine months, the last three at 50%; over six years twelve months, three at
75% and three at 50%.  Several illnesses keep the job 9, 12 or 15 months in
30.  Months of 30 days.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.models import SicknessEpisode

_START = date(2026, 1, 1)


def _treatment(seniority: int, *earlier: SicknessEpisode) -> CumulativeTreatment:
    work = load_ccnl("edilizia-ance-impiegati").work_rules
    assert work is not None
    rules = work.sickness_rules
    assert rules is not None
    assert rules.cumulation is not None
    worker = SicknessWorker(
        seniority=SeniorityFact(seniority, _START, SenioritySource.PAYSLIP)
    )
    episode = SicknessEpisode("e", _START, _START + timedelta(days=499))
    return CumulativeTreatment(rules, rules.cumulation, episode, earlier, worker)


def _day(treatment: CumulativeTreatment, nth: int) -> tuple[bool, Decimal]:
    result = treatment.day(nth, _START + timedelta(days=nth - 1))
    return result.beyond_comporto, result.rate


@pytest.mark.parametrize(
    ("seniority", "nth", "beyond", "rate"),
    [
        (24, 180, False, "1"),
        (24, 181, True, "0"),
        (25, 180, False, "1"),
        (25, 181, False, "0.5"),
        (25, 270, False, "0.5"),
        (25, 271, True, "0"),
        (73, 181, False, "0.75"),
        (73, 270, False, "0.75"),
        (73, 271, False, "0.5"),
        (73, 360, False, "0.5"),
        (73, 361, True, "0"),
    ],
)
def test_one_illness(seniority: int, nth: int, beyond: bool, rate: str) -> None:
    """The schedule of one illness by seniority ('fino a due anni compiuti')."""
    got_beyond, got_rate = _day(_treatment(seniority), nth)
    assert got_beyond is beyond
    if not beyond:
        assert got_rate == Decimal(rate)


def test_several_illnesses_keep_the_job_nine_months_in_thirty() -> None:
    """150 days in 2025 and a new illness: 270 in 30 months at day 120."""
    earlier = SicknessEpisode("a", date(2025, 3, 1), date(2025, 7, 28))
    treatment = _treatment(12, earlier)
    assert _day(treatment, 120) == (False, Decimal(1))
    assert _day(treatment, 121)[0]
