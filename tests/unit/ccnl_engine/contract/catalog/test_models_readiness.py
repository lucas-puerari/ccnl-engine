"""Assurance of a CCNL ruleset from its identity and verification."""

from __future__ import annotations

from ccnl_engine.contract.catalog.models_readiness import ccnl_ruleset_assurance
from ccnl_engine.contract.identity.facade import CCNLVerification
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.ruleset.models_assurance import RulesetKind
from tests.unit.ccnl_engine.builders import make_minimal_ccnl
from tests.unit.ccnl_engine.provenance.ruleset.builders_rulesets import ruleset_identity


def test_readiness_and_confidence_come_from_the_verification() -> None:
    """The tier and confidence are those a reviewer recorded."""
    identity = ruleset_identity("ccnl/minimal")
    verification = CCNLVerification(
        confidence=VerificationStatus.UNVERIFIED,
        readiness=RulesetReadiness.REVIEWED,
    )
    ccnl = make_minimal_ccnl().model_copy(
        update={"ruleset": identity, "verification": verification}
    )

    assurance = ccnl_ruleset_assurance(ccnl)

    assert assurance is not None
    assert assurance.identity == identity
    assert assurance.kind is RulesetKind.CCNL
    assert assurance.readiness is RulesetReadiness.REVIEWED
    assert assurance.confidence is VerificationStatus.UNVERIFIED
    assert assurance.confidence_contradicts_readiness


def test_a_ccnl_without_identity_has_no_assurance() -> None:
    """Nothing identifies the file, so nothing can be reported."""
    assert ccnl_ruleset_assurance(make_minimal_ccnl()) is None
