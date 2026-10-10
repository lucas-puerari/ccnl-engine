"""The sick days of a month count at most one monthly pay, rounded once.

A monthly pay of 2211.43 EUR divided by 26 days: 9 days are worth
2211.43 x 9 / 26 = 765.495, 765.50 rounded half up; 17 days 2211.43 x 17 /
26 = 1445.935, 1445.94.  Rounded apart they deduct 2211.44, one cent more
than the month; rounded once on the 26 days counted, the second band is
worth 2211.43 - 765.50 = 1445.93.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.amount.types_chain import MonthlyPayChain
from ccnl_engine.payroll.sickness.handlers_pay import (
    _quota,
    _within_month,
)
from ccnl_engine.payroll.sickness.rules_day import SickDayKind, SickDaySegment

_CHAIN = MonthlyPayChain(base=Decimal("2211.43"), seniority=Decimal(0), allowances=())
_DIVISOR = Decimal(26)


def _segment(first: int, last: int, kind: SickDayKind) -> SickDaySegment:
    return SickDaySegment(
        first=date(2026, 7, first),
        last=date(2026, 7, last),
        first_index=first,
        kind=kind,
        inps_rate=Decimal(0),
        worker_rate=Decimal(1),
    )


def test_bands_rounded_apart_exceed_the_month() -> None:
    """9 and 17 days of 26, each rounded half up, add up to 2211.44."""
    nine = _quota(_CHAIN, Decimal(9), _DIVISOR)
    seventeen = _quota(_CHAIN, Decimal(17), _DIVISOR)
    assert (nine, seventeen) == (Decimal("765.50"), Decimal("1445.94"))
    assert nine + seventeen == Decimal("2211.44")


def test_bands_rounded_once_add_up_to_the_month() -> None:
    """The 17 days are the 26 counted less the 9 before: 1445.93."""
    nine = _quota(_CHAIN, Decimal(9), _DIVISOR)
    month = _quota(_CHAIN, _DIVISOR, _DIVISOR)
    assert month == Decimal("2211.43")
    assert month - nine == Decimal("1445.93")


def test_units_past_the_month_are_dropped() -> None:
    """13 days already counted by an earlier episode leave 13 of 26."""
    segments = (
        _segment(16, 18, SickDayKind.CARENZA),
        _segment(19, 31, SickDayKind.INDEMNIFIED),
    )
    units = (Decimal(3), Decimal(11))
    assert _within_month(segments, units, Decimal(13), _DIVISOR) == (
        Decimal(3),
        Decimal(10),
    )


def test_days_past_the_comporto_keep_their_units() -> None:
    """They are not deducted, so they neither spend nor need the month left."""
    segments = (
        _segment(1, 10, SickDayKind.INDEMNIFIED),
        _segment(11, 31, SickDayKind.BEYOND_COMPORTO),
    )
    units = (Decimal(9), Decimal(17))
    assert _within_month(segments, units, Decimal(20), _DIVISOR) == (
        Decimal(6),
        Decimal(17),
    )
