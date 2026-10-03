"""Assessment of one run: its assurance derived from what it recorded.

Each recorded condition is one :class:`~ccnl_engine.payroll.domain.assurance\
.ResultBlocker`:

- an issue, whatever its status; a ``missing_fact`` blocker when the issue
  names the fact;
- a decision that is not final;
- a gap of the capability report;
- an executed capability whose weakest rule is weaker than the evidence
  its registry entry accepts (``derived`` for every capability today), or
  a run whose rules carry no provenance record;
- a capability that took a caller value in place of a rule;
- an open model limitation with a monetary impact (``yes`` or
  ``unknown``) that concerns the run;
- in ``operational`` mode only, a ruleset that tracks a readiness tier and
  is not ``production``, or a run where no ruleset tracks one (the CCNL
  identity is missing): the run fails closed.

A ``derived`` rule lowers the evidence axis but does not block on its own:
the bundle holds no ``verified`` rule yet, so requiring one would block every
result without telling them apart.  For the same reason ``simulation`` mode
reports readiness without enforcing it.  Rulesets that track no tier (tax,
INPS, surtax) never raise a readiness blocker: their evidence is the
provenance of each rule.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.assurance import (
    BlockerCode,
    EvidenceStatus,
    ResultAssurance,
    ResultBlocker,
    decide_payability,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.engine_mode import EngineMode

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.capability_report import CapabilityReport
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance
    from ccnl_engine.shared.domain.limitation import ModelLimitation

__all__ = ["assess"]


def assess(
    issues: tuple[CalculationIssue, ...],
    decisions: tuple[CalculationDecision, ...],
    report: CapabilityReport,
    rulesets: tuple[RulesetAssurance, ...],
    mode: EngineMode,
    limitations: tuple[ModelLimitation, ...] = (),
) -> ResultAssurance:
    """Derive the assurance of one run from what the run recorded.

    Args:
        issues: Issues of the run.
        decisions: Decisions of the run.
        report: Capability report of the run.
        rulesets: Rulesets the payable rules of the run came from.
        mode: Payability policy of the engine.
        limitations: Model limitations that concern the run.

    Returns:
        The assurance of the run.
    """
    blockers = (
        *(_issue_blocker(issue) for issue in issues),
        *(
            _blocker(BlockerCode.CALCULATION_ISSUE, d.capability, d.reason_code)
            for d in decisions
            if d.status is not CalculationStatus.FINAL
        ),
        *(
            _blocker(BlockerCode.CAPABILITY_NOT_COMPUTED, gap.feature, gap.kind)
            for gap in report.gaps
        ),
        *_evidence_blockers(report),
        *(
            _blocker(BlockerCode.CALLER_SUPPLIED_RULE, feature, ",".join(fields))
            for feature, fields in report.caller_supplied.items()
        ),
        *_readiness_blockers(rulesets, mode),
        *(
            _blocker(BlockerCode.OPEN_LIMITATION, lim.capability, lim.id)
            for lim in limitations
            if lim.blocks
        ),
    )
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


def _evidence_blockers(report: CapabilityReport) -> tuple[ResultBlocker, ...]:
    if not report.rule_sources:
        return (_blocker(BlockerCode.RULE_SOURCE_WEAK, None, EvidenceStatus.MISSING),)
    return tuple(
        _blocker(BlockerCode.RULE_SOURCE_WEAK, feature, status)
        for feature, status in report.weak_sources().items()
    )


#: Detail of the blocker of a run where no ruleset tracks a readiness tier.
NO_TRACKED_READINESS = "no_ruleset_tracks_readiness"


def _readiness_blockers(
    rulesets: tuple[RulesetAssurance, ...], mode: EngineMode
) -> tuple[ResultBlocker, ...]:
    if mode is EngineMode.SIMULATION:
        return ()
    tracked = tuple(r for r in rulesets if r.readiness_tracked)
    if not tracked:
        return (
            _blocker(BlockerCode.RULESET_NOT_PRODUCTION, None, NO_TRACKED_READINESS),
        )
    return tuple(
        _blocker(BlockerCode.RULESET_NOT_PRODUCTION, None, r.id)
        for r in tracked
        if not r.is_production
    )


def _issue_blocker(issue: CalculationIssue) -> ResultBlocker:
    if issue.fact is not None:
        return _blocker(BlockerCode.MISSING_FACT, None, issue.fact)
    return _blocker(BlockerCode.CALCULATION_ISSUE, None, issue.code)


_REMEDIATION: dict[BlockerCode, str] = {
    BlockerCode.CALCULATION_ISSUE: (
        "resolve the condition reported as {detail}, then calculate again"
    ),
    BlockerCode.MISSING_FACT: "supply the fact {detail} in the request",
    BlockerCode.CAPABILITY_NOT_COMPUTED: (
        "{feature} was not computed ({detail}): compute it outside the engine "
        "or confirm it does not apply to this run"
    ),
    BlockerCode.RULE_SOURCE_WEAK: (
        "{feature} read a rule whose source is {detail}: source and review "
        "the rule in the bundle before paying"
    ),
    BlockerCode.CALLER_SUPPLIED_RULE: (
        "{feature} used caller values ({detail}) in place of a bundled rule: "
        "validate them outside the engine"
    ),
    BlockerCode.OPEN_LIMITATION: (
        "{feature} is computed under the open limitation {detail}: check the "
        "amount outside the engine or resolve the limitation"
    ),
    BlockerCode.RULESET_NOT_PRODUCTION: (
        "{detail} is not cleared as production (or no ruleset of the run tracks "
        "readiness): promote it under the readiness criteria, or calculate in "
        "simulation mode"
    ),
}


def _blocker(code: BlockerCode, feature: str | None, detail: str) -> ResultBlocker:
    remediation = _REMEDIATION[code].format(feature=feature or "the run", detail=detail)
    return ResultBlocker(code, feature, str(detail), remediation)
