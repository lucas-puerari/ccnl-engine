"""The multi-week hours from the 81st: Federmeccanica art. 5, 8 points more.

"Ciascuna delle suddette maggiorazioni, a partire dalla 81esima ora, saranno
elevate nella misura onnicomprensiva dell'8%" (renewal of 22 November 2025,
p. 32), read as 8 points: 15% to 23%.  D1, hourly 10.0695, 10 hours.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.multiweek import with_multiweek_premium
from tests.mutation.ccnl_engine.working_time.overtime.test_supplementary import (
    _pay,
    _run,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_SLUG = "metalmeccanico-federmeccanica"
_DAY = date(2026, 3, 10)


def _event(
    before: Decimal | None,
    kind: OvertimeKind = OvertimeKind.MULTIWEEK,
    multiplier: Decimal | None = None,
) -> OvertimeEvent:
    return OvertimeEvent(
        _DAY,
        hours=Decimal(10),
        kind=kind,
        multiweek_hours_before=before,
        multiplier=multiplier,
    )


def _unknown(result: PeriodResult) -> bool:
    return any(i.code == "overtime_multiweek_hours_unknown" for i in result.issues)


@pytest.mark.parametrize(
    ("before", "kind", "pay"),
    [
        (Decimal(70), OvertimeKind.MULTIWEEK, Decimal("15.10")),
        (Decimal(75), OvertimeKind.MULTIWEEK, Decimal("19.13")),
        (Decimal(80), OvertimeKind.MULTIWEEK, Decimal("23.16")),
        (Decimal(100), OvertimeKind.MULTIWEEK_SATURDAY, Decimal("33.23")),
        (Decimal(100), OvertimeKind.MULTIWEEK_SUDDEN, Decimal("28.19")),
        (Decimal(100), OvertimeKind.MULTIWEEK_SUDDEN_SATURDAY, Decimal("38.26")),
    ],
)
def test_the_hours_from_the_81st_take_8_points_more(
    before: Decimal, kind: OvertimeKind, pay: Decimal
) -> None:
    """Up to 80 hours 15%; 5 of 10 past it 15.10 + 4.03; all past 23%."""
    result = _run(_SLUG, "D1", _event(before, kind))

    assert _pay(result) == pay
    assert not _unknown(result)


def test_the_decision_shows_the_hours_past_the_threshold() -> None:
    """75 earlier hours and 10 now: 5 past 80, at 8 points."""
    result = _run(_SLUG, "D1", _event(Decimal(75)))

    (decision,) = (
        d
        for d in result.decisions
        if d.reason_code == "overtime_multiweek_excess_premium"
    )
    assert (
        decision.inputs["hours_before"],
        decision.inputs["threshold_hours"],
        decision.inputs["hours_past_threshold"],
        decision.inputs["rate"],
        decision.amount,
    ) == (Decimal(75), Decimal(80), Decimal(5), Decimal("0.08"), Decimal("19.13"))
    assert decision.rule.endswith("work_rules.time_supplements.multiweek_excess")


def test_without_the_earlier_hours_the_base_band_and_a_missing_fact() -> None:
    """The hours of the schedule are a fact of the timesheet."""
    result = _run(_SLUG, "D1", _event(None))

    assert _pay(result) == Decimal("15.10")
    assert _unknown(result)
    (issue,) = (
        i for i in result.issues if i.code == "overtime_multiweek_hours_unknown"
    )
    assert issue.fact == "multiweek_hours_before"


def test_a_caller_multiplier_and_other_overtime_are_left_alone() -> None:
    """A stated multiplier prevails; weekday overtime is not multi-week."""
    stated = _run(_SLUG, "D1", _event(None, multiplier=Decimal("0.5")))
    weekday = _run(_SLUG, "D1", _event(Decimal(100), OvertimeKind.WEEKDAY))

    assert not _unknown(stated)
    assert not _unknown(weekday)
    assert not any(
        d.reason_code == "overtime_multiweek_excess_premium"
        for d in (*stated.decisions, *weekday.decisions)
    )


def test_a_ccnl_without_the_clause_pays_no_excess() -> None:
    """Bands without the clause leave the multi-week event as paid."""
    event = _event(Decimal(100))
    paid = _event(Decimal(100), multiplier=Decimal("0.15"))
    assert with_multiweek_premium(event, paid, CCNLOvertimeBands()) == (
        paid,
        None,
        None,
    )


def test_before_the_renewal_there_is_no_excess() -> None:
    """The clause is in force from 22 November 2025."""
    bands = CCNLOvertimeBands.of(load_ccnl(_SLUG), 2025, "D1")
    early = OvertimeEvent(
        date(2025, 11, 21), hours=Decimal(10), kind=OvertimeKind.MULTIWEEK
    )
    paid = OvertimeEvent(
        early.event_date, hours=Decimal(10), kind=early.kind, multiplier=Decimal("0.15")
    )
    assert with_multiweek_premium(early, paid, bands) == (paid, None, None)
