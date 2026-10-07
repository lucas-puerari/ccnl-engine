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
from ccnl_engine.payroll.domain.capability_report import CapabilityReport
from ccnl_engine.payroll.domain.requirements import (
    UnresolvedRequirement,
    unresolved_requirements,
)

_REGIONE = "facts.regione"
_UNKNOWN = frozenset({_REGIONE})
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
    """Nothing ruled the surtax out and the residence is unknown: unresolved."""
    unresolved = unresolved_requirements(_CATALOG, frozenset(), _UNKNOWN)
    assert unresolved == (UnresolvedRequirement("addizionale_regionale", _REGIONE),)


def test_a_supplied_fact_resolves_the_requirement() -> None:
    """With the residence stated, the surtax is decided on it."""
    assert unresolved_requirements(_CATALOG, frozenset(), frozenset()) == ()


def test_a_decision_rules_a_capability_out() -> None:
    """An employer that does not withhold decides the surtax is not owed."""
    ruled_out = frozenset({"addizionale_regionale"})
    assert unresolved_requirements(_CATALOG, ruled_out, _UNKNOWN) == ()


def test_an_unresolved_requirement_makes_the_coverage_incomplete() -> None:
    """A required capability nothing resolved is not covered."""
    report = CapabilityReport(
        2026,
        (),
        unresolved=(UnresolvedRequirement("addizionale_regionale", _REGIONE),),
    )
    assert report.status is CoverageStatus.INCOMPLETE
    assert CapabilityReport.empty(2026).status is CoverageStatus.COMPLETE
