"""Supplement of ordinary night, holiday and shift hours from the CCNL band.

A night, holiday or shift event without ``supplement_amount`` is paid
``rate * hours * hourly base``: the band of its work in
``work_rules.time_supplements.supplement_bands`` and the hourly base of
:mod:`~ccnl_engine.working_time.hourly.policies`.  The band is the one in
force on the event date, of the worker's level, and of a role the worker
holds; without such a role, the band that names none.  When a CCNL has a
band reserved to a role and the request does not state the roles, the band
cannot be chosen.

The engine posts the supplement (the maggiorazione) only.  A band whose
CCNL also pays the hours themselves on top of the monthly pay, or whose text
does not settle it, makes the run provisional with issue
``supplement_hours_not_posted``: those hours are ordinary pay, with TFR, the
engine does not post.

A CCNL without a band of the work is not derived: the caller states the
amount.  The bundle leaves out a band when its rate depends on facts the
request does not carry (a night window the company fixes, the shift column
of the metalmeccanici) or when the text is unconfirmed; the coverage notes
of the CCNL say which.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    NightShiftEvent,
    ShiftWorkEvent,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.working_time.hourly.policies import BASE_PATH, reject_underived
from ccnl_engine.working_time.inputs import ShiftKind
from ccnl_engine.working_time.models import SupplementWork

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.working_time.hourly.policies import HourlyBase, HourlyTerms
    from ccnl_engine.working_time.models import SupplementBand

__all__ = [
    "HOURS_NOT_POSTED",
    "SUPPLEMENT_APPLIED",
    "SupplementPay",
    "resolve_supplement",
    "supplement_rule",
    "work_of",
]

#: Reason of the decision of a supplement derived from the CCNL band.
SUPPLEMENT_APPLIED = "ccnl_supplement_applied"
#: Issue of a band whose hours themselves the engine does not post.
HOURS_NOT_POSTED = "supplement_hours_not_posted"

type SupplementEvent = NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent

_FEATURES: dict[type, str] = {
    NightShiftEvent: "night_work",
    HolidayWorkEvent: "holiday_work",
    ShiftWorkEvent: "shift_work",
}
_SHIFTS = {
    ShiftKind.DAY: SupplementWork.DAY_SHIFT,
    ShiftKind.NIGHT: SupplementWork.NIGHT_SHIFT,
}
_PAID_APART = {True: "yes", False: "no", None: "unconfirmed"}


def work_of(event: SupplementEvent) -> SupplementWork | None:
    """Return the work a supplement event pays.

    Returns:
        Night work, the holiday work of its kind, or the shift of its kind;
        ``None`` for a shift event that states no kind.
    """
    if isinstance(event, NightShiftEvent):
        return SupplementWork.NIGHT
    if isinstance(event, HolidayWorkEvent):
        return SupplementWork(event.kind.value)
    return None if event.kind is None else _SHIFTS[event.kind]


def supplement_rule(terms: HourlyTerms, band: SupplementBand) -> str:
    """Return the rule identifier of ``band``.

    Returns:
        ``<ruleset>:work_rules.time_supplements.supplement_bands[<code>]``.
    """
    return terms.rule_of(f"work_rules.time_supplements.supplement_bands[{band.code}]")


@dataclass(frozen=True)
class SupplementPay:
    """The supplement of an event and what it is computed from.

    Attributes:
        amount: ``rate * hours * hourly base``, rounded to the cent.
        band: The CCNL band applied.
        rate: Its rate on the event date.
        hours: Hours of the event.
        base: The hourly base.
    """

    amount: Decimal
    band: SupplementBand
    rate: Decimal
    hours: Decimal
    base: HourlyBase


def _in_force(
    terms: HourlyTerms, work: SupplementWork, day: date
) -> list[tuple[SupplementBand, Decimal]]:
    """Return the bands of ``work`` for the worker's level in force on ``day``.

    Returns:
        Each band with its rate on ``day``.
    """
    supplements = terms.supplements
    bands = () if supplements is None else supplements.supplement_bands
    found: list[tuple[SupplementBand, Decimal]] = []
    for band in bands:
        period = band.rate.period_at(day)
        if (
            band.work is work
            and (not band.levels or terms.level_code in band.levels)
            and period is not None
            and period.value is not None
        ):
            found.append((band, period.value))
    return found


def _band(
    terms: HourlyTerms, work: SupplementWork, day: date
) -> tuple[SupplementBand, Decimal] | str:
    """Return the band of ``work`` the worker is paid with on ``day``.

    Returns:
        The band and its rate, or the reason none can be chosen.
    """
    found = _in_force(terms, work, day)
    if not found:
        return (
            f"the CCNL ({terms.ruleset}) has no {work.value} supplement band "
            "the engine applies (see its coverage notes)"
        )
    roles = sorted({b.role for b, _ in found if b.role is not None})
    if roles and terms.roles is None:
        return (
            f"the CCNL ({terms.ruleset}) pays {work.value} work apart for the "
            f"roles {', '.join(roles)} and Employment.roles is not stated"
        )
    held = terms.roles or frozenset()
    chosen = next(((b, r) for b, r in found if b.role in held), None)
    chosen = chosen or next(((b, r) for b, r in found if b.role is None), None)
    if chosen is None:
        return (
            f"the CCNL ({terms.ruleset}) has a {work.value} supplement band "
            f"only for the roles {', '.join(roles)}"
        )
    return chosen


def resolve_supplement(event: SupplementEvent, terms: HourlyTerms) -> SupplementPay:
    """Return the CCNL supplement of an event without ``supplement_amount``.

    The event is rejected (``reject_underived``) when the shift kind is not
    stated, the CCNL has no band of the work for the worker or the hourly
    base cannot be derived.

    Returns:
        The supplement and what it is computed from.
    """
    feature = _FEATURES[type(event)]
    field = f"{type(event).__name__}.supplement_amount"
    day = event.event_date
    work = work_of(event)
    if work is None:
        reject_underived(field, feature, day, "ShiftWorkEvent.kind is not stated")
    found = _band(terms, work, day)
    if isinstance(found, str):
        reject_underived(field, feature, day, found)
    band, rate = found
    base = terms.base(day, field, feature, band.base)
    # The event validation requires the hours when the amount is not stated.
    hours = event.hours or Decimal(0)
    return SupplementPay(money(hours * rate * base.rate), band, rate, hours, base)


def supplement_decision(
    event: SupplementEvent, pay: SupplementPay, terms: HourlyTerms
) -> CalculationDecision:
    """Return the decision of a supplement derived from the CCNL band.

    Returns:
        A decision of the event's capability citing the band, provisional
        when the hours themselves may be due apart.
    """
    band = pay.band
    provenance = band.provenance
    return CalculationDecision(
        capability=_FEATURES[type(event)],
        status=(
            CalculationStatus.FINAL
            if band.hours_paid_apart is False
            else CalculationStatus.PROVISIONAL
        ),
        reason_code=SUPPLEMENT_APPLIED,
        rule=supplement_rule(terms, band),
        rule_version=terms.version,
        inputs={
            "work": band.work.value,
            "band_code": band.code,
            "band_supplement": pay.rate,
            "hours": pay.hours,
            **pay.base.inputs(),
            "hourly_base_rule": terms.rule_of(BASE_PATH),
            "hours_paid_apart": _PAID_APART[band.hours_paid_apart],
        },
        source=provenance.location,
        amount=pay.amount,
    )


def supplement_issue(
    event: SupplementEvent, pay: SupplementPay
) -> CalculationIssue | None:
    """Return the issue of a band whose hours the engine does not post.

    Returns:
        ``supplement_hours_not_posted`` when the CCNL pays the hours apart
        or does not settle it, else ``None``.
    """
    paid_apart = pay.band.hours_paid_apart
    if paid_apart is False:
        return None
    day = event.event_date.isoformat()
    hours = f"the {pay.hours} hours worked on {day} (hourly base {pay.base.rate:.4f})"
    why = (
        f"the CCNL band {pay.band.code} pays {hours} on top of the monthly pay"
        if paid_apart
        else f"the CCNL text of band {pay.band.code} does not settle whether "
        f"{hours} are paid on top of the monthly pay"
    )
    message = f"{why}; the engine posts the supplement only, not those hours"
    return CalculationIssue(
        HOURS_NOT_POSTED,
        message,
        CalculationStatus.PROVISIONAL,
        capability=_FEATURES[type(event)],
    )
