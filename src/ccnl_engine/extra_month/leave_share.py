"""The share of the extra months a CCNL pays for the compulsory maternity leave.

D.Lgs. 151/2001 art. 22 c. 3 counts the compulsory leave for the 13th and the
other extra months, and the employer pays the whole rateo.  A CCNL may limit it
to a share, the INPS indemnity holding the rest in its base (art. 23 c. 2):
ANASTE art. 45 c. 23, "la 13° mensilità limitatamente all'aliquota
corrispondente al 20% della retribuzione".  The months the leave alone makes
accrue are then paid at that share; the share scales the fraction of the
rateo, as the change of hours does.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.inputs import MaternityLeaveEvent

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.fact.inputs import WorkPattern
    from ccnl_engine.event.facade import WorkEvent
    from ccnl_engine.extra_month.models import ExtraMonthAccrual

__all__ = ["LeaveShare", "leave_share", "maternity_share", "with_leave_share"]


def _days(events: Iterable[WorkEvent]) -> frozenset[date]:
    """Return the days of the compulsory maternity leaves of ``events``.

    Returns:
        Every calendar day of each :class:`MaternityLeaveEvent`.
    """
    return frozenset(
        event.started_on + timedelta(days=i)
        for event in events
        if isinstance(event, MaternityLeaveEvent)
        for i in range((event.ended_on - event.started_on).days + 1)
    )


@dataclass(frozen=True)
class LeaveShare:
    """The days of the compulsory leave and the share of the rateo they accrue.

    Attributes:
        days: Days of the compulsory maternity leave.
        share: Share of the rateo the employer pays for the months they alone
            make accrue.
    """

    days: frozenset[date]
    share: Decimal


def maternity_share(ccnl: CCNL) -> Decimal | None:
    """Return the share of the rateo the CCNL pays for the compulsory leave.

    Returns:
        ``MaternityRules.extra_month_share``, ``None`` for the whole rateo.
    """
    rules = ccnl.work_rules
    absence = None if rules is None else rules.insured_absence
    maternity = None if absence is None else absence.maternity
    return None if maternity is None else maternity.extra_month_share


def leave_share(
    share: Decimal | None, events: Iterable[WorkEvent]
) -> LeaveShare | None:
    """Return the leave days of ``events`` with the share they accrue.

    Returns:
        ``None`` for the whole rateo or when no event is a compulsory
        maternity leave.
    """
    days = _days(events) if share is not None else frozenset()
    if share is None or not days:
        return None
    return LeaveShare(days, share)


def with_leave_share(
    accrual: ExtraMonthAccrual,
    non_accruing: frozenset[date],
    share: LeaveShare | None,
    pattern: WorkPattern | None = None,
) -> ExtraMonthAccrual:
    """Return ``accrual`` with the months the leave alone accrues at the share.

    Args:
        accrual: The rateo, counted with ``non_accruing``.
        non_accruing: Days that accrue nothing, as ``accrual`` was counted.
        share: The leave days and their share; ``None`` leaves it unchanged.
        pattern: Work pattern whose idle days accrue nothing.

    Returns:
        ``accrual`` with its scale lowered by the part of the accrued months
        that only the leave days qualify, paid at the share.
    """
    if share is None or not accrual.accrued:
        return accrual
    window, ended_on, rule = accrual.window, accrual.ended_on, accrual.rule
    idle = (
        frozenset() if pattern is None else pattern.idle_days(window.start, window.end)
    )
    without = non_accruing | idle | share.days
    kept = rule.qualifying_months(
        window, ended_on=ended_on, non_accruing_days=without
    ) + rule.day_units(window, ended_on=ended_on, non_accruing_days=without)
    if kept == accrual.accrued:
        return accrual
    paid = kept + (accrual.accrued - kept) * share.share
    return replace(accrual, scale=accrual.scale * paid / accrual.accrued)
