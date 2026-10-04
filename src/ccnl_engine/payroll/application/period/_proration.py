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
(:mod:`~ccnl_engine.payroll.domain.proration`), read from the unpaid-absence
rule of the CCNL (``work_rules.absence_rules``) and, for ``by_hourly``, its
hourly divisor.  Without that rule the month is never paid in full: the pay
chain posts nothing, the ``base_salary`` decision carries no amount and an
incomplete issue makes the result not payable.  Extra-month runs keep their
own chain, scaled by the ratei.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.absence import DailyDivisorMethod
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.proration import MonthProration
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.period._rule_lookup import Rule
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.service.types import MonthlyPayChain
    from ccnl_engine.provenance.domain.source import SourceLocation

__all__ = [
    "FULL_MONTH",
    "POSTED_BY_ANOTHER_RUN",
    "PRORATED",
    "RULE_MISSING",
    "RunProration",
    "run_proration",
]

#: Reason of a ``base_salary`` decision paid in daily quotas.
PRORATED = "pay_chain_prorated"
#: Reason of a ``base_salary`` decision without a partial-month rule.
RULE_MISSING = "partial_month_rule_missing"
#: Reason of a ``base_salary`` decision of a run that posts no monthly pay.
POSTED_BY_ANOTHER_RUN = "monthly_pay_posted_by_another_run"
#: Who posts the monthly pay of an adjustment run's month.
_CORRECTED_RUN = "corrected_run"
_NONE = "none"


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
    """

    span: tuple[date, date] | None
    proration: MonthProration | None = None
    rules: tuple[Rule, ...] = ()
    source: SourceLocation | None = None
    posted_by: str | None = None

    @property
    def partial(self) -> bool:
        """Whether the run pays part of its month."""
        return self.span is not None

    @property
    def missing(self) -> bool:
        """Whether a partial run has no CCNL rule to prorate with."""
        return self.partial and self.proration is None

    @property
    def reason(self) -> str | None:
        """Reason of the ``base_salary`` decision, ``None`` for a full month."""
        if self.posted_by is not None:
            return POSTED_BY_ANOTHER_RUN
        if not self.partial:
            return None
        return RULE_MISSING if self.missing else PRORATED

    def apply(self, chain: MonthlyPayChain) -> MonthlyPayChain:
        """Return the part of ``chain`` the run pays.

        Returns:
            ``chain`` for a full month or a span worth a monthly pay, the
            prorated chain for a shorter span, a zero chain without a rule
            or when another run posts the monthly pay.
        """
        if self.posted_by is not None:
            return chain.scaled(Decimal(0))
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
            that posts the monthly pay instead; empty for a full month.
        """
        if self.posted_by is not None:
            return {"monthly_pay_posted_by": self.posted_by}
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
            An incomplete issue, or ``None``.
        """
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


def run_proration(
    request: PeriodCalculationRequest, ccnl: CCNL, run_kind: RunKind
) -> RunProration:
    """Return the proration of the run of ``request``.

    Returns:
        A proration that posts no monthly pay when another run posts it;
        :data:`FULL_MONTH` unless the run pays a partly employed month.
    """
    posted_by = _posted_by(request, run_kind)
    if posted_by is not None:
        return RunProration(span=None, posted_by=posted_by)
    span = _partial_span(request, run_kind)
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
