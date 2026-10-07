"""Required capabilities of a run that no supplied fact resolves.

The capability report lists the gaps of the capabilities that apply to a
run.  That is a blocklist: a capability whose handler took no decision
because a fact was left to its default looks ``not_applicable`` and leaves
no gap.  This module closes the list.  A capability of the registry that
declares ``applicability_facts`` is required in every run: it must be
computed, or ruled out by a decision of the run (e.g. an employer that is
not a withholding agent) or by the supplied facts.  A default never rules
it out, so each of those facts left to its default, on a run where the
capability took no decision, is one :class:`UnresolvedRequirement`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.capability_report import CapabilityScope

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog

__all__ = ["UnresolvedRequirement", "unresolved_requirements"]


@dataclass(frozen=True, slots=True)
class UnresolvedRequirement:
    """A required capability the run neither computed nor ruled out.

    Attributes:
        feature: The capability, as named by the registry.
        fact: The request fact that decides whether it applies, left to its
            default, e.g. ``"facts.regione"``.
    """

    feature: str
    fact: str


def unresolved_requirements(
    catalog: CapabilityCatalog,
    scope: Mapping[str, CapabilityScope],
    decided: frozenset[str],
    absent_facts: frozenset[str],
) -> tuple[UnresolvedRequirement, ...]:
    """Return the required capabilities no decision or supplied fact resolves.

    Args:
        catalog: Capability registry of the run.
        scope: Scope of each capability for the run.
        decided: Capabilities the run took a decision for.
        absent_facts: Request facts left to their default.

    Returns:
        One entry per applicability fact left to its default, for each
        capability that is not applicable without a decision of the run,
        in registry order.
    """
    return tuple(
        UnresolvedRequirement(entry.feature, fact)
        for entry in catalog.capabilities
        if entry.feature not in decided
        and scope.get(entry.feature) is CapabilityScope.NOT_APPLICABLE
        for fact in entry.applicability_facts
        if fact in absent_facts
    )
