"""Handler of the notice not given: the indemnity the employer owes.

The indemnity is the pay of the notice not worked (art. 2118 c. 2 c.c.):
the monthly pays of the CCNL band (or its calendar days) on the monthly
pay of art. 2121 c.c., with the extra months where the CCNL says so; a
notice partly worked pays the share of its days left.  The item is in the
INPS base (art. 12 c. 4 lett. b L. 153/1969: "fatta salva l'imponibilità
dell'indennità sostitutiva del preavviso"), out of the TFR base unless the
CCNL puts it in (Cass. 19 January 2023 n. 1581: "L'indennità di mancato
preavviso non rientra nella base di computo del T.f.r."), and taxed apart
(art. 17 c. 1 lett. a TUIR) at the rate of the TFR settlement of the run
(art. 19 c. 2).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.handlers import EventEffect
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.models import NoticeIndemnityItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.termination.notice.inputs import employer_owes
from ccnl_engine.termination.notice.rules import notice_period

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.event.handlers import _EventHandlerCtx
    from ccnl_engine.termination.notice.inputs import NoticeIndemnityEvent
    from ccnl_engine.termination.notice.models import NoticeBand
    from ccnl_engine.termination.notice.services import NoticeTerms

__all__ = ["NOTICE", "_handle_notice_indemnity"]

#: Capability of the notice of a termination.
NOTICE = "termination_notice"
_KIND = "notice_indemnity_item"
_FEATURE = "termination_notice"
_ZERO = Decimal(0)
#: Limitations of the indemnity.
PARTIAL = "notice_indemnity_partial"
EXTRA_MONTHS = "notice_indemnity_extra_months"
_WITH_JUST_CAUSE = frozenset({TerminationCause.DISMISSAL, TerminationCause.RESIGNATION})
DAY_MEASURE = "notice_indemnity_day_measure"
_MONTH_DAYS = Decimal(30)
_MONTHS = Decimal(12)
type _Inputs = dict[str, Decimal | str]


def _check(
    event: NoticeIndemnityEvent, terms: NoticeTerms, ctx: _EventHandlerCtx
) -> date:
    """Return the last day of the employment, the event checked against it.

    Returns:
        The last day of the employment.

    Raises:
        InvalidInputError: When the employment has no end, is not
            open-ended, ends in another month than the run's, or before
            the act.
    """
    ended = terms.ended_on
    if ended is None:
        msg = "NoticeIndemnityEvent needs Employment.employment_period.ended_on"
        raise InvalidInputError(
            msg, field="Employment.employment_period", feature=_FEATURE
        )
    if not terms.permanent:
        msg = "the notice of art. 2118 c.c. ends an open-ended contract only"
        raise InvalidInputError(msg, field="Employment.contract_type", feature=_FEATURE)
    if (ctx.cp.year, ctx.cp.month) != (ended.year, ended.month):
        msg = (
            "NoticeIndemnityEvent must be passed to the run of the month of "
            f"the last day of the employment, {ended:%B %Y}"
        )
        raise InvalidInputError(msg, field="NoticeIndemnityEvent", feature=_FEATURE)
    if event.received_on > ended:
        msg = "NoticeIndemnityEvent.received_on must not follow the last day"
        raise InvalidInputError(
            msg, field="NoticeIndemnityEvent.received_on", feature=_FEATURE
        )
    return ended


def _issue(code: str, message: str, *, fact: str | None = None) -> EventEffect:
    return EventEffect(
        issues=[
            CalculationIssue(
                code=code,
                message=message,
                status=CalculationStatus.INCOMPLETE,
                capability=NOTICE,
                fact=fact,
                cause=IssueCause.RULE,
            )
        ]
    )


def _decision(
    terms: NoticeTerms, reason: str, amount: Decimal, inputs: _Inputs
) -> CalculationDecision:
    return CalculationDecision(
        capability=NOTICE,
        status=CalculationStatus.FINAL,
        reason_code=reason,
        rule=terms.rule,
        rule_version=terms.rule_version,
        inputs=inputs,
        source=terms.source,
        amount=amount,
    )


def _band(
    event: NoticeIndemnityEvent, terms: NoticeTerms
) -> tuple[NoticeBand, int] | EventEffect:
    """Return the CCNL band of the worker and the months of service, or why not.

    Returns:
        The band and the months of service on the day of the act, or the
        ``incomplete`` issue that leaves the indemnity out.
    """
    if terms.rules is None:
        return _issue(
            "notice_rule_missing",
            f"the CCNL ({terms.rule}) states no notice: the indemnity is not computed",
        )
    if terms.seniority is None:
        return _issue(
            "notice_seniority_unknown",
            "the notice band depends on the service of the worker, which "
            "Employment.seniority does not state: the indemnity is not computed",
            fact="seniority",
        )
    months = terms.seniority.months_at(event.received_on)
    band = terms.rules.band(terms.level, TerminationCause.DISMISSAL, months)
    if band is None:
        return _issue(
            "notice_band_missing",
            f"the CCNL notice has no band for level {terms.level}: the "
            "indemnity is not computed",
        )
    return band, months


def _cause(terms: NoticeTerms) -> tuple[TerminationCause, bool | None] | EventEffect:
    """Return how the employment ends, or the fact it misses.

    Returns:
        The cause and the just cause, or the ``missing_fact`` issue of
        ``ended_by``, or of ``just_cause`` on a dismissal or a resignation.
    """
    cause = terms.ended_by
    if cause is None:
        return _issue(
            "notice_cause_unknown",
            "who owes the notice depends on how the employment ends "
            "(EmploymentPeriod.ended_by), which is not stated",
            fact="ended_by",
        )
    if cause in _WITH_JUST_CAUSE and terms.just_cause is None:
        return _issue(
            "notice_just_cause_unknown",
            f"a {cause.value} owes the notice according to its just cause "
            "(EmploymentPeriod.just_cause), which is not stated",
            fact="just_cause",
        )
    return cause, terms.just_cause


def _not_owed(
    cause: TerminationCause, terms: NoticeTerms, inputs: _Inputs
) -> EventEffect:
    """Return the effect of a termination whose notice the employer does not owe.

    Returns:
        The issue of a resignation without just cause, or a nil decision.
    """
    if cause is TerminationCause.RESIGNATION:
        return _issue(
            "notice_owed_by_worker",
            "a resignation without just cause and without the notice makes "
            "the worker owe the indemnity to the employer (art. 2118 c.c.), "
            "which the engine does not compute",
        )
    return EventEffect(decisions=[_decision(terms, "notice_not_owed", _ZERO, inputs)])


def _handle_notice_indemnity(
    event: NoticeIndemnityEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the indemnity of the notice not given, when the employer owes it.

    Returns:
        The item, entry, base deltas, decision, issues and limitations.
    """
    terms = ctx.notice
    assert terms is not None, "built by the run"  # pragma: no mutate
    ended = _check(event, terms, ctx)
    stated = _cause(terms)
    if isinstance(stated, EventEffect):
        return stated
    cause, just_cause = stated
    inputs: _Inputs = {
        "cause": cause.value,
        "just_cause": str(just_cause).lower(),
        "received_on": event.received_on.isoformat(),
        "ended_on": ended.isoformat(),
    }
    if not employer_owes(cause, just_cause):
        return _not_owed(cause, terms, inputs)
    found = _band(event, terms)
    if isinstance(found, EventEffect):
        return found
    band, months = found
    rules = terms.rules
    assert rules is not None, "a band comes from the CCNL notice"  # pragma: no mutate
    period = notice_period(band, event.received_on, rules.starts)
    unworked = period.unworked_days(ended)
    pays = band.indemnity_months
    if pays is None:
        pays = Decimal(period.days) / _MONTH_DAYS
    monthly = terms.monthly
    if rules.extra_months_included:
        monthly = monthly * terms.yearly_payments / _MONTHS
    inputs |= {
        "months_of_service": str(months),
        "notice_first_day": period.first_day.isoformat(),
        "notice_last_day": period.last_day.isoformat(),
        "notice_days": str(period.days),
        "unworked_days": str(unworked),
        "indemnity_months": pays,
        "monthly_pay": monthly,
    }
    if not unworked:
        return EventEffect(decisions=[_decision(terms, "notice_worked", _ZERO, inputs)])
    amount = money(monthly * pays * unworked / Decimal(period.days))
    limitations = (
        *((PARTIAL,) if unworked < period.days else ()),
        *(() if rules.extra_months_included else (EXTRA_MONTHS,)),
        *((DAY_MEASURE,) if band.indemnity_months is None else ()),
    )
    return _post(amount, terms, inputs, ctx, limitations, tfr=rules.tfr_base is True)


def _post(
    amount: Decimal,
    terms: NoticeTerms,
    inputs: _Inputs,
    ctx: _EventHandlerCtx,
    limitations: tuple[str, ...],
    *,
    tfr: bool,
) -> EventEffect:
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    treatment = _treatment_from_resolution(resolution)
    item = NoticeIndemnityItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    intent = PostingIntent(
        entry_id=f"notice_{ctx.evt_id}",
        source_item_id=ctx.evt_id,
        pay_item_kind=_KIND,
        account=AccountKind.CASH_EARNINGS,
        amount=amount,
        policy_decision_id=resolution.policy_id,
    )
    inps = amount if treatment.inps else _ZERO
    return EventEffect(
        items=[item],
        intents=[intent],
        inps_delta=inps,
        tfr_delta=amount if treatment.tfr and tfr else _ZERO,
        apart_inps_delta=inps,
        decisions=[_decision(terms, "notice_indemnity_due", amount, inputs)],
        limitations=limitations,
    )
