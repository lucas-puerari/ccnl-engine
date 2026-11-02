"""The NASpI contribution of the run that closes an employment.

The run that closes the employment posts the contribution of L. 92/2012
art. 2 c. 31 as an employer contribution, once: a run of the same
employment that closed it before (the regular run of the last month, then
its termination run) leaves it to that run.  The cases that change it (a
resignation in the maternity protection, a mutual agreement before the
labour office or on a transfer, the changes of contractor and site
closures of c. 34, the collective dismissal of c. 35) are
``EmploymentPeriod.naspi_case``; an end that does not state it is decided
from its cause alone, provisionally, with an issue naming the fact.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.employment.period.inputs import (
    CollectiveDismissal,
    TerminationCause,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.models import EmployerContributionItem
from ccnl_engine.pay_item.services import _make_entry, _require_resolution
from ccnl_engine.run.models import RunKind
from ccnl_engine.termination.naspi.loaders import load_naspi_dismissal_rules
from ccnl_engine.termination.naspi.rules import (
    case_inputs,
    contribution_terms,
    dismissal_contribution,
    is_due,
    service_months,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.rule.models import RuleProvenance
    from ccnl_engine.run.models import PayrollRunId

__all__ = [
    "CASE_UNKNOWN",
    "NASPI_DISMISSAL",
    "NaspiDismissal",
    "naspi_dismissal",
    "naspi_rules",
]

#: Capability of the contribution.
NASPI_DISMISSAL = "naspi_dismissal"
#: An end that could be a case of the contribution does not state it.
CASE_UNKNOWN = "naspi_dismissal_case_unknown"
_KIND = "employer_contribution_item"
_RULE = "law/naspi-dismissal:l92-2012-art2-c31"
_ZERO = Decimal(0)
type _Inputs = dict[str, Decimal | str]


@dataclass(frozen=True)
class NaspiDismissal:
    """The NASpI contribution of the run, with its decision or issue."""

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _closed(run: PayrollRunId, ended: date) -> bool:
    month = (ended.year, ended.month)
    return run.kind is RunKind.TERMINATION or (
        run.kind is RunKind.REGULAR and (run.year, run.month) == month
    )


def _issue(
    code: str, message: str, *, fact: str | None = None, cause: IssueCause | None = None
) -> NaspiDismissal:
    issue = CalculationIssue(
        code=code,
        message=message,
        status=CalculationStatus.INCOMPLETE,
        capability=NASPI_DISMISSAL,
        fact=fact,
        cause=cause,
    )
    return NaspiDismissal(issues=(issue,))


def _decision(
    ctx: RunContext, reason: str, amount: Decimal, inputs: _Inputs, *, open_case: bool
) -> CalculationDecision:
    final = CalculationStatus.PROVISIONAL if open_case else CalculationStatus.FINAL
    return CalculationDecision(
        capability=NASPI_DISMISSAL,
        status=final,
        reason_code=reason,
        rule=_RULE,
        rule_version=str(ctx.fiscal_year),
        inputs=inputs,
        amount=amount,
    )


def _ending(
    ctx: RunContext,
) -> tuple[EmploymentPeriod, date, TerminationCause, bool] | NaspiDismissal:
    """Return the end of the employment and whether it owes the contribution.

    Returns:
        The period, its last day, its cause and whether it owes the
        contribution; nothing when an earlier run closed the employment;
        the ``incomplete`` issue of a fact not stated.
    """
    period = ctx.request.employment_period
    if period is None or period.ended_on is None:
        return _issue(
            "naspi_dismissal_end_unknown",
            "the NASpI contribution of the end of the employment counts the "
            "service up to its last day (EmploymentPeriod.ended_on), which is "
            "not stated: it is not computed",
            cause=IssueCause.CONDITION,
        )
    ended = period.ended_on
    if any(_closed(run, ended) for run in ctx.opening.accrual.competence_runs):
        return NaspiDismissal()
    cause = period.ended_by
    if cause is None:
        return _issue(
            "naspi_dismissal_cause_unknown",
            "whether the end of the employment owes the NASpI contribution "
            "(L. 92/2012 art. 2 c. 31) depends on its cause "
            "(EmploymentPeriod.ended_by), which is not stated",
            fact="ended_by",
        )
    due = is_due(cause, period.just_cause, ctx.request.contract_type, period.naspi_case)
    if due is None:
        return _issue(
            "naspi_dismissal_just_cause_unknown",
            "a resignation owes the NASpI contribution only for just cause "
            "(INPS circ. 44/2013 par. 1), which EmploymentPeriod.just_cause "
            "does not state",
            fact="just_cause",
        )
    return period, ended, cause, due


def _case_issue() -> CalculationIssue:
    return CalculationIssue(
        code=CASE_UNKNOWN,
        message=(
            "the end does not state its NASpI case (EmploymentPeriod.naspi_case: "
            "a maternity resignation, a conciliation or a transfer owe the "
            "contribution, a change of contractor or a site closure leave it "
            "out, a collective dismissal changes it; NaspiCase.ORDINARY for "
            "none): it is decided from the cause alone"
        ),
        status=CalculationStatus.PROVISIONAL,
        capability=NASPI_DISMISSAL,
        fact="naspi_case",
        cause=IssueCause.FACT,
    )


def _posted(
    ctx: RunContext, amount: Decimal, inputs: _Inputs, *, open_case: bool
) -> NaspiDismissal:
    item_id = f"naspi_dismissal_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    item = EmployerContributionItem(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source="L. 92/2012 art. 2 c. 31",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.EMPLOYER_CONTRIBUTIONS,
        amount,
        policy_id=resolution.policy_id,
    )
    return NaspiDismissal(
        items=(item,),
        entries=(entry,),
        decisions=(_decision(ctx, "due", amount, inputs, open_case=open_case),),
        issues=(_case_issue(),) if open_case else (),
    )


def naspi_dismissal(ctx: RunContext) -> NaspiDismissal:
    """Return the NASpI contribution the run owes on closing the employment.

    Returns:
        Nothing for a run that does not close the employment or whose
        employment an earlier run closed; the item, entry and decision of
        the contribution, or the nil decision of an end that owes none;
        an ``incomplete`` issue when the last day, the cause or the just
        cause of a resignation is not stated, or the year has no NASpI
        maximum.
    """
    if not ctx.closes_employment:
        return NaspiDismissal()
    found = _ending(ctx)
    if isinstance(found, NaspiDismissal):
        return found
    period, ended, cause, due = found
    inputs: _Inputs = {
        "cause": cause.value,
        "contract_type": ctx.request.contract_type.type,
        "ended_on": ended.isoformat(),
    }
    inputs |= case_inputs(period.naspi_case)
    unstated = period.naspi_case is None
    if cause is TerminationCause.RESIGNATION and period.just_cause is not None:
        inputs["just_cause"] = str(period.just_cause).lower()
    if not due:
        # A death, or the end of a contract the contribution leaves out,
        # has no exception that would owe it.
        excepted = (
            unstated
            and cause is not TerminationCause.DEATH
            and isinstance(ctx.request.contract_type, Permanent | Apprentice)
        )
        return NaspiDismissal(
            decisions=(_decision(ctx, "not_due", _ZERO, inputs, open_case=excepted),),
            issues=(_case_issue(),) if excepted else (),
        )
    rules = load_naspi_dismissal_rules(ended.year)
    if rules is None:
        return _issue(
            "naspi_dismissal_rule_missing",
            f"the bundle has no NASpI maximum of {ended.year}: the contribution "
            "of the end of the employment is not computed",
            cause=IssueCause.RULE,
        )
    months = service_months(period.started_on, ended)
    rate, times = contribution_terms(rules, period.naspi_case)
    inputs |= {
        "service_months": str(months),
        "rate": rate,
        "monthly_maximum": rules.monthly_maximum.value,
    }
    if times != 1:
        inputs["multiplier"] = times
    amount = dismissal_contribution(rules, months, period.naspi_case)
    return _posted(ctx, amount, inputs, open_case=unstated)


def naspi_rules(ctx: RunContext) -> tuple[tuple[str, RuleProvenance], ...]:
    """Return the rules the contribution of the run was computed with.

    Returns:
        The rate (the 82% of a collective dismissal of an employer owing
        the CIGS contribution) and the NASpI maximum of the year of the last
        day, with the multiplier of a collective dismissal without union
        agreement; empty when the year has none.
    """
    period = ctx.request.employment_period
    assert period is not None, "decided on an end"  # pragma: no mutate
    assert period.ended_on is not None, "decided on a last day"  # pragma: no mutate
    rules = load_naspi_dismissal_rules(period.ended_on.year)
    if rules is None:
        return ()
    name = (
        f"law/{rules.year}/naspi-dismissal"
        if rules.ruleset is None
        else rules.ruleset.id
    )
    case = period.naspi_case
    used = [("rate", rules.rate), ("monthly_maximum", rules.monthly_maximum)]
    if isinstance(case, CollectiveDismissal) and case.cigs_employer:
        used[0] = ("collective_rate", rules.collective_rate)
    if isinstance(case, CollectiveDismissal) and not case.union_agreement:
        used.append(("no_agreement_multiplier", rules.no_agreement_multiplier))
    return tuple((f"{name}:{key}", value.provenance) for key, value in used)
