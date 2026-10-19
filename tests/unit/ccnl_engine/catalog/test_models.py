"""Assurance of a CCNL ruleset from its identity and verification."""

from __future__ import annotations

from datetime import date

from ccnl_engine.agreement.facade import CCNLVerification
from ccnl_engine.catalog.models import ccnl_ruleset_assurance
from ccnl_engine.provenance.ruleset.assurance.models import RulesetKind
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from tests.unit.ccnl_engine.builders import make_minimal_ccnl
from tests.unit.ccnl_engine.provenance.ruleset.builders import ruleset_identity


def test_readiness_and_confidence_come_from_the_verification() -> None:
    """The tier, confidence and review date are those a reviewer recorded."""
    identity = ruleset_identity("ccnl/minimal")
    verification = CCNLVerification(
        confidence=VerificationStatus.UNVERIFIED,
        readiness=RulesetReadiness.REVIEWED,
        review_due=date(2027, 1, 31),
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
    assert assurance.review_due == date(2027, 1, 31)
    assert assurance.confidence_contradicts_readiness


def test_a_ccnl_without_identity_has_no_assurance() -> None:
    """Nothing identifies the file, so nothing can be reported."""
    assert ccnl_ruleset_assurance(make_minimal_ccnl()) is None
