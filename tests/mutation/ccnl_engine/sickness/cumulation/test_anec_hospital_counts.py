"""Hand-computed ANEC sick pay on a EUR 100 daily wage.

After 179 ordinary days, a two-day hospital stay leaves the next ordinary
sick day at count 180 (EUR 100); without stated stays it is count 182
(EUR 50, provisional until the hospital facts are supplied).
"""

from datetime import date, timedelta
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment
from ccnl_engine.sickness.models import SicknessEpisode


def test_stated_hospital_days_do_not_exhaust_full_pay() -> None:
    """The day after a two-day stay pays EUR 100 instead of EUR 50."""
    agreement = load_ccnl("esercizi-cinematografici-anec")
    assert agreement.work_rules is not None
    rules = agreement.work_rules.sickness_rules
    assert rules is not None
    cumulation = rules.cumulation
    assert cumulation is not None
    assert cumulation.hospital_excluded_from_counts

    first = date(2025, 1, 1)
    previous = (SicknessEpisode("prior", first, first + timedelta(days=178)),)
    admission = first + timedelta(days=179)
    next_day = admission + timedelta(days=2)
    stated = SicknessEpisode(
        "stated",
        admission,
        next_day,
        hospital_stays=((admission, admission + timedelta(days=1)),),
    )
    known = CumulativeTreatment(rules, cumulation, stated, previous)
    assert known.window_days(next_day) == 180
    assert known.comporto_count(next_day) == 180
    assert known.day(3, next_day).rate * Decimal(100) == Decimal(100)

    unstated = SicknessEpisode("unstated", admission, next_day)
    unknown = CumulativeTreatment(rules, cumulation, unstated, previous)
    assert unknown.window_days(next_day) == 182
    assert unknown.day(3, next_day).rate * Decimal(100) == Decimal(50)
