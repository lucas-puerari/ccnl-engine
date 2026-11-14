"""Credit and pay the permits of a programme of flexibility.

The weeks of a run credit the ``flessibilita`` bucket of their programme
year (the year the programme started, ``EmployerProfile.
flexibility_programme_month``); the hours left are paid with the overtime
premium of the CCNL on the pay of the month ``payout_months_after`` the
last month of the programme year, and at the end of the employment.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.leave.balance.models import LeaveAccount
from ccnl_engine.leave.flexibility.inputs import FlexibilityWeekEvent
from ccnl_engine.leave.models import PermitDeadline
from ccnl_engine.leave.settlement.services import settle_leave
from ccnl_engine.leave.types import LeaveBucket

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.leave.flexibility.models import FlexibilityPermits
    from ccnl_engine.leave.models import LeaveRules
    from ccnl_engine.leave.settlement.models import LeaveSettlement, SettlementTerms

__all__ = [
    "accrue_weeks",
    "flexibility_payout",
    "flexibility_premiums",
    "payout_month",
    "programme_year",
]

_BUCKET = LeaveBucket.FLESSIBILITA
_TWELVE = Decimal(12)


def programme_year(day: date, month: int | None) -> int:
    """Return the year of the programme ``day`` falls in.

    Returns:
        The year of the last start of the programme (``month``, January
        when unstated) on or before ``day``.
    """
    start = month or 1
    return day.year if day.month >= start else day.year - 1


def payout_month(year: int, month: int, after: int) -> tuple[int, int]:
    """Return the year and month whose pay settles a programme of ``year``.

    Returns:
        The month ``after`` the last month of the programme started in
        ``month`` of ``year``.
    """
    index = year * 12 + month - 1 + 11 + after
    return index // 12, index % 12 + 1


def accrue_weeks(
    account: LeaveAccount,
    flex: FlexibilityPermits,
    events: Iterable[object],
    month: int | None,
) -> LeaveAccount:
    """Return ``account`` with the permits the weeks of the run earn.

    Returns:
        The account with each week's hours credited to its programme year;
        the balance is inexact when the programme month is unstated.
    """
    for event in events:
        if not isinstance(event, FlexibilityWeekEvent):
            continue
        hours = flex.hours_for(event.hours_worked)
        year = programme_year(event.event_date, month)
        account = account.credited(
            _BUCKET, year, hours * _TWELVE, exact=month is not None
        )
    return account


def flexibility_premiums(
    ccnl: CCNL, rules: LeaveRules | None, day: date
) -> dict[LeaveBucket, Decimal]:
    """Return the premium the hours of flexibility left are paid with.

    Returns:
        ``{flessibilita: rate}`` of the overtime band the rules name, in
        force on ``day``; empty without flexibility or that band.
    """
    flex = None if rules is None else rules.flexibility
    work = ccnl.work_rules
    if flex is None or work is None or work.time_supplements is None:
        return {}
    bands = work.time_supplements.overtime_bands
    band = next((b for b in bands if b.code == flex.premium_band), None)
    return {} if band is None else {_BUCKET: Decimal(band.rate.value_at(day))}


def flexibility_payout(
    account: LeaveAccount,
    flex: FlexibilityPermits,
    terms: SettlementTerms,
    month: int | None,
    period: tuple[int, int],
) -> LeaveSettlement | None:
    """Pay the hours of the programmes whose payout month is ``period``.

    Returns:
        The settlement of those balances, at the hourly quota with the
        premium of ``terms``; ``None`` when none is due or the programme
        month is unstated.
    """
    if month is None:
        return None
    due = tuple(
        b
        for b in account.unsettled()
        if b.bucket is _BUCKET
        and payout_month(b.year, month, flex.payout_months_after) == period
    )
    if not due:
        return None
    deadline = PermitDeadline(
        carry_until_month=period[1],
        buckets=(_BUCKET,),
        permits_hourly=True,
        provenance=flex.provenance,
    )
    settlement = settle_leave(
        LeaveAccount(due, account.known), replace(terms, deadline=deadline)
    )
    return replace(
        settlement, account=account.with_balances(*settlement.account.balances)
    )
