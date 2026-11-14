"""Federmeccanica art. 7: 8% more past the yearly 'quote esenti'.

"Per le ore di straordinario in regime di «quote esenti» dall'accordo
preventivo eccedenti le 40 ore annue, per i lavoratori turnisti e per i
lavoratori non turnisti che lavorino in aziende con oltre 200 dipendenti,
ovvero le 48 ore annue, per i lavoratori non turnisti che lavorino in
aziende fino a 200 dipendenti, sarà corrisposta una maggiorazione
aggiuntiva pari all'8%" (ipotesi of 22 November 2025, p. 35).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import OvertimeEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.overtime.quota import (
    OvertimeExemptQuota,
    quota_hours,
    quota_premium,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_SLUG = "metalmeccanico-federmeccanica"
_DAY = date(2026, 3, 10)


def _rule() -> OvertimeExemptQuota:
    rules = load_ccnl(_SLUG).work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    rule = rules.time_supplements.overtime_exempt_quota
    assert rule is not None
    return rule


@pytest.mark.parametrize(
    ("headcount", "shift", "quota"),
    [
        (300, None, 40),
        (300, False, 40),
        (50, True, 40),
        (None, True, 40),
        (50, False, 48),
        (200, False, 48),
        (201, False, 40),
        (50, None, None),
        (None, False, None),
    ],
)
def test_the_quota_follows_shift_and_headcount(
    headcount: int | None, shift: bool | None, quota: int | None
) -> None:
    """40 for shift workers and large firms, 48 for the others, else open."""
    assert quota_hours(_rule(), headcount, shift) == quota


def test_only_the_hours_past_the_quota_take_the_premium() -> None:
    """44 earlier hours and 10 more against 48: 6 hours at 8%."""
    event = OvertimeEvent(
        _DAY,
        hours=Decimal(10),
        exempt_quota_hours_before=Decimal(44),
        in_periodic_shift=False,
    )
    premium = quota_premium(event, _rule(), 50)
    assert premium is not None
    assert premium.hours == Decimal(6)
    assert premium.multiplier == Decimal("0.08") * 6 / 10
    assert not premium.unknown


def test_hours_already_past_the_quota_all_take_it() -> None:
    """60 earlier hours against 40: the whole event is past the quota."""
    event = OvertimeEvent(_DAY, hours=Decimal(5), exempt_quota_hours_before=Decimal(60))
    premium = quota_premium(event, _rule(), 300)
    assert premium is not None
    assert premium.hours == Decimal(5)


def test_hours_within_the_quota_take_nothing() -> None:
    """10 earlier hours and 8 more stay within 40."""
    event = OvertimeEvent(_DAY, hours=Decimal(8), exempt_quota_hours_before=Decimal(10))
    premium = quota_premium(event, _rule(), 300)
    assert premium is not None
    assert premium.multiplier == 0


def test_without_the_facts_the_premium_is_unknown() -> None:
    """No earlier hours, or no shift status in a small firm."""
    rule = _rule()
    plain = OvertimeEvent(_DAY, hours=Decimal(8))
    small = OvertimeEvent(_DAY, hours=Decimal(8), exempt_quota_hours_before=Decimal(50))
    first = quota_premium(plain, rule, 300)
    second = quota_premium(small, rule, 50)
    assert first is not None
    assert second is not None
    assert first.unknown
    assert second.unknown


def test_before_the_decorrenza_or_without_a_rule_there_is_none() -> None:
    """The ipotesi runs from 22 November 2025; other CCNLs set no premium."""
    before = OvertimeEvent(
        date(2025, 11, 21), hours=Decimal(8), exempt_quota_hours_before=Decimal(50)
    )
    assert quota_premium(before, _rule(), 300) is None
    assert quota_premium(before, None, 300) is None


def _run(event: OvertimeEvent, headcount: int) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(headcount)),
            period_id=PeriodId(2026, 3),
            payment_date=date(2026, 3, 27),
            ccnl_id=_SLUG,
            level_code="D1",
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
        lim.variant == "overtime_exempt_quota_supplement" for lim in result.limitations
    )


def test_the_run_pays_the_premium_past_the_quota() -> None:
    """D1, 10 weekday hours at 25%: 125.87; 6 past 48 add 4.83, 10 past 40 add 8.05."""
    plain = _run(OvertimeEvent(_DAY, hours=Decimal(10)), 50)
    small = _run(
        OvertimeEvent(
            _DAY,
            hours=Decimal(10),
            exempt_quota_hours_before=Decimal(44),
            in_periodic_shift=False,
        ),
        50,
    )
    large = _run(
        OvertimeEvent(_DAY, hours=Decimal(10), exempt_quota_hours_before=Decimal(44)),
        300,
    )
    assert (_pay(plain), _pay(small), _pay(large)) == (
        Decimal("125.87"),
        Decimal("130.70"),
        Decimal("133.92"),
    )
    assert _limited(plain)
    assert not _limited(small)
    assert not _limited(large)
    (decision,) = (
        d for d in small.decisions if d.reason_code == "overtime_exempt_quota_premium"
    )
    assert decision.inputs["hours_past_quota"] == Decimal(6)


def test_a_caller_multiplier_is_applied_as_given() -> None:
    """An explicit multiplier prevails: no premium, no limitation."""
    event = OvertimeEvent(
        _DAY,
        hours=Decimal(10),
        multiplier=Decimal("1.5"),
        exempt_quota_hours_before=Decimal(60),
    )
    result = _run(event, 300)
    assert not any(
        d.reason_code == "overtime_exempt_quota_premium" for d in result.decisions
    )
    assert not _limited(result)
