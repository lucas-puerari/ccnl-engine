"""The diaria of UNEBA art. 58: twice the daily pay of art. 42.

'una diaria non inferiore al doppio della retribuzione giornaliera di cui
all'art. 42; qualora non vi sia pernottamento fuori sede la diaria verrà
ridotta di un terzo': the global monthly pay over 26, times two, less a
third without an overnight stay.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_the_diaria_is_twice_the_daily_pay() -> None:
    """Rate 2 on the pay over 26, a third off without overnight."""
    rules = load_ccnl("uneba-uneba").work_rules
    assert rules is not None
    travel = rules.travel_allowance
    assert travel is not None
    share = travel.daily_share
    assert share is not None
    assert (share.rate, share.base, share.divisor) == (Decimal(2), "pay", Decimal(26))
    assert share.no_overnight_discount == Decimal("0.3333333333")
    assert travel.long_mission_discount == Decimal("0.10")
