"""Extra premium of the overtime worked past the yearly 'quote esenti'.

Federmeccanica art. 7 (ipotesi di rinnovo of 22 November 2025, p. 35):
"Per le ore di straordinario in regime di «quote esenti» dall'accordo
preventivo eccedenti le 40 ore annue, per i lavoratori turnisti e per i
lavoratori non turnisti che lavorino in aziende con oltre 200 dipendenti,
ovvero le 48 ore annue, per i lavoratori non turnisti che lavorino in
aziende fino a 200 dipendenti, sarà corrisposta una maggiorazione
aggiuntiva pari all'8% per ciascuna ora lavorata".

The hours of the regime worked earlier in the year are a fact of the
timesheet (``OvertimeEvent.exempt_quota_hours_before``); stating them
places the event in the regime.  Without them, or without the facts that
choose the quota, the extra premium is not added and the run carries the
CCNL limitation of the clause.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.event.facade import OvertimeEvent

__all__ = [
    "EXEMPT_QUOTA_VARIANT",
    "OvertimeExemptQuota",
    "QuotaPremium",
    "quota_hours",
    "quota_premium",
]

#: Variant of the CCNL limitation a run carries when the premium is unknown.
EXEMPT_QUOTA_VARIANT = "overtime_exempt_quota_supplement"
_ZERO = Decimal(0)


class OvertimeExemptQuota(BaseModel):
    """The extra premium of the overtime past the yearly exempt quota.

    Attributes:
        rate: Extra premium of each hour past the quota, from its decorrenza.
        quota_hours: Yearly quota of the shift workers, and of every worker
            of a firm above ``small_firm_headcount``.
        small_firm_quota_hours: Yearly quota of the workers not on shifts of
            a firm of at most ``small_firm_headcount`` employees.
        small_firm_headcount: Headcount up to which a firm is small.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: TimeSeries
    quota_hours: int = Field(gt=0)
    small_firm_quota_hours: int = Field(gt=0)
    small_firm_headcount: int = Field(gt=0)
    provenance: RuleProvenance


def quota_hours(
    rule: OvertimeExemptQuota, headcount: int | None, shift: bool | None
) -> int | None:
    """Return the yearly quota of the worker.

    Returns:
        ``quota_hours`` for a shift worker or a firm above the threshold,
        ``small_firm_quota_hours`` for a worker known not to be on shifts in
        a firm known to be small, ``None`` when the facts leave it open.
    """
    if shift or (headcount is not None and headcount > rule.small_firm_headcount):
        return rule.quota_hours
    if shift is False and headcount is not None:
        return rule.small_firm_quota_hours
    return None


@dataclass(frozen=True)
class QuotaPremium:
    """The extra premium of an overtime event.

    Attributes:
        multiplier: Multiplier to add to the event's multiplier, zero when
            no hour of the event is past the quota.
        hours: Hours of the event past the quota.
        quota: Yearly quota applied, ``None`` when unknown.
        rate: Extra premium of each hour past the quota.
        unknown: Whether a fact the premium needs is missing.
    """

    multiplier: Decimal = _ZERO
    hours: Decimal = _ZERO
    quota: int | None = None
    rate: Decimal = _ZERO
    unknown: bool = False


def quota_premium(
    event: OvertimeEvent, rule: OvertimeExemptQuota | None, headcount: int | None
) -> QuotaPremium | None:
    """Return the extra premium of ``event`` under ``rule``.

    Returns:
        ``None`` when the CCNL has no such clause in force on the event
        day; otherwise the premium, ``unknown`` when the hours of the
        regime before the event or the quota are not known.
    """
    if rule is None:
        return None
    period = rule.rate.period_at(event.event_date)
    if period is None or period.is_gap:
        return None
    rate = rule.rate.value_at(event.event_date)
    before = event.exempt_quota_hours_before
    quota = quota_hours(rule, headcount, event.in_periodic_shift)
    if before is None or quota is None:
        return QuotaPremium(quota=quota, rate=rate, unknown=True)
    past = max(before + event.hours - max(before, Decimal(quota)), _ZERO)
    return QuotaPremium(
        multiplier=rate * past / event.hours, hours=past, quota=quota, rate=rate
    )
