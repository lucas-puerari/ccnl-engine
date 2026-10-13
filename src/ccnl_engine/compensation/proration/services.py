"""The monthly pay a run posts: once per competence month, prorated.

The monthly pay of a competence month is posted once, by the run that
closes the month first:

- the regular run;
- a termination run, when the regular run of its month is not closed in
  the opening state (a termination closes the competence year, so no
  regular run of the month can follow it); when it is, the termination run
  posts no monthly pay;
- never an adjustment run, which corrects a run already closed.

The run that posts it for a month the employment covers only in part pays
the daily quotas of its employed days
(:mod:`~ccnl_engine.compensation.proration.rules`), read from the unpaid-absence
rule of the CCNL (``work_rules.absence_rules``) and, for ``by_hourly``, its
hourly divisor.  Without that rule the month is never paid in full: the pay
chain posts nothing, the ``base_salary`` decision carries no amount and an
incomplete issue makes the result not payable.  Extra-month runs keep their
own chain, scaled by the ratei.

A worker of a category the CCNL pays by the hour (``parameters.hourly_pay``)
is paid the chain over the hourly divisor times the ordinary hours worked
(:class:`HourlyBasis`), whatever the days employed: the hours already leave
out the days not employed.  Without the hours the chain posts nothing and the
run has the same ``missing_fact`` blocker as the Prevedi amount per hour.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.compensation.proration.rules import MonthProration
from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import AbsenceEvent
from ccnl_engine.run.models import PayrollRun, RunKind

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.employment.fact.inputs import EmploymentPeriod
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.provenance.source.models import SourceLocation

__all__ = [
    "FULL_MONTH",
    "HOURS_UNKNOWN",
    "PAID_BY_THE_HOUR",
    "POSTED_BY_ANOTHER_RUN",
    "PRORATED",
    "RULE_MISSING",
    "HourlyBasis",
    "RunProration",
    "run_proration",
]

#: Reason of a ``base_salary`` decision paid in daily quotas.
PRORATED = "pay_chain_prorated"
#: Reason of a ``base_salary`` decision without a partial-month rule.
RULE_MISSING = "partial_month_rule_missing"
#: Reason of a ``base_salary`` decision of a run that posts no monthly pay.
POSTED_BY_ANOTHER_RUN = "monthly_pay_posted_by_another_run"
#: Reason of a ``base_salary`` decision paid on the ordinary hours worked.
PAID_BY_THE_HOUR = "pay_chain_paid_by_the_hour"
#: Reason of a ``base_salary`` decision paid by the hour without the hours.
HOURS_UNKNOWN = "hourly_pay_hours_unknown"
#: Who posts the monthly pay of an adjustment run's month.
_CORRECTED_RUN = "corrected_run"
_NONE = "none"
_HOURS_ISSUE = CalculationIssue(
    code=HOURS_UNKNOWN,
    message=(
        "the CCNL pays the worker by the ordinary hour worked, which the run "
        "does not state: the pay of the month is undetermined, the amounts "
        "shown leave it out; state PeriodFacts.ordinary_hours_worked"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="ordinary_hours_worked",
)


@dataclass(frozen=True)
class HourlyBasis:
    """Hours a run pays by the hour and what the monthly pay is divided by.

    Attributes:
        hours: Ordinary hours worked in the month, ``None`` when the run
            does not state them.
        divisor: Hourly divisor of the CCNL; for a part-time worker times
            the part-time ratio, since the chain is already reduced by it:
            the hours worked carry the part time.
    """

    hours: Decimal | None
    divisor: Decimal

    def apply(self, chain: MonthlyPayChain) -> MonthlyPayChain:
        """Return the chain paid on the hours worked.

        Returns:
            Every component times ``hours / divisor``, rounded once; a zero
            chain without the hours.
        """
        if self.hours is None:
            return chain.scaled(Decimal(0))
        return chain.prorated(self.hours, self.divisor)


@dataclass(frozen=True)
class RunProration:
    """Whether a run pays part of its month, and with which CCNL rule.

    Attributes:
        span: First and last employed day of a partly employed month whose
            regular run this is; ``None`` for any other run.
        proration: Payable days and divisor of ``span``, ``None`` when the
            CCNL defines no partial-month rule.
        rules: Rules the proration read, with their provenance.
        source: Location of the absence rule of the CCNL, if recorded.
        posted_by: Run that posts the monthly pay of the month instead of
            this one (``corrected_run`` for an adjustment), ``None`` when
            this run posts it.
        hourly: Hours of a worker paid by the hour, which replace the
            days of ``span``; ``None`` for a worker paid by the month.
    """

    span: tuple[date, date] | None
    proration: MonthProration | None = None
    rules: tuple[Rule, ...] = ()
    source: SourceLocation | None = None
    posted_by: str | None = None
    hourly: HourlyBasis | None = None

    @property
    def partial(self) -> bool:
        """Whether the run pays part of its month."""
        return self.span is not None

    @property
    def missing(self) -> bool:
        """Whether the pay of the run is undetermined.

        A run paid by the hour misses the hours; any other partial run the
        CCNL rule to prorate with.
        """
        if self.hourly is not None:
            return self.hourly.hours is None
        return self.partial and self.proration is None

    @property
    def reason(self) -> str | None:
        """Reason of the ``base_salary`` decision, ``None`` for a full month."""
        if self.posted_by is not None:
            return POSTED_BY_ANOTHER_RUN
        if self.hourly is not None:
            return HOURS_UNKNOWN if self.missing else PAID_BY_THE_HOUR
        if not self.partial:
            return None
        return RULE_MISSING if self.missing else PRORATED

    def apply(self, chain: MonthlyPayChain) -> MonthlyPayChain:
        """Return the part of ``chain`` the run pays.

        Returns:
            ``chain`` for a full month or a span worth a monthly pay, the
            prorated chain for a shorter span, a zero chain without a rule
            or when another run posts the monthly pay; the chain of the
            hours worked of a worker paid by the hour.
        """
        if self.posted_by is not None:
            return chain.scaled(Decimal(0))
        if self.hourly is not None:
            return self.hourly.apply(chain)
        if not self.partial:
            return chain
        proration = self.proration
        if proration is None:
            return chain.scaled(Decimal(0))
        if proration.full:
            return chain
        return chain.prorated(proration.units, proration.divisor)

    def inputs(self) -> dict[str, Decimal | str]:
        """Return the decision inputs of a partial run.

        Returns:
            The employed span, the method, payable days and divisor; the run
            that posts the monthly pay instead; the hours and divisor of a
            run paid by the hour; empty for a full month.
        """
        if self.posted_by is not None:
            return {"monthly_pay_posted_by": self.posted_by}
        hourly = self.hourly
        if hourly is not None:
            hours = _NONE if hourly.hours is None else hourly.hours
            return {"ordinary_hours_worked": hours, "hourly_divisor": hourly.divisor}
        if self.span is None:
            return {}
        first, last = self.span
        proration = self.proration
        return {
            "employed_from": first.isoformat(),
            "employed_until": last.isoformat(),
            "divisor_method": _NONE if proration is None else proration.method.value,
            "payable_days": _NONE if proration is None else str(proration.days),
            "divisor": _NONE if proration is None else proration.divisor,
        }

    def issue(self) -> CalculationIssue | None:
        """Return the issue of a partial run without a CCNL rule.

        Returns:
            An incomplete issue, or ``None``; the ``missing_fact`` issue of a
            run paid by the hour without the hours.
        """
        if self.hourly is not None:
            return _HOURS_ISSUE if self.missing else None
        if not self.missing or self.span is None:
            return None
        first, last = self.span
        return CalculationIssue(
            code=RULE_MISSING,
            message=(
                f"employment covers only {first.isoformat()} to "
                f"{last.isoformat()} of the month and the CCNL data define no "
                "daily quota to prorate the monthly pay: the pay of the month "
                "is undetermined, the amounts shown leave it out"
            ),
            status=CalculationStatus.INCOMPLETE,
        )


#: Proration of a run that pays its whole month.
FULL_MONTH = RunProration(span=None)
#: Kinds of run that may post the monthly pay of their month.
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})


def _posted_by(request: PeriodCalculationRequest, run_kind: RunKind) -> str | None:
    """Return the run that posts the monthly pay instead of this one.

    Returns:
        ``corrected_run`` for an adjustment, the regular run of the month
        for a termination run after it, ``None`` otherwise.
    """
    if run_kind is RunKind.ADJUSTMENT:
        return _CORRECTED_RUN
    if run_kind is not RunKind.TERMINATION:
        return None
    month = request.period_id
    regular = PayrollRun.regular(month.year, month.month).identifier
    closed = request.opening_state.accrual.competence_runs
    return str(regular) if regular in closed else None


def _partial_span(
    request: PeriodCalculationRequest, run_kind: RunKind
) -> tuple[date, date] | None:
    """Return the employed span of a partly employed month the run pays.

    Returns:
        ``None`` for an extra-month run, an untracked employment or a fully
        employed month.
    """
    period: EmploymentPeriod | None = request.employment_period
    month = request.period_id
    if (
        run_kind not in _PAYING_KINDS
        or period is None
        or period.covers_month(month.year, month.month)
    ):
        return None
    return period.span_in_month(month.year, month.month)


def _hourly_rule(ccnl: CCNL, name: str, day: date) -> tuple[Decimal | None, Rule]:
    """Return the hourly divisor in force on ``day`` and its rule.

    Returns:
        The divisor, ``None`` when the series has no value on ``day``.
    """
    period = ccnl.parameters.hourly_divisor.period_at(day)
    if period is None:
        return None, (f"{name}:hourly_divisor", None)
    rule: Rule = (f"{name}:hourly_divisor[{period.valid_from}]", period.provenance)
    return period.value, rule


def _reject_absences(request: PeriodCalculationRequest) -> None:
    """Reject an absence event of a worker paid by the hour.

    Raises:
        InvalidInputError: When the request carries an ``AbsenceEvent``: its
            hours are not among the hours worked, so it would deduct them
            twice.
    """
    for i, event in enumerate(request.events):
        if isinstance(event, AbsenceEvent):
            msg = (
                "the CCNL pays the worker by the hour: the absent hours are "
                "already excluded from PeriodFacts.ordinary_hours_worked, an "
                "AbsenceEvent would deduct them a second time"
            )
            raise InvalidInputError(
                msg, field=f"PeriodFacts.events[{i}]", feature="base_salary"
            )


def _hourly_basis(
    request: PeriodCalculationRequest,
    ccnl: CCNL,
    span: tuple[date, date] | None,
    worker_category: WorkerCategory | None,
) -> RunProration | None:
    """Return the proration of a worker the CCNL pays by the hour.

    Returns:
        The hours and divisor with the ``hourly_pay`` and divisor rules;
        ``None`` for a worker paid by the month.
    """
    spec = ccnl.parameters.hourly_pay
    if spec is None or worker_category not in spec.categories:
        return None
    _reject_absences(request)
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    month = request.period_id
    day = date(month.year, month.month, 1)
    with rule_scope(ruleset=ccnl.meta.ccnl_id, feature="base_salary"):
        divisor = ccnl.parameters.hourly_divisor.value_at(day)
    weekly, full = request.weekly_hours, request.full_time_weekly_hours
    if weekly is not None and full is not None and weekly.value < full.value:
        divisor = divisor * Decimal(weekly.value) / Decimal(full.value)
    stated = request.ordinary_hours_worked
    pay: Rule = (f"{name}:hourly_pay", spec.provenance)
    return RunProration(
        span=span,
        rules=(pay, _hourly_rule(ccnl, name, day)[1]),
        source=spec.provenance.location,
        hourly=HourlyBasis(None if stated is None else stated.value, divisor),
    )


def run_proration(
    request: PeriodCalculationRequest,
    ccnl: CCNL,
    run_kind: RunKind,
    worker_category: WorkerCategory | None = None,
) -> RunProration:
    """Return the proration of the run of ``request``.

    Returns:
        A proration that posts no monthly pay when another run posts it;
        the hourly basis of a worker paid by the hour on a run that posts
        the monthly pay; :data:`FULL_MONTH` unless the run pays a partly
        employed month.
    """
    posted_by = _posted_by(request, run_kind)
    if posted_by is not None:
        return RunProration(span=None, posted_by=posted_by)
    span = _partial_span(request, run_kind)
    by_hour = (
        _hourly_basis(request, ccnl, span, worker_category)
        if run_kind in _PAYING_KINDS
        else None
    )
    if by_hour is not None:
        return by_hour
    if span is None:
        return FULL_MONTH
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    rules = None if ccnl.work_rules is None else ccnl.work_rules.absence_rules
    if rules is None:
        return RunProration(span=span)
    provenance = rules.provenance
    absence: Rule = (f"{name}:work_rules.absence_rules", provenance)
    source = None if provenance is None else provenance.location
    if rules.daily_divisor_method is not DailyDivisorMethod.BY_HOURLY:
        return RunProration(
            span=span,
            proration=MonthProration.of(rules.daily_divisor_method, span),
            rules=(absence,),
            source=source,
        )
    divisor, hourly = _hourly_rule(ccnl, name, span[0])
    return RunProration(
        span=span,
        proration=MonthProration.of(
            rules.daily_divisor_method,
            span,
            hourly_divisor=divisor,
            daily_hours=rules.daily_hours,
        ),
        rules=(absence, hourly),
        source=source,
    )
