"""Assessment of a run under each mode: readiness blocks only operational."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.domain.assessment import NO_TRACKED_READINESS, assess
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.capability_report import CapabilityReport
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetReadiness,
    VerificationStatus,
)
from tests.fixtures.rulesets import ccnl_ruleset, tax_ruleset

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.assurance import ResultAssurance
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance

_SIMULATION = EngineMode.SIMULATION
_OPERATIONAL = EngineMode.OPERATIONAL
_TAX = tax_ruleset("tax/2026/industria")
_PRODUCTION = ccnl_ruleset(RulesetReadiness.PRODUCTION)


def _clean_run(
    rulesets: tuple[RulesetAssurance, ...], mode: EngineMode
) -> ResultAssurance:
    """Assess a run that nothing but readiness could block.

    Returns:
        The assurance of the run.
    """
    report = CapabilityReport(
        catalog_year=2026,
        gaps=(),
        rule_sources={"irpef": ProvenanceStatus.DERIVED},
        caller_supplied={},
    )
    return assess((), (), report, rulesets, mode)


def _readiness_details(assurance: ResultAssurance) -> list[str]:
    return [
        b.detail
        for b in assurance.blockers
        if b.code is BlockerCode.RULESET_NOT_PRODUCTION
    ]


@pytest.mark.parametrize("mode", list(EngineMode))
def test_a_production_ccnl_is_payable_in_both_modes(mode: EngineMode) -> None:
    """Operational adds nothing when every tracked ruleset is production."""
    assurance = _clean_run((_PRODUCTION, _TAX), mode)

    assert assurance.is_payable
    assert assurance.mode is mode
    assert assurance.rulesets == (_PRODUCTION, _TAX)


@pytest.mark.parametrize(
    ("readiness", "confidence"),
    [
        (RulesetReadiness.EXPLORATORY, VerificationStatus.UNVERIFIED),
        (RulesetReadiness.REVIEWED, VerificationStatus.VERIFIED),
        (RulesetReadiness.REVIEWED, VerificationStatus.UNVERIFIED),
        (RulesetReadiness.PRODUCTION, VerificationStatus.UNVERIFIED),
    ],
)
def test_a_ccnl_short_of_production_blocks_only_operational(
    readiness: RulesetReadiness, confidence: VerificationStatus
) -> None:
    """Simulation reports the tier; operational blocks on it."""
    rulesets = (ccnl_ruleset(readiness, confidence, "ccnl/y"), _TAX)

    simulated = _clean_run(rulesets, _SIMULATION)
    operational = _clean_run(rulesets, _OPERATIONAL)

    assert simulated.is_payable
    assert not operational.is_payable
    assert _readiness_details(operational) == ["ccnl/y"]
    (blocker,) = operational.blockers
    assert blocker.feature is None
    assert "simulation mode" in blocker.remediation


def test_untracked_rulesets_never_raise_a_readiness_blocker() -> None:
    """Tax readiness is not tracked: only the CCNL tier is enforced."""
    assurance = _clean_run((_PRODUCTION, _TAX, tax_ruleset("tax/x")), _OPERATIONAL)

    assert _readiness_details(assurance) == []


def test_operational_fails_closed_without_a_tracked_ruleset() -> None:
    """A run whose CCNL identity is missing cannot be cleared."""
    simulated = _clean_run((_TAX,), _SIMULATION)
    operational = _clean_run((_TAX,), _OPERATIONAL)

    assert simulated.is_payable
    assert _readiness_details(operational) == [NO_TRACKED_READINESS]
    assert not operational.is_payable
