"""Whether the end of an employment owes the NASpI contribution, and how much.

L. 92/2012 art. 2 c. 31 charges the employer, on the end of an open-ended
employment for a cause that would give the NASpI, 41% of the monthly NASpI
maximum for each twelve months of service in the last three years; c. 32
extends it to an apprenticeship ended otherwise than by the worker.  INPS
circ. 44/2013 par. 1 leaves out resignations (but for just cause, of an
apprentice too), mutual agreements and death, and par. 2 counts a shorter
service in months, a month of at least 15 calendar days whole.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.employment.inputs import Contract
    from ccnl_engine.termination.naspi.models import NaspiDismissalRules

__all__ = ["dismissal_contribution", "is_due", "service_months"]

_WINDOW_MONTHS = 36
_MIN_DAYS = 15
_MONTHS = Decimal(12)
_CENT = Decimal("0.01")
_DAY = timedelta(days=1)


def _months_back(day: date, months: int) -> date:
    year, month = divmod(day.month - 1 - months, 12)
    year, month = day.year + year, month + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def service_months(started_on: date, ended_on: date) -> int:
    """Return the months of service in the three years before ``ended_on``.

    Returns:
        The calendar months with at least 15 days of service from the later
        of ``started_on`` and the day 36 months before ``ended_on``, at most
        36.
    """
    first = max(started_on, _months_back(ended_on, _WINDOW_MONTHS) + _DAY)
    months, cursor = 0, date(first.year, first.month, 1)
    while cursor <= ended_on:
        last = date(
            cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1]
        )
        days = (min(last, ended_on) - max(cursor, first)).days + 1
        months += days >= _MIN_DAYS
        cursor = last + _DAY
    return min(months, _WINDOW_MONTHS)


def is_due(
    cause: TerminationCause, just_cause: bool | None, contract: Contract
) -> bool | None:
    """Return whether the end of the employment owes the contribution.

    Returns:
        ``True`` on a dismissal of an open-ended employee or an apprentice,
        or on their resignation for just cause;
        ``None`` when the just cause of a resignation is not stated;
        ``False`` otherwise.
    """
    if not isinstance(contract, Permanent | Apprentice):
        return False
    if cause is TerminationCause.DISMISSAL:
        return True
    if cause is not TerminationCause.RESIGNATION:
        return False
    return just_cause


def dismissal_contribution(rules: NaspiDismissalRules, months: int) -> Decimal:
    """Return the contribution of ``months`` of service.

    INPS circ. 44/2013 note 6: the yearly amount "va diviso per 12 e il
    risultato va moltiplicato per il numero dei mesi"; its example, 483.80
    for ten months, gives 403.16, the cent cut off.

    Returns:
        The rate times the monthly maximum, to the cent, for twelve months;
        a twelfth of it for each month, the cent cut off.
    """
    yearly = money(rules.rate.value * rules.monthly_maximum.value)
    return (yearly * months / _MONTHS).quantize(_CENT, rounding=ROUND_DOWN)
