"""The sick days of a month count at most one monthly pay, rounded once.

A monthly pay of 2211.43 EUR divided by 26 days: 9 days are worth
2211.43 x 9 / 26 = 765.495, 765.50 rounded half up; 17 days 2211.43 x 17 /
26 = 1445.935, 1445.94.  Rounded apart they deduct 2211.44, one cent more
than the month; rounded once on the 26 days counted, the second band is
worth 2211.43 - 765.50 = 1445.93.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.day.rules import SickDayKind, SickDaySegment
from ccnl_engine.sickness.pay.handlers import (
    EpisodePay,
    _grossed,
    _quota,
    _segment_pay,
    _within_month,
)
from ccnl_engine.sickness.term.rules import SicknessTerms

if TYPE_CHECKING:
    from ccnl_engine.sickness.day.models import SickPayRules

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


def _rules(*, net_basis: bool) -> SickPayRules:
    return cast(
        "SickPayRules", SimpleNamespace(ccnl=SimpleNamespace(net_basis=net_basis))
    )


def test_net_basis_grosses_up_the_inps_share() -> None:
    """274.11 / (1 - 0.0976) = 303.758..., 303.76; the gross basis keeps it."""
    terms = SicknessTerms(employee_rate=Decimal("0.0976"))
    share = Decimal("274.11")
    assert _grossed(share, _rules(net_basis=True), terms) == Decimal("303.76")
    assert _grossed(share, _rules(net_basis=False), terms) == share


def test_the_quota_adds_the_seniority_to_the_base() -> None:
    """13 of 26 days of 2000.00 base and 100.00 seniority: 1000.00 + 50.00."""
    chain = MonthlyPayChain(
        base=Decimal("2000.00"), seniority=Decimal("100.00"), allowances=()
    )
    assert _quota(chain, Decimal(13), _DIVISOR) == Decimal("1050.00")


def test_the_units_of_a_kind_sum_its_segments_only() -> None:
    """Carenza and the two indemnified segments are counted apart."""
    pay = EpisodePay(
        segments=(
            _segment(1, 3, SickDayKind.CARENZA),
            _segment(4, 20, SickDayKind.INDEMNIFIED),
            _segment(21, 25, SickDayKind.INDEMNIFIED),
        ),
        units=(Decimal(3), Decimal(14), Decimal(5)),
    )
    assert pay.units_of(SickDayKind.CARENZA) == Decimal(3)
    assert pay.units_of(SickDayKind.INDEMNIFIED) == Decimal(19)
    none = pay.units_of(SickDayKind.BEYOND_COMPORTO)
    assert (none, type(none)) == (Decimal(0), Decimal)


def _paid(
    kind: SickDayKind, *, inps_direct: bool = False
) -> tuple[Decimal, Decimal, Decimal]:
    segment = replace(
        _segment(4, 10, kind),
        inps_rate=Decimal("0.5"),
        inps_direct=inps_direct,
    )
    rules = (_rules(net_basis=False), SicknessTerms())
    return _segment_pay(segment, Decimal("300.00"), rules, excluded=False)


def test_the_employer_advances_the_inps_share_unless_inps_pays_it() -> None:
    """INPS 50% of 300.00: advanced, or paid by INPS directly; the top-up stays."""
    assert _paid(SickDayKind.INDEMNIFIED) == (
        Decimal("150.00"),
        Decimal("150.00"),
        Decimal(0),
    )
    assert _paid(SickDayKind.INDEMNIFIED, inps_direct=True) == (
        Decimal(0),
        Decimal("150.00"),
        Decimal(0),
    )


def test_the_carenza_is_paid_by_the_employer_alone() -> None:
    """No INPS share is advanced on the waiting days, whatever their rate."""
    assert _paid(SickDayKind.CARENZA) == (Decimal(0), Decimal(0), Decimal("300.00"))


def test_days_back_within_a_rolling_comporto_are_still_clipped() -> None:
    """Days within the comporto again after days past it still spend the month.

    A rolling comporto window can drop the sick days of old episodes, so a
    day past the comporto may be followed by days within it.
    """
    segments = (
        _segment(1, 5, SickDayKind.INDEMNIFIED),
        _segment(6, 10, SickDayKind.BEYOND_COMPORTO),
        _segment(11, 31, SickDayKind.INDEMNIFIED),
    )
    units = (Decimal(5), Decimal(4), Decimal(18))
    assert _within_month(segments, units, Decimal(10), _DIVISOR) == (
        Decimal(5),
        Decimal(4),
        Decimal(11),
    )
