"""What the notice indemnity of a run is computed from."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import Permanent

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.employment.period.inputs import TerminationCause
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.seniority.inputs import SeniorityFact
    from ccnl_engine.termination.notice.models import NoticeRules

__all__ = ["NoticeTerms", "notice_terms"]


@dataclass(frozen=True)
class NoticeTerms:
    """The CCNL notice and the facts of the worker it is read with.

    Attributes:
        rules: The CCNL notice, ``None`` when the CCNL states none.
        level: Level of the worker.
        seniority: Recognised service, ``None`` when not stated.
        ended_on: Last day of the employment, ``None`` when not stated.
        ended_by: How the employment ends, ``None`` when not stated.
        just_cause: Whether a dismissal or resignation has a just cause.
        permanent: Whether the contract is open-ended.
        monthly: Monthly pay of art. 2121 c.c.: base salary, seniority and
            cash allowances of the worker's month.
        yearly_payments: Monthly payments of a year (13 with the 13th, 14
            with the 14th).
        rule: Identifier of the CCNL rule.
        rule_version: Version of the CCNL ruleset.
        source: Location of the clause, if recorded.
    """

    rules: NoticeRules | None
    level: str
    seniority: SeniorityFact | None
    ended_on: date | None
    ended_by: TerminationCause | None
    just_cause: bool | None
    permanent: bool
    monthly: Decimal
    yearly_payments: Decimal
    rule: str
    rule_version: str
    source: SourceLocation | None = None


def notice_terms(ctx: RunContext) -> NoticeTerms:
    """Return the notice terms of the run.

    Returns:
        The terms; their ``rules`` are ``None`` without a CCNL notice.
    """
    ccnl, request = ctx.contract.ccnl, ctx.request
    work = ccnl.work_rules
    rules = None if work is None else work.notice
    chain = ctx.regular_chain
    period = request.employment_period
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    year = ctx.contract.tctx.competence.year
    return NoticeTerms(
        rules=rules,
        level=request.level_code,
        seniority=request.seniority,
        ended_on=None if period is None else period.ended_on,
        ended_by=None if period is None else period.ended_by,
        just_cause=None if period is None else period.just_cause,
        permanent=isinstance(request.contract_type, Permanent),
        monthly=chain.base + chain.seniority + chain.allowances_total,
        yearly_payments=ccnl.parameters.additional_months.value_at(
            ctx.contract.tctx.competence
        ),
        rule=f"{name}:work_rules.notice",
        rule_version=str(year) if ccnl.ruleset is None else ccnl.ruleset.version,
        source=None if rules is None else rules.provenance.location,
    )
