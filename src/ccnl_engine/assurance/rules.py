"""Assessment of one run: its assurance derived from what it recorded.

The assessment is fail-closed.  The capability report holds, besides the
gaps of the capabilities that apply, the capabilities required in every run
whose applicability fact was left to its default and that no decision of
the run ruled out (:mod:`~ccnl_engine.capability.requirement.rules`): a
default never decides a capability.  Each such requirement and each recorded condition
is one :class:`~ccnl_engine.assurance.models.ResultBlocker`:

- an issue, whatever its status: ``missing_fact`` when it names the fact,
  ``missing_rule`` when its cause is a rule the bundle or the engine lacks,
  ``calculation_issue`` otherwise;
- a decision that is not final;
- a required capability whose applicability fact was left to its default
  (``requirement_unresolved``);
- a gap of the capability report;
- an executed capability whose weakest rule is weaker than the evidence
  its registry entry accepts (``derived`` for every capability today), or
  a run whose rules carry no provenance record;
- a capability that took a caller value in place of a rule;
- an open model limitation with a monetary impact (``yes`` or
  ``unknown``) that concerns the run; it leaves unreliable only the totals
  the limitation names;
- in ``operational`` mode only, a ruleset that tracks a readiness tier and
  is not ``production``, or a run where no ruleset tracks one (the CCNL
  identity is missing): the run fails closed;
- in ``operational`` mode only, a ``production`` ruleset whose next review
  was due before the payment date of the run: the tier is no longer
  current for that run, whatever the installed bundle says.

A cause is reported once.  A missing fact keeps its key of
:data:`~ccnl_engine.decision.models.PUBLIC_FACTS` as detail, names its public
field (``Employment.seniority``) in the remediation and the capability it
leaves open as feature; the other blockers of that capability (its decision that is not
final, its gap) follow from the fact and are not repeated.  Likewise an
issue or a non-final decision of a capability makes its gap redundant.

A ``derived`` rule lowers the evidence axis but does not block on its own:
the bundle holds no ``verified`` rule yet, so requiring one would block every
result without telling them apart.  For the same reason ``simulation`` mode
reports readiness without enforcing it.  Rulesets that track no tier (tax,
INPS, surtax) never raise a readiness blocker: their evidence is the
provenance of each rule.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.assurance.blocker.rules import REVIEW_OVERDUE, blocker
from ccnl_engine.assurance.models import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    ResultAssurance,
    ResultBlocker,
    decide_payability,
)
from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.decision.models import CalculationStatus, IssueCause

if TYPE_CHECKING:
    import datetime as dt

    from ccnl_engine.capability.results import CapabilityReport
    from ccnl_engine.decision.models import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.limitation.models import ModelLimitation
    from ccnl_engine.provenance.ruleset.assurance.models import RulesetAssurance

__all__ = ["assess", "assess_nothing_computed"]


def assess(
    issues: tuple[CalculationIssue, ...],
    decisions: tuple[CalculationDecision, ...],
    report: CapabilityReport,
    rulesets: tuple[RulesetAssurance, ...],
    mode: EngineMode,
    payment_date: dt.date,
    limitations: tuple[ModelLimitation, ...] = (),
) -> ResultAssurance:
    """Derive the assurance of one run from what the run recorded.

    Args:
        issues: Issues of the run.
        decisions: Decisions of the run.
        report: Capability report of the run.
        rulesets: Rulesets the payable rules of the run came from.
        mode: Payability policy of the engine.
        payment_date: Payment date of the run; in ``operational`` mode a
            ruleset whose review was due before it is not production.
        limitations: Model limitations that concern the run.

    Returns:
        The assurance of the run.
    """
    blockers = _one_per_cause((
        *(_issue_blocker(issue) for issue in issues),
        *(
            blocker(BlockerCode.CALCULATION_ISSUE, d.capability, d.reason_code)
            for d in decisions
            if d.status is not CalculationStatus.FINAL
        ),
        *_coverage_blockers(report),
        *_evidence_blockers(report),
        *(
            blocker(BlockerCode.CALLER_SUPPLIED_RULE, feature, ",".join(fields))
            for feature, fields in report.caller_supplied.items()
        ),
        *_readiness_blockers(rulesets, mode, payment_date),
        *(
            blocker(BlockerCode.OPEN_LIMITATION, lim.capability, lim.id, lim.totals)
            for lim in limitations
            if lim.blocks
        ),
    ))
    return ResultAssurance(
        calculation=CalculationStatus.worst((
            *(i.status for i in issues),
            *(d.status for d in decisions),
        )),
        coverage=report.status,
        evidence=EvidenceStatus.weakest(report.rule_sources.values()),
        rulesets=rulesets,
        mode=mode,
        payability=decide_payability(blockers),
        blockers=blockers,
        limitations=limitations,
    )


def assess_nothing_computed(mode: EngineMode) -> ResultAssurance:
    """Derive the assurance of a sequence of payments that computed none.

    Nothing was computed, so nothing was covered and no rule was read: the
    policy of a run whose rules carry no provenance record applies, and in
    ``operational`` mode no ruleset tracks a readiness tier.  The result is
    never payable.

    Returns:
        The assurance, ``incomplete`` with ``missing`` evidence.
    """
    blockers = (
        blocker(BlockerCode.RULE_SOURCE_WEAK, None, EvidenceStatus.MISSING),
        *_untracked_readiness_blockers(mode),
    )
    return ResultAssurance(
        calculation=CalculationStatus.FINAL,
        coverage=CoverageStatus.INCOMPLETE,
        evidence=EvidenceStatus.MISSING,
        rulesets=(),
        mode=mode,
        payability=decide_payability(blockers),
        blockers=blockers,
    )


def _coverage_blockers(report: CapabilityReport) -> tuple[ResultBlocker, ...]:
    return (
        *(
            blocker(BlockerCode.REQUIREMENT_UNRESOLVED, req.feature, req.fact)
            for req in report.unresolved
        ),
        *(
            blocker(BlockerCode.CAPABILITY_NOT_COMPUTED, gap.feature, gap.kind)
            for gap in report.gaps
        ),
    )


def _evidence_blockers(report: CapabilityReport) -> tuple[ResultBlocker, ...]:
    if not report.rule_sources:
        return (blocker(BlockerCode.RULE_SOURCE_WEAK, None, EvidenceStatus.MISSING),)
    return tuple(
        blocker(BlockerCode.RULE_SOURCE_WEAK, feature, status)
        for feature, status in report.weak_sources().items()
    )


#: Detail of the blocker of a run where no ruleset tracks a readiness tier.
NO_TRACKED_READINESS = "no_ruleset_tracks_readiness"


def _untracked_readiness_blockers(mode: EngineMode) -> tuple[ResultBlocker, ...]:
    if mode is EngineMode.SIMULATION:
        return ()
    return (blocker(BlockerCode.RULESET_NOT_PRODUCTION, None, NO_TRACKED_READINESS),)


def _readiness_blockers(
    rulesets: tuple[RulesetAssurance, ...],
    mode: EngineMode,
    payment_date: dt.date,
) -> tuple[ResultBlocker, ...]:
    tracked = tuple(r for r in rulesets if r.readiness_tracked)
    if mode is EngineMode.SIMULATION or not tracked:
        return _untracked_readiness_blockers(mode)
    return tuple(
        found
        for r in tracked
        if (found := _readiness_blocker(r, payment_date)) is not None
    )


def _readiness_blocker(
    ruleset: RulesetAssurance, payment_date: dt.date
) -> ResultBlocker | None:
    if not ruleset.is_production:
        return blocker(BlockerCode.RULESET_NOT_PRODUCTION, None, ruleset.id)
    if not ruleset.review_overdue(payment_date):
        return None
    remediation = REVIEW_OVERDUE.format(
        detail=ruleset.id, review_due=ruleset.review_due, payment_date=payment_date
    )
    return ResultBlocker(
        BlockerCode.RULESET_NOT_PRODUCTION, None, ruleset.id, remediation
    )


def _issue_blocker(issue: CalculationIssue) -> ResultBlocker:
    if issue.fact is not None:
        return blocker(BlockerCode.MISSING_FACT, issue.capability, issue.fact)
    if issue.cause is IssueCause.RULE:
        return blocker(BlockerCode.MISSING_RULE, issue.capability, issue.code)
    return blocker(BlockerCode.CALCULATION_ISSUE, issue.capability, issue.code)


#: Blockers of a capability from the most to the least specific cause: a
#: capability keeps only the blockers of its most specific rank.
_CAUSE_RANK: dict[BlockerCode, int] = {
    BlockerCode.MISSING_FACT: 0,
    BlockerCode.REQUIREMENT_UNRESOLVED: 0,
    BlockerCode.CALCULATION_ISSUE: 1,
    BlockerCode.MISSING_RULE: 1,
    BlockerCode.CAPABILITY_NOT_COMPUTED: 2,
}


def _one_per_cause(blockers: tuple[ResultBlocker, ...]) -> tuple[ResultBlocker, ...]:
    """Drop the blockers that repeat a more specific cause of their capability.

    Returns:
        ``blockers`` in order, without duplicates and without the ranked
        blockers of a capability that has one of a more specific rank.
    """
    best: dict[str, int] = {}
    for b in blockers:
        if b.feature is not None and b.code in _CAUSE_RANK:
            best[b.feature] = min(best.get(b.feature, 2), _CAUSE_RANK[b.code])
    kept = (
        b
        for b in blockers
        if b.feature is None
        or b.code not in _CAUSE_RANK
        or _CAUSE_RANK[b.code] == best[b.feature]
    )
    return tuple(dict.fromkeys(kept))
