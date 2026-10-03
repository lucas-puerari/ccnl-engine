"""Capability registry of a fiscal year: the single source of coverage.

Every capability the engine knows is one :class:`CapabilityEntry`.  The
entry says how the engine implements it, when it applies to a run, which
handler owns its decision and traces it, which variants and facts it needs
and the evidence its rules must reach.  The runtime capability report, the
contracts index and the capability matrix all derive from these entries;
no other flag declares coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.assurance import EvidenceStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = [
    "CapabilityApplicability",
    "CapabilityCatalog",
    "CapabilityEntry",
    "CapabilityHandler",
    "CapabilityImplementation",
    "CapabilityLayer",
]


class CapabilityImplementation(StrEnum):
    """How the engine implements a capability, from the best to the worst.

    Attributes:
        NATIVE: Computed from bundled rules and the facts of the request.
        CALLER_SUPPLIED: Computed from a rate or amount the caller supplies
            in place of a rule.
        PARTIAL: Computed for the listed variants only; a run that executes
            it is partially covered.
        UNSUPPORTED: Not computed; a run it applies to is not covered.
    """

    NATIVE = "native"
    CALLER_SUPPLIED = "caller_supplied"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"

    @classmethod
    def worst(
        cls, implementations: Iterable[CapabilityImplementation]
    ) -> CapabilityImplementation:
        """Return the worst of ``implementations``.

        Returns:
            The worst implementation, or :attr:`NATIVE` when empty.
        """
        order = list(cls)
        return max(implementations, key=order.index, default=cls.NATIVE)


class CapabilityLayer(StrEnum):
    """Payslip layer a capability belongs to, for grouping in reports.

    Attributes:
        GROSS: Pay elements (L1).
        NET: Contributions, taxes and deductions (L2).
        WORK_RULES: Work-time, absence and benefit events (L3).
    """

    GROSS = "gross"
    NET = "net"
    WORK_RULES = "work_rules"


class CapabilityApplicability(StrEnum):
    """Predicate that says whether a capability applies to a run.

    Attributes:
        ALWAYS: Every run, unless its handler rules it out (an employer
            that does not withhold tax).
        DECIDED: Its decision owner decides: it applies when the run took a
            decision for it that does not rule it out.
        EVENT: The request declares an event of the capability.
        TERMINATION_RUN: The run closes the employment: a termination run,
            or the regular run of the month the employment ends in.
        OUTSIDE_INPUT: The fact that makes it apply has no field in the
            request: a case with that fact is outside the engine input.
    """

    ALWAYS = "always"
    DECIDED = "decided"
    EVENT = "event"
    TERMINATION_RUN = "termination_run"
    OUTSIDE_INPUT = "outside_input"


class CapabilityHandler(StrEnum):
    """Kind of code that owns the decision of a capability and traces it.

    Attributes:
        PIPELINE: A stage every run executes.
        EVENT: The handler of an event type.
        DECISION: A step that records a decision for the capability.
    """

    PIPELINE = "pipeline"
    EVENT = "event"
    DECISION = "decision"


#: Handler each applicability predicate is evaluated from.
_HANDLER_OF: dict[CapabilityApplicability, CapabilityHandler] = {
    CapabilityApplicability.ALWAYS: CapabilityHandler.PIPELINE,
    CapabilityApplicability.DECIDED: CapabilityHandler.DECISION,
    CapabilityApplicability.EVENT: CapabilityHandler.EVENT,
}


@dataclass(frozen=True)
class CapabilityEntry:
    """One capability of the registry.

    Attributes:
        feature: Stable capability name, as traced and reported.
        layer: Payslip layer the capability belongs to.
        implementation: How the engine implements it.
        applies_when: Predicate that says whether it applies to a run.
        handler: Kind of code that decides and traces it; ``None`` exactly
            when the capability is unsupported.
        evidence: Weakest provenance its rules may have for a payable run.
        description: Human-readable description.
        variants: Variants the engine supports, for a partial capability
            the only ones it computes.
        required_facts: Request facts the capability reads; for an
            ``outside_input`` capability, the fact the request lacks.

    Raises:
        ValueError: When the handler disagrees with the implementation or
            with the applicability predicate.
    """

    feature: str
    layer: CapabilityLayer
    implementation: CapabilityImplementation
    applies_when: CapabilityApplicability
    handler: CapabilityHandler | None
    evidence: EvidenceStatus = EvidenceStatus.DERIVED
    description: str = ""
    variants: tuple[str, ...] = ()
    required_facts: tuple[str, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        unsupported = self.implementation is CapabilityImplementation.UNSUPPORTED
        if unsupported != (self.handler is None):
            msg = (
                f"capability {self.feature!r}: an unsupported capability has no "
                f"handler and every other one has one; got {self.implementation} "
                f"with handler {self.handler}"
            )
            raise ValueError(msg)
        expected = _HANDLER_OF.get(self.applies_when)
        if not unsupported and expected is not None and self.handler is not expected:
            msg = (
                f"capability {self.feature!r}: applies_when {self.applies_when} "
                f"is decided by a {expected} handler, not {self.handler}"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class CapabilityCatalog:
    """Capability registry of one fiscal year.

    Raises:
        ValueError: When two entries share a feature.
    """

    year: int
    capabilities: tuple[CapabilityEntry, ...]

    def __post_init__(self) -> None:  # noqa: D105
        features = [entry.feature for entry in self.capabilities]
        duplicates = sorted({f for f in features if features.count(f) > 1})
        if duplicates:
            msg = f"capability catalog {self.year}: duplicate features {duplicates}"
            raise ValueError(msg)

    def by_feature(self, feature: str) -> CapabilityEntry | None:
        """Return the entry for *feature*, or ``None`` when absent.

        Returns:
            The matching :class:`CapabilityEntry`, or ``None``.
        """
        for cap in self.capabilities:
            if cap.feature == feature:
                return cap
        return None

    def implemented(self) -> tuple[CapabilityEntry, ...]:
        """Return the entries the engine computes, in declaration order.

        Returns:
            Every entry that is not unsupported.
        """
        return tuple(
            entry
            for entry in self.capabilities
            if entry.implementation is not CapabilityImplementation.UNSUPPORTED
        )
