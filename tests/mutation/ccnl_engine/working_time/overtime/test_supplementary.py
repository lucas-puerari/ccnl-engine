"""Part-time supplementary hours past a yearly share of the agreed hours.

Federmeccanica (CCNL 5 February 2021, p. 58): 10% up to 50% of the normal
annual part-time hours, 20% past it; Logistica Confetra art. 56 cc. 16-17:
18% up to 30% of the agreed hours, 40% past it.  With 1040 agreed hours
the shares end at 520 and 312 hours.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.overtime.supplementary import (
    SupplementaryExcess,
    excess_rate,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_DAY = date(2026, 3, 10)
_ANNUAL = Decimal(1040)
_SUPPLEMENTARY = OvertimeKind.SUPPLEMENTARY


def _rule(slug: str) -> SupplementaryExcess:
    rules = load_ccnl(slug).work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    rule = rules.time_supplements.supplementary_excess
    assert rule is not None
    return rule


def _event(before: Decimal | None, annual: Decimal | None = _ANNUAL) -> OvertimeEvent:
    return OvertimeEvent(
        _DAY,
        hours=Decimal(10),
        kind=_SUPPLEMENTARY,
        supplementary_hours_before=before,
        agreed_annual_hours=annual,
    )


@pytest.mark.parametrize(
    ("slug", "before", "past"),
    [
        ("metalmeccanico-federmeccanica", Decimal(500), Decimal(0)),
        ("metalmeccanico-federmeccanica", Decimal(515), Decimal(5)),
        ("metalmeccanico-federmeccanica", Decimal(600), Decimal(10)),
        ("logistica-trasporto-confetra", Decimal(300), Decimal(0)),
        ("logistica-trasporto-confetra", Decimal(310), Decimal(8)),
    ],
)
def test_only_the_hours_past_the_share_take_the_higher_rate(
    slug: str, before: Decimal, past: Decimal
) -> None:
    """The hours of the event beyond the share of the agreed annual hours."""
    excess = excess_rate(_event(before), _rule(slug))
    assert excess is not None
    assert excess.hours == past
    assert not excess.unknown


def test_without_the_facts_the_split_is_unknown() -> None:
    """No earlier hours or no annual hours: the split cannot be made."""
    rule = _rule("logistica-trasporto-confetra")
    for event in (_event(None), _event(Decimal(10), None)):
        excess = excess_rate(event, rule)
        assert excess is not None
        assert excess.unknown


def test_other_overtime_or_dates_are_not_supplementary() -> None:
    """Weekday overtime, a CCNL without the clause, a day before it."""
    rule = _rule("logistica-trasporto-confetra")
    weekday = OvertimeEvent(
        _DAY, hours=Decimal(2), supplementary_hours_before=Decimal(0)
    )
    early = OvertimeEvent(date(2024, 12, 31), hours=Decimal(2), kind=_SUPPLEMENTARY)
    assert excess_rate(weekday, rule) is None
    assert excess_rate(_event(Decimal(0)), None) is None
    assert excess_rate(early, rule) is None


def _run(slug: str, level: str, event: OvertimeEvent) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(2026, 3),
            payment_date=date(2026, 3, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=PeriodState.zero(),
            events=(event,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _pay(result: PeriodResult) -> Decimal:
    (amount,) = (i.amount for i in result.pay_items if i.item_id.endswith("_evt0"))
    return amount


def _limited(result: PeriodResult) -> bool:
    return any(
        lim.variant == "part_time_supplementary_rate" for lim in result.limitations
    )


def test_logistica_pays_forty_percent_past_the_share() -> None:
    """Level 3, 10 hours: 136.74 at 18% (hourly 11.588); past 312 hours 162.24."""
    plain = _run("logistica-trasporto-confetra", "3", _event(None))
    past = _run("logistica-trasporto-confetra", "3", _event(Decimal(500)))
    assert (_pay(plain), _pay(past)) == (Decimal("136.74"), Decimal("162.24"))
    assert _limited(plain)
    assert not _limited(past)


def test_federmeccanica_splits_an_event_crossing_the_share() -> None:
    """D1 (hourly 10.0695), 10 hours at 10%: 110.76; 5 past 520 at 20%: 115.80."""
    within = _run("metalmeccanico-federmeccanica", "D1", _event(Decimal(500)))
    crossing = _run("metalmeccanico-federmeccanica", "D1", _event(Decimal(515)))
    assert (_pay(within), _pay(crossing)) == (Decimal("110.76"), Decimal("115.80"))
    (decision,) = (
        d
        for d in crossing.decisions
        if d.reason_code == "part_time_supplementary_excess"
    )
    assert decision.inputs["hours_past_threshold"] == Decimal(5)


def test_a_caller_multiplier_is_applied_as_given() -> None:
    """An explicit multiplier prevails: no split, no limitation."""
    event = OvertimeEvent(
        _DAY, hours=Decimal(10), kind=_SUPPLEMENTARY, multiplier=Decimal("1.3")
    )
    result = _run("logistica-trasporto-confetra", "3", event)
    assert not _limited(result)
    assert not any(
        d.reason_code == "part_time_supplementary_excess" for d in result.decisions
    )
