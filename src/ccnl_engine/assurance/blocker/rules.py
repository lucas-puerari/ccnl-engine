"""The blocker of each cause and what the caller does about it."""

from __future__ import annotations

from ccnl_engine.assurance.models import BlockerCode, ResultBlocker
from ccnl_engine.decision.models import PUBLIC_FACTS
from ccnl_engine.limitation.types import ALL_TOTALS, ResultTotal

__all__ = ["REVIEW_OVERDUE", "blocker"]

_REMEDIATION: dict[BlockerCode, str] = {
    BlockerCode.CALCULATION_ISSUE: (
        "resolve the condition reported as {detail}, then calculate again"
    ),
    BlockerCode.MISSING_FACT: "supply {field} in the request",
    BlockerCode.MISSING_RULE: (
        "the bundle or the engine lacks the rule behind {detail}: supplying "
        "facts does not resolve it; compute {feature} outside the engine "
        "until the rule is added"
    ),
    BlockerCode.REQUIREMENT_UNRESOLVED: (
        "{feature} is required unless a decision of the run rules it out, and "
        "{detail} was left to its default: supply {detail} (a value that "
        "rules {feature} out is a fact too)"
    ),
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


#: Remediation of a ``production`` ruleset whose review was due before the
#: payment date: the blocker keeps the code and detail of any ruleset short
#: of production, only the reason differs.
REVIEW_OVERDUE = (
    "{detail} was due for review on {review_due}, before the payment date "
    "{payment_date}, so it no longer counts as production: review it and move "
    "verification.review_due forward, install a bundle that does, or "
    "calculate in simulation mode"
)


def blocker(
    code: BlockerCode,
    feature: str | None,
    detail: str,
    totals: frozenset[ResultTotal] = ALL_TOTALS,
) -> ResultBlocker:
    """Return the blocker of ``code`` with the remediation of its kind.

    Returns:
        The blocker; a fact as ``detail`` is named by its public field.
    """
    remediation = _REMEDIATION[code].format(
        feature=feature or "the run",
        detail=detail,
        field=PUBLIC_FACTS.get(str(detail), detail),
    )
    return ResultBlocker(code, feature, str(detail), remediation, totals)
