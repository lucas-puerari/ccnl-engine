"""The trattamento integrativo speciale of tourism and food service workers.

L. 199/2025 art. 1 (Gazzetta Ufficiale of 21 January 2026, page sha256
e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d):

- c. 18: "per il periodo dal 1° gennaio al 30 settembre 2026, ai lavoratori
  degli esercizi di somministrazione di alimenti e bevande [...] e ai
  lavoratori del comparto del turismo, ivi inclusi gli stabilimenti
  termali, e' riconosciuto un trattamento integrativo speciale, che non
  concorre alla formazione del reddito, pari al 15 per cento delle
  retribuzioni lorde corrisposte in relazione al lavoro notturno e alle
  prestazioni di lavoro straordinario, ai sensi del decreto legislativo 8
  aprile 2003, n. 66, effettuate nei giorni festivi";
- c. 19: private-sector workers with 2025 employment income "non superiore
  [...] a 40.000 euro";
- c. 20: paid "su richiesta del lavoratore"; c. 21: recovered by the
  withholding agent in F24 compensation.

AdE circ. 26/E/2023 par. 2 on the identical measure of 2023 (sha256
4ce411588b2ddcdaff03bbe391be17a24129108de040d6eb15a7668af2a8c7cd): "è
calcolata sulla retribuzione lorda [...] corrisposta per il lavoro straordinario
prestato nei giorni festivi e/o per il lavoro notturno": the whole gross pay
of those hours, the hour and its premium.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.regime.models import EmployerActivity, EmploymentSector
from ccnl_engine.working_time.inputs import (
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftKind,
    ShiftWorkEvent,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.decision.models import CalculationDecision
    from ccnl_engine.regime.requirement.rules import RegimeFacts

__all__ = ["SpecialSupplement", "special_supplement"]

_RATE = Decimal("0.15")
_FIRST, _LAST = date(2026, 1, 1), date(2026, 9, 30)
_INCOME_CAP = Decimal(40_000)
_ACTIVITIES = frozenset({
    EmployerActivity.FOOD_AND_BEVERAGE_SERVICE,
    EmployerActivity.TOURISM,
    EmployerActivity.THERMAL_ESTABLISHMENT,
})
_OVERTIME = frozenset({
    OvertimeKind.NIGHT,
    OvertimeKind.HOLIDAY,
    OvertimeKind.NIGHT_HOLIDAY,
})

type WorkEventOfSupplement = (
    NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent | OvertimeEvent
)


@dataclass(frozen=True)
class SpecialSupplement:
    """The supplement of one event, or why it is not computed.

    Attributes:
        reason: ``paid``, or ``activity_unknown``, ``income_unknown``,
            ``income_above_cap`` or ``base_unknown``.
        amount: 15% of ``base``, to the cent; ``None`` when not paid.
        base: Gross pay of the hours; ``None`` when not paid.
    """

    reason: str
    amount: Decimal | None = None
    base: Decimal | None = None


def _qualifies(event: object) -> bool:
    if isinstance(event, NightShiftEvent):
        return True
    if isinstance(event, HolidayWorkEvent):
        return event.kind is HolidayWorkKind.NIGHT_HOLIDAY
    if isinstance(event, ShiftWorkEvent):
        return event.kind is ShiftKind.NIGHT
    return isinstance(event, OvertimeEvent) and event.kind in _OVERTIME


def _base(
    event: WorkEventOfSupplement,
    gross: Decimal,
    decisions: Iterable[CalculationDecision],
) -> Decimal | None:
    """Return the gross pay of the hours of ``event``.

    Returns:
        The overtime amount, the hour included; for ordinary night hours,
        their premium plus the hours at the hourly base of the decision;
        ``None`` when the hours or the hourly base are not known.
    """
    if isinstance(event, OvertimeEvent):
        return gross
    rate = next(
        (
            d.inputs["hourly_base_rate"]
            for d in decisions
            if isinstance(d.inputs.get("hourly_base_rate"), Decimal)
        ),
        None,
    )
    if event.hours is None or not isinstance(rate, Decimal):
        return None
    return gross + event.hours * rate


def special_supplement(
    event: object,
    gross: Decimal,
    decisions: Iterable[CalculationDecision],
    facts: RegimeFacts,
) -> SpecialSupplement | None:
    """Return the trattamento integrativo speciale of ``event``.

    Returns:
        ``None`` when the worker did not ask for it, the employer is not a
        withholding agent, the employment is public, the activity is not
        one of c. 18, the work falls outside 1 January - 30 September 2026
        or is neither night work nor holiday overtime; otherwise the
        amount, or why it cannot be computed.
    """
    if not (
        facts.special_supplement
        and facts.withholding_agent
        and facts.sector is not EmploymentSector.PUBLIC
        and isinstance(
            event, NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent | OvertimeEvent
        )
        and _FIRST <= event.event_date <= _LAST
        and _qualifies(event)
        and (facts.activity is None or facts.activity in _ACTIVITIES)
    ):
        return None
    if facts.activity is None:
        return SpecialSupplement("activity_unknown")
    if facts.prior_income is None:
        return SpecialSupplement("income_unknown")
    if facts.prior_income > _INCOME_CAP:
        return SpecialSupplement("income_above_cap")
    base = _base(event, gross, decisions)
    if base is None:
        return SpecialSupplement("base_unknown")
    return SpecialSupplement("paid", money(base * _RATE), base)
