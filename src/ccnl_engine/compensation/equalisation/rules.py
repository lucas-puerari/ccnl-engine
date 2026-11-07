"""The elemento perequativo a run pays, once a year.

A CCNL with an :class:`~.models.EqualisationElement` owes it, with the
regular pay of its month, to the worker in service on 1 January of the
year, for the months of the year before with more than 15 days of service
over twelve.  A termination run of that year before its month pays it with
the final settlement ("all'atto della liquidazione delle competenze"), so a
worker who leaves before June is paid it once.

The firm must have no second-level bargaining with economic content:
``EmployerProfile.second_level_premium`` false and no
``EmployerProfile.second_level_elements``; the flag not stated, the run
leaves it out and names the missing fact.  The pay above the CCNL of the
year before reduces it "fino a concorrenza": the engine reads it from the
individual elements of the run (``Employment.individual_elements``), each
monthly amount, at the part-time fraction, for each month served in the
year before.  It is paid as an ordinary bonus
(:class:`~ccnl_engine.variable_pay.inputs.BonusEvent`): in the INPS base,
taxed with the run as income of its year, out of the TFR base.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.una_tantum.rules import _months
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.run.models import RunKind
from ccnl_engine.variable_pay.inputs import BonusEvent

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.equalisation.models import EqualisationElement
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = ["EqualisationOutcome", "equalisation_outcome"]

_MONTHS = Decimal(12)


@dataclass(frozen=True, slots=True)
class EqualisationOutcome:
    """What a run does with the elemento perequativo.

    Attributes:
        events: The bonus the run pays, empty when it pays none.
        unknown: The code of the element the run leaves out because the
            employer does not state whether it has second-level bargaining.
    """

    events: tuple[BonusEvent, ...] = ()
    unknown: str | None = None


def _pays(
    element: EqualisationElement, request: PeriodCalculationRequest, kind: RunKind
) -> bool:
    """Return whether the run of ``request`` is the one that pays ``element``.

    Returns:
        ``True`` for the regular run of its month and a termination run of
        an earlier month of the year.
    """
    month = request.period_id.month
    if kind is RunKind.REGULAR:
        return month == element.paid_in_month
    return kind is RunKind.TERMINATION and month < element.paid_in_month


def _served(element: EqualisationElement, request: PeriodCalculationRequest) -> int:
    """Return the months of the year before served, nought when not owed.

    Returns:
        The months with more than 15 days of service in the year before,
        ``0`` when the worker was not in service on 1 January of the year
        or the employment period is not stated.
    """
    period, year = request.employment_period, request.period_id.year
    january = date(year, 1, 1)
    if period is None or period.started_on > january:
        return 0
    if period.ended_on is not None and period.ended_on < january:
        return 0
    first = max(period.started_on, date(year - 1, 1, 1))
    return len(_months(first, date(year - 1, 12, 31), element.month_min_days))


def _ratio(request: PeriodCalculationRequest) -> Decimal:
    weekly, full = request.weekly_hours, request.full_time_weekly_hours
    if weekly is None or full is None or weekly.value >= full.value:
        return Decimal(1)
    return weekly.value / full.value


def _amount(
    element: EqualisationElement, request: PeriodCalculationRequest, months: int
) -> Decimal:
    """Return the element owed for ``months`` net of the pay above the CCNL.

    Returns:
        The yearly amount over twelve for each month, less the individual
        elements of the run paid over the same months, not below zero.
    """
    owed = element.yearly * months / _MONTHS
    above = sum(
        (e.monthly * months for e in request.individual_elements), Decimal(0)
    ) * _ratio(request)
    return money(max(owed - above, Decimal(0)))


def equalisation_outcome(
    request: PeriodCalculationRequest, ccnl: CCNL, kind: RunKind
) -> EqualisationOutcome:
    """Return the elemento perequativo the run pays or leaves out.

    Returns:
        The outcome: the bonus when owed and the firm states no second-level
        bargaining, the code of the element when the firm does not say.
    """
    element = ccnl.parameters.equalisation_element
    if element is None or not _pays(element, request, kind):
        return EqualisationOutcome()
    employer = request.employer
    if employer.second_level_premium or employer.second_level_elements:
        return EqualisationOutcome()
    months = _served(element, request)
    if not months:
        return EqualisationOutcome()
    if employer.second_level_premium is None:
        return EqualisationOutcome(unknown=element.code)
    amount = _amount(element, request, months)
    if not amount:
        return EqualisationOutcome()
    paid = date(request.period_id.year, request.period_id.month, 1)
    return EqualisationOutcome(events=(BonusEvent(paid, amount),))
