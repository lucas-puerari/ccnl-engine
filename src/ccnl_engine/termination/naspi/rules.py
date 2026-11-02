"""Whether the end of an employment owes the NASpI contribution, and how much.

L. 92/2012 art. 2 c. 31 charges the employer, on the end of an open-ended
employment for a cause that would give the NASpI, 41% of the monthly NASpI
maximum for each twelve months of service in the last three years; c. 32
extends it to an apprenticeship ended otherwise than by the worker.  INPS
circ. 44/2013 par. 1 leaves out resignations (but for just cause, of an
apprentice too), mutual agreements and death, and par. 2 counts a shorter
service in months, a month of at least 15 calendar days whole.  The
cases the caller states (:class:`~ccnl_engine.employment.period.inputs.NaspiCase`)
owe it on a resignation in the maternity protection and on the mutual
agreements of par. 1, and leave it out on the changes of contractor and
site closures of c. 34; a collective dismissal takes the 82% of L.
205/2017 art. 1 c. 137 when the employer owes the CIGS contribution, three
times without union agreement (c. 35).
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.employment.period.inputs import (
    CollectiveDismissal,
    NaspiCase,
    TerminationCause,
)
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.employment.inputs import Contract
    from ccnl_engine.termination.naspi.models import NaspiDismissalRules

__all__ = [
    "case_inputs",
    "contribution_terms",
    "dismissal_contribution",
    "is_due",
    "service_months",
]

_WINDOW_MONTHS = 36
_MIN_DAYS = 15
_MONTHS = Decimal(12)
_CENT = Decimal("0.01")
_DAY = timedelta(days=1)
_ONCE = Decimal(1)
_OWED = frozenset({
    NaspiCase.PROTECTED_MATERNITY,
    NaspiCase.CONCILIATION,
    NaspiCase.TRANSFER,
})
_EXEMPT = frozenset({NaspiCase.CONTRACTOR_CHANGE, NaspiCase.SITE_CLOSURE})


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
    cause: TerminationCause,
    just_cause: bool | None,
    contract: Contract,
    case: NaspiCase | CollectiveDismissal | None = None,
) -> bool | None:
    """Return whether the end of the employment owes the contribution.

    Returns:
        ``True`` on a dismissal of an open-ended employee or an apprentice,
        on their resignation for just cause, or on a case that owes it;
        ``False`` on a case that leaves it out;
        ``None`` when the just cause of a resignation is not stated;
        ``False`` otherwise.
    """
    if not isinstance(contract, Permanent | Apprentice):
        return False
    if case in _OWED:
        return True
    if case in _EXEMPT:
        return False
    if cause is TerminationCause.DISMISSAL:
        return True
    if cause is not TerminationCause.RESIGNATION:
        return False
    return just_cause


def contribution_terms(
    rules: NaspiDismissalRules, case: NaspiCase | CollectiveDismissal | None
) -> tuple[Decimal, Decimal]:
    """Return the rate and the multiplier of the contribution of ``case``.

    Returns:
        The 41% once; for a collective dismissal the 82% of an employer
        owing the CIGS contribution, and three times without union
        agreement.
    """
    if not isinstance(case, CollectiveDismissal):
        return rules.rate.value, _ONCE
    rate = rules.collective_rate if case.cigs_employer else rules.rate
    times = _ONCE if case.union_agreement else rules.no_agreement_multiplier.value
    return rate.value, times


def dismissal_contribution(
    rules: NaspiDismissalRules,
    months: int,
    case: NaspiCase | CollectiveDismissal | None = None,
) -> Decimal:
    """Return the contribution of ``months`` of service.

    INPS circ. 44/2013 note 6: the yearly amount "va diviso per 12 e il
    risultato va moltiplicato per il numero dei mesi"; its example, 483.80
    for ten months, gives 403.16, the cent cut off.  INPS msg. 594/2018
    par. 4: 990.68 for twelve months at 82% of 1208.15, "moltiplicata per
    tre volte" without union agreement.

    Returns:
        The rate times the monthly maximum, to the cent, for twelve months;
        a twelfth of it for each month, the cent cut off; times the
        multiplier of the case.
    """
    rate, times = contribution_terms(rules, case)
    yearly = money(rate * rules.monthly_maximum.value)
    return (yearly * months / _MONTHS).quantize(_CENT, rounding=ROUND_DOWN) * times


def case_inputs(case: NaspiCase | CollectiveDismissal | None) -> dict[str, str]:
    """Return the inputs of the decision that name the case of the end.

    Returns:
        Nothing for an unstated case; the case, or for a collective
        dismissal its union agreement and CIGS flags.
    """
    if case is None:
        return {}
    if isinstance(case, CollectiveDismissal):
        return {
            "naspi_case": "collective_dismissal",
            "union_agreement": str(case.union_agreement).lower(),
            "cigs_employer": str(case.cigs_employer).lower(),
        }
    return {"naspi_case": case.value}
