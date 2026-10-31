"""Deduction of an unpaid absence at the quota of the CCNL absence rule.

An absence without ``hourly_rate`` is deducted at the quota the CCNL absence
rule (``work_rules.absence_rules``) sets, from the monthly pay elements of
its hourly base (:mod:`~ccnl_engine.working_time.hourly.policies`):

- ``by_hourly``: each absent hour at ``monthly / hourly divisor`` (CCNL
  chimica art. 20 punto 3: "in ragione di 1/175 della retribuzione mensile
  per ogni ora non lavorata");
- ``by_22``, ``by_26``, ``by_30``: each of the ``working_days`` at
  ``monthly / days`` (CCNL Turismo art. 150: the 26th is valid "ivi compresi
  i casi di trattenuta per assenze non retribuite").

The engine derives it only when the absence rule is ``verified``: a rule
taken by analogy (``derived``, the metalmeccanici read the 1/26 of a
festività falling on a Sunday) leaves the rate to the caller.  An absence of
hours under a daily rule, and any absence of a part-time worker under a
daily rule (whose day is not a 26th of the full-time month), are not derived
either.  Every refusal names its reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from ccnl_engine.working_time.hourly.policies import (
    BASE_PATH,
    Unstated,
    reject_underived,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.inputs import AbsenceEvent
    from ccnl_engine.absence.models import AbsenceRules
    from ccnl_engine.working_time.hourly.policies import HourlyBase, HourlyTerms

__all__ = ["ABSENCE_QUOTA_APPLIED", "RULE_PATH", "AbsenceQuota", "resolve_absence"]

#: Reason of the decision of an absence deducted at the CCNL quota.
ABSENCE_QUOTA_APPLIED = "ccnl_absence_quota_applied"
#: Path of the absence rule in a CCNL file.
RULE_PATH = "work_rules.absence_rules"
_FEATURE = "absence"
_FIELD = "AbsenceEvent.hourly_rate"
_DAILY = {
    DailyDivisorMethod.BY_22: Decimal(22),
    DailyDivisorMethod.BY_26: Decimal(26),
    DailyDivisorMethod.BY_30: Decimal(30),
}


@dataclass(frozen=True)
class AbsenceQuota:
    """The deduction of an absence and what it is computed from.

    Attributes:
        amount: Amount deducted, positive, rounded to the cent.
        hourly_rate: Rate per absent hour that deducts ``amount``.
        method: Method of the CCNL absence rule.
        divisor: Hours (``by_hourly``) or days of one monthly pay.
        units: Absent hours or working days deducted.
        base: The hourly base whose monthly elements are divided.
    """

    amount: Decimal
    hourly_rate: Decimal
    method: DailyDivisorMethod
    divisor: Decimal
    units: Decimal
    base: HourlyBase


def _rules(terms: HourlyTerms, day: date) -> AbsenceRules | str:
    """Return the verified absence rule of the CCNL, or why not.

    Returns:
        The rule, or the reason it cannot be applied.
    """
    work = None if terms.ccnl is None else terms.ccnl.work_rules
    rules = None if work is None else work.absence_rules
    record = None if rules is None else rules.provenance
    if (
        rules is None
        or record is None
        or record.status is not ProvenanceStatus.VERIFIED
    ):
        status = "none" if record is None else record.status.value
        return (
            f"the CCNL ({terms.ruleset}) absence rule is not verified "
            f"(status {status}) on {day}"
        )
    return rules


def _units(
    event: AbsenceEvent, terms: HourlyTerms, rules: AbsenceRules
) -> tuple[Decimal, Decimal | None] | str | Unstated:
    """Return the units deducted and the days of a monthly pay, or why not.

    Returns:
        The hours and ``None`` for ``by_hourly``, the working days and the
        divisor for a daily rule, or the reason the absence is not derived.
    """
    method = rules.daily_divisor_method
    if method is DailyDivisorMethod.BY_HOURLY:
        return event.hours, None
    days = _DAILY.get(method)
    name = f"the CCNL ({terms.ruleset}) deducts an absence by {method.value}"
    if days is None:
        return f"{name}, whose quota of a day the engine does not derive"
    if event.working_days is None:
        return Unstated(
            "AbsenceEvent.working_days",
            f"{name} and AbsenceEvent.working_days is not stated",
        )
    if terms.part_time:
        return f"{name} and the day of a part-time worker is not such a quota"
    return Decimal(event.working_days), days


def resolve_absence(event: AbsenceEvent, terms: HourlyTerms) -> AbsenceQuota:
    """Return the CCNL deduction of an absence without ``hourly_rate``.

    The event is rejected (``reject_underived``) when the absence rule is
    not verified, the absence is not of the units the rule deducts, or the
    hourly base cannot be derived.

    Returns:
        The deduction and what it is computed from.
    """
    day = event.event_date
    rules = _rules(terms, day)
    if isinstance(rules, str):
        reject_underived(_FIELD, _FEATURE, day, rules)
    units = _units(event, terms, rules)
    if isinstance(units, str | Unstated):
        reject_underived(_FIELD, _FEATURE, day, units)
    count, days = units
    base = terms.base(day, _FIELD, _FEATURE)
    if days is None:
        return AbsenceQuota(
            money(count * base.rate),
            base.rate,
            rules.daily_divisor_method,
            base.divisor,
            count,
            base,
        )
    amount = money(count * base.monthly / days)
    # The event deducts hours x rate: this rate deducts the days' amount.
    rate = count * base.monthly / (days * event.hours)
    return AbsenceQuota(amount, rate, rules.daily_divisor_method, days, count, base)


def absence_decision(
    quota: AbsenceQuota, terms: HourlyTerms, gross: Decimal
) -> CalculationDecision:
    """Return the decision of an absence deducted at the CCNL quota.

    Args:
        quota: The deduction.
        terms: The hourly terms of the run.
        gross: Amount the event posts, negative.

    Returns:
        An ``absence`` decision citing the CCNL absence rule.
    """
    work = None if terms.ccnl is None else terms.ccnl.work_rules
    rules = None if work is None else work.absence_rules
    record = None if rules is None else rules.provenance
    return CalculationDecision(
        capability=_FEATURE,
        status=CalculationStatus.FINAL,
        reason_code=ABSENCE_QUOTA_APPLIED,
        rule=terms.rule_of(RULE_PATH),
        rule_version=terms.version,
        inputs={
            "daily_divisor_method": quota.method.value,
            "quota_divisor": quota.divisor,
            "units": quota.units,
            **quota.base.inputs(),
            "hourly_base_rule": terms.rule_of(BASE_PATH),
        },
        source=None if record is None else record.location,
        amount=gross,
    )
