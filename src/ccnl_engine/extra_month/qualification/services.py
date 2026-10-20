"""Month qualification of extra-month ratei: the CCNL rule and termination ratei.

The days of absences that suspend accrual do not count towards a month.
The days of absences whose suspension is not stated count, and mark the
rateo they could change as undetermined.  An extra month whose next
payment falls outside the employment is liquidated on the regular run of
the termination month.

The rule comes from ``parameters.accrual_rule`` when the bundle holds the
signed clause.  Without it the engine default applies (a month counts with
at least 15 accruing days) and the rule carries a ``missing`` provenance
record: a run whose rateo depends on the threshold, because a month of its
window accrued for part of its days, reports the rule as unsourced.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.event.facade import AbsenceEvent
from ccnl_engine.extra_month.models import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
    absence_days,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.run.models import PayrollRun

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.calendar.models import WorkCalendar
    from ccnl_engine.compensation.models import ExtraMonthAccrualRule
    from ccnl_engine.employment.fact.inputs import EmploymentPeriod, WorkPattern
    from ccnl_engine.event.facade import WorkEvent


__all__ = [
    "MISSING_ACCRUAL_PROVENANCE",
    "accrual_rule_id",
    "month_accrual_rule",
    "non_accruing_days",
    "termination_settlements",
    "unknown_accrual_days",
]


def non_accruing_days(events: Iterable[WorkEvent]) -> frozenset[date]:
    """Return the days of the year's absences that suspend accrual.

    Args:
        events: Every event of the year, of any run.

    Returns:
        Every calendar day of an :class:`AbsenceEvent` with
        ``suspends_accrual`` set.
    """
    return _absence_days(events, suspends=True)


def unknown_accrual_days(events: Iterable[WorkEvent]) -> frozenset[date]:
    """Return the days of the year's absences whose suspension is not stated.

    Args:
        events: Every event of the year, of any run.

    Returns:
        Every calendar day of an :class:`AbsenceEvent` whose
        ``suspends_accrual`` is ``None``.
    """
    return _absence_days(events, suspends=None)


def _absence_days(
    events: Iterable[WorkEvent], *, suspends: bool | None
) -> frozenset[date]:
    days: set[date] = set()
    for event in events:
        if isinstance(event, AbsenceEvent) and event.suspends_accrual is suspends:
            last = event.end_date or event.event_date
            days |= absence_days(event.event_date, last)
    return frozenset(days)


def termination_settlements(
    calendar: WorkCalendar,
    employment_period: EmploymentPeriod | None,
    non_accruing_days: frozenset[date],
    rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
    unknown_days: frozenset[date] = frozenset(),
    pattern: WorkPattern | None = None,
) -> dict[str, tuple[ExtraMonthAccrual, ...]]:
    """Return the ratei the last run of an employment ending this year pays.

    An extra month whose next payment after the termination month falls
    outside the employment is liquidated on the regular run of the
    termination month.  Its window is the one of that next payment (the
    following year when the payment month precedes the termination month),
    clipped to the hire date and counted up to the termination date with
    ``rule``; the days of ``unknown_days`` count as accruing and mark
    an accrual they change as undetermined, and the months ``pattern``
    does not work accrue nothing.

    Returns:
        The accruals keyed by the ``run_id`` of the termination month's
        regular run, empty when the employment does not end in the year.
    """
    if employment_period is None or employment_period.ended_on is None:
        return {}
    ended_on = employment_period.ended_on
    if ended_on.year != calendar.year:
        return {}
    accruals = tuple(
        ExtraMonthAccrual.of(
            extra,
            calendar.year + (1 if extra.payment_month < ended_on.month else 0),
            employment_period,
            non_accruing_days=non_accruing_days,
            rule=rule,
            unknown_days=unknown_days,
            pattern=pattern,
        )
        for extra in calendar.extra_months
        if extra.payment_month != ended_on.month
    )
    return {PayrollRun.regular(calendar.year, ended_on.month).run_id: accruals}


#: Provenance of the engine default applied for a CCNL without the clause.
MISSING_ACCRUAL_PROVENANCE = RuleProvenance(
    status=ProvenanceStatus.MISSING,
    note=(
        "No signed CCNL text in the bundle states when a fraction of a month "
        "counts for the extra-month ratei; the engine default (at least 15 "
        "days) applies."
    ),
)


def accrual_rule_id(ccnl: CCNL) -> str:
    """Return the identifier of the accrual rule of ``ccnl``.

    Returns:
        ``<ruleset id>:parameters.accrual_rule``.
    """
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    return f"{name}:parameters.accrual_rule"


def month_accrual_rule(ccnl: CCNL) -> MonthAccrualRule:
    """Return the rule the ratei of ``ccnl`` are counted with.

    Returns:
        The CCNL clause with its provenance, or the engine default with a
        ``missing`` provenance when the bundle has no clause.
    """
    stored = ccnl.parameters.accrual_rule
    if stored is None:
        return MonthAccrualRule(
            min_days=DEFAULT_MONTH_ACCRUAL_RULE.min_days,
            source=DEFAULT_MONTH_ACCRUAL_RULE.source,
            comparison=DEFAULT_MONTH_ACCRUAL_RULE.comparison,
            rule=accrual_rule_id(ccnl),
            provenance=MISSING_ACCRUAL_PROVENANCE,
        )
    return _month_rule(ccnl, stored)


def _month_rule(ccnl: CCNL, stored: ExtraMonthAccrualRule) -> MonthAccrualRule:
    """Return the month rule of a stored clause and of the clauses before it.

    Returns:
        The rule, its :attr:`~MonthAccrualRule.previous` built likewise.
    """
    location = stored.provenance.location
    section = None if location is None else location.section
    previous = stored.previous
    return MonthAccrualRule(
        min_days=stored.min_days,
        source=f"CCNL {ccnl.meta.name}: {section or 'accrual clause'}",
        comparison=stored.comparison,
        working_days=stored.working_days,
        rule=accrual_rule_id(ccnl),
        provenance=stored.provenance,
        valid_from=stored.valid_from,
        previous=None if previous is None else _month_rule(ccnl, previous),
    )
