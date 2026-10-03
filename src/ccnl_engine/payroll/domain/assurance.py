"""Assurance of a payroll result: can its amounts be paid as they are.

A result answers one question for an integration: may this amount be paid?
:class:`ResultAssurance` is the only answer.  It is derived from what the run
already records, never stored beside it:

- ``calculation``: the worst status of the issues and decisions of the run;
- ``coverage``: the status of the capability report, the gaps between the
  capability registry and what the run executed, for the capabilities that
  apply to it;
- ``evidence``: the weakest provenance of the payable rules the run read;
- ``rulesets``: the identity, readiness and confidence of each ruleset
  those rules came from;
- ``mode``: the payability policy of the engine that produced the result;
- ``blockers``: every reason the amounts cannot be paid.

The result is payable only when nothing blocks it.  How a run is assessed is
in :mod:`~ccnl_engine.payroll.domain.assessment`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.payroll.domain.engine_mode import EngineMode
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance

__all__ = [
    "BlockerCode",
    "CoverageStatus",
    "EvidenceStatus",
    "Payability",
    "ResultAssurance",
    "ResultBlocker",
    "decide_payability",
]


class CoverageStatus(StrEnum):
    """How far the run covers the capabilities that apply to it.

    Members are listed from the best to the worst coverage.

    Attributes:
        COMPLETE: Every applicable capability was computed in full.
        PARTIAL: Every gap is a partial result or a partially implemented
            capability that executed.
        INCOMPLETE: An applicable capability is unsupported, untraced or
            could not decide.
    """

    COMPLETE = "complete"
    PARTIAL = "partial"
    INCOMPLETE = "incomplete"

    @classmethod
    def worst(cls, statuses: Iterable[CoverageStatus]) -> CoverageStatus:
        """Return the worst coverage in ``statuses``.

        Returns:
            The worst status, or :attr:`COMPLETE` when ``statuses`` is empty.
        """
        order = list(cls)
        return max(statuses, key=order.index, default=cls.COMPLETE)


class EvidenceStatus(StrEnum):
    """How far the payable rules a run read are backed by their sources.

    The values are those of the rule provenance status, listed from the
    strongest to the weakest backing.

    Attributes:
        VERIFIED: Every rule was checked by a named person.
        DERIVED: The weakest rule is taken from a cited location, unchecked.
        ASSUMED: A rule is adopted without a located citation.
        MISSING: A rule has no source, or no rule carries a record.
    """

    VERIFIED = "verified"
    DERIVED = "derived"
    ASSUMED = "assumed"
    MISSING = "missing"

    @classmethod
    def weakest(cls, statuses: Iterable[str]) -> EvidenceStatus:
        """Return the weakest of ``statuses``, given as provenance values.

        Returns:
            The weakest status, or :attr:`MISSING` when ``statuses`` is empty:
            nothing backs a run whose rules carry no record.
        """
        order = list(cls)
        return max(map(cls, statuses), key=order.index, default=cls.MISSING)


class Payability(StrEnum):
    """Whether the amounts of a result can be paid as they are.

    Attributes:
        PAYABLE: Nothing blocks the amounts.
        NOT_PAYABLE: At least one :class:`ResultBlocker` applies.
    """

    PAYABLE = "payable"
    NOT_PAYABLE = "not_payable"


class BlockerCode(StrEnum):
    """Stable machine-readable kind of a :class:`ResultBlocker`.

    Attributes:
        CALCULATION_ISSUE: An issue was raised, or a decision is not final:
            an amount rests on an assumption, a fallback or a condition the
            worker must be told about.
        MISSING_FACT: A fact the calculation needs was not supplied.
        CAPABILITY_NOT_COMPUTED: A capability the catalog promises was not
            computed, could not decide or came out partial.
        RULE_SOURCE_WEAK: An executed capability read a rule whose
            provenance is ``assumed`` or ``missing``, or no rule of the run
            carries a provenance record.
        CALLER_SUPPLIED_RULE: The caller supplied a value in place of a rule
            of the bundle, so no source backs it.
        RULESET_NOT_PRODUCTION: In ``operational`` mode only: a ruleset the
            run read is not ``production``, or no ruleset of the run tracks
            a readiness tier.
    """

    CALCULATION_ISSUE = "calculation_issue"
    MISSING_FACT = "missing_fact"
    CAPABILITY_NOT_COMPUTED = "capability_not_computed"
    RULE_SOURCE_WEAK = "rule_source_weak"
    CALLER_SUPPLIED_RULE = "caller_supplied_rule"
    RULESET_NOT_PRODUCTION = "ruleset_not_production"


@dataclass(frozen=True, slots=True)
class ResultBlocker:
    """One reason the amounts of a result cannot be paid.

    Attributes:
        code: Kind of blocker; callers may branch on it.
        feature: Capability the blocker concerns, ``None`` when it concerns
            the run as a whole (an issue, a missing fact).
        detail: Machine-readable specifics in lower snake case where the
            source allows: the issue code, the decision reason, the missing
            fact, the gap kind, the provenance status, the caller fields, or
            the id of the ruleset short of ``production``.
        remediation: What removes the blocker, for a human reader.
    """

    code: BlockerCode
    feature: str | None
    detail: str
    remediation: str


@dataclass(frozen=True, slots=True)
class ResultAssurance:
    """Whether the amounts of a result can be relied upon and paid.

    Attributes:
        calculation: Worst status of the issues and decisions.
        coverage: Status of the capability report.
        evidence: Weakest provenance of the payable rules read;
            ``missing`` when no rule carries a record.
        rulesets: Assurance of the rulesets the rules were read from:
            identity, hash, readiness and confidence.
        mode: Payability policy the blockers were derived under.
        payability: :attr:`Payability.PAYABLE` exactly when
            :attr:`blockers` is empty.
        blockers: Every reason the amounts cannot be paid, in the order
            they were found.
    """

    calculation: CalculationStatus
    coverage: CoverageStatus
    evidence: EvidenceStatus
    rulesets: tuple[RulesetAssurance, ...]
    mode: EngineMode
    payability: Payability
    blockers: tuple[ResultBlocker, ...]

    @property
    def is_payable(self) -> bool:
        """Whether nothing blocks the amounts."""
        return self.payability is Payability.PAYABLE

    @classmethod
    def combine(cls, assurances: Iterable[ResultAssurance]) -> ResultAssurance:
        """Aggregate the assurance of several runs, e.g. those of a year.

        Each axis takes its worst value; rulesets and blockers are listed
        once each, in the order they first appear.

        Returns:
            The aggregated assurance.

        Raises:
            ValueError: When ``assurances`` is empty, or mixes modes.
        """
        items = tuple(assurances)
        if not items:
            msg = "cannot combine the assurance of no run"
            raise ValueError(msg)
        modes = {a.mode for a in items}
        if len(modes) > 1:
            msg = f"cannot combine runs of different modes: {sorted(modes)}"
            raise ValueError(msg)
        blockers = tuple(dict.fromkeys(b for a in items for b in a.blockers))
        return cls(
            calculation=CalculationStatus.worst(a.calculation for a in items),
            coverage=CoverageStatus.worst(a.coverage for a in items),
            evidence=EvidenceStatus.weakest(a.evidence for a in items),
            rulesets=_unique_rulesets(r for a in items for r in a.rulesets),
            mode=items[0].mode,
            payability=decide_payability(blockers),
            blockers=blockers,
        )


def _unique_rulesets(
    rulesets: Iterable[RulesetAssurance],
) -> tuple[RulesetAssurance, ...]:
    seen: dict[str, RulesetAssurance] = {}
    for ruleset in rulesets:
        seen.setdefault(str(ruleset), ruleset)
    return tuple(seen.values())


def decide_payability(blockers: tuple[ResultBlocker, ...]) -> Payability:
    """Apply the payability policy to the blockers of a result.

    Every blocker blocks; this is the single place a stricter or looser
    policy would change the outcome.  The mode acts earlier: ``operational``
    adds the ``ruleset_not_production`` blockers (see
    :mod:`~ccnl_engine.payroll.domain.assessment`).

    Returns:
        :attr:`Payability.PAYABLE` when there is no blocker.
    """
    return Payability.NOT_PAYABLE if blockers else Payability.PAYABLE
