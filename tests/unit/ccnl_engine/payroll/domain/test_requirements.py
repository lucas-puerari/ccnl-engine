"""Required capabilities a run neither computed nor ruled out."""

from __future__ import annotations

from ccnl_engine.payroll.domain.assurance import CoverageStatus
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)
from ccnl_engine.payroll.domain.capability_report import (
    CapabilityReport,
    CapabilityScope,
)
from ccnl_engine.payroll.domain.requirements import (
    UnresolvedRequirement,
    unresolved_requirements,
)

_REGIONE = "facts.regione"
_NOT_APPLICABLE = {"addizionale_regionale": CapabilityScope.NOT_APPLICABLE}
_CATALOG = CapabilityCatalog(
    2026,
    (
        CapabilityEntry(
            "addizionale_regionale",
            CapabilityLayer.NET,
            CapabilityImplementation.NATIVE,
            CapabilityApplicability.DECIDED,
            CapabilityHandler.DECISION,
            required_facts=(_REGIONE,),
            applicability_facts=(_REGIONE,),
        ),
        CapabilityEntry(
            "irpef",
            CapabilityLayer.NET,
            CapabilityImplementation.NATIVE,
            CapabilityApplicability.ALWAYS,
            CapabilityHandler.PIPELINE,
        ),
    ),
)


def test_a_default_does_not_rule_a_capability_out() -> None:
    """Not applicable, no decision, residence left unknown: unresolved."""
    unresolved = unresolved_requirements(
        _CATALOG, _NOT_APPLICABLE, frozenset(), frozenset({_REGIONE})
    )
    assert unresolved == (UnresolvedRequirement("addizionale_regionale", _REGIONE),)


def test_a_supplied_fact_rules_a_capability_out() -> None:
    """With the residence stated, a capability left not applicable stands."""
    assert (
        unresolved_requirements(_CATALOG, _NOT_APPLICABLE, frozenset(), frozenset())
        == ()
    )


def test_a_decision_rules_a_capability_out() -> None:
    """An employer that does not withhold decides the surtax is not owed."""
    decided = frozenset({"addizionale_regionale"})
    unresolved = unresolved_requirements(
        _CATALOG, _NOT_APPLICABLE, decided, frozenset({_REGIONE})
    )
    assert unresolved == ()


def test_a_computed_capability_is_resolved() -> None:
    """An applicable capability is covered by its gaps, not by a requirement."""
    applicable = {"addizionale_regionale": CapabilityScope.APPLICABLE}
    unresolved = unresolved_requirements(
        _CATALOG, applicable, frozenset(), frozenset({_REGIONE})
    )
    assert unresolved == ()


def test_an_unresolved_requirement_makes_the_coverage_incomplete() -> None:
    """A required capability nothing resolved is not covered."""
    report = CapabilityReport(
        2026,
        (),
        unresolved=(UnresolvedRequirement("addizionale_regionale", _REGIONE),),
    )
    assert report.status is CoverageStatus.INCOMPLETE
    assert CapabilityReport.empty(2026).status is CoverageStatus.COMPLETE
