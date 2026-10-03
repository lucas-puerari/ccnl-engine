"""Assurance of one ruleset: readiness, confidence and their agreement."""

from __future__ import annotations

import pytest

from ccnl_engine.provenance.domain.ruleset_assurance import RulesetKind
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetReadiness,
    VerificationStatus,
)
from tests.fixtures.rulesets import ccnl_ruleset, ruleset_identity, tax_ruleset

_EXPLORATORY = RulesetReadiness.EXPLORATORY
_REVIEWED = RulesetReadiness.REVIEWED
_PRODUCTION = RulesetReadiness.PRODUCTION
_VERIFIED = VerificationStatus.VERIFIED
_UNVERIFIED = VerificationStatus.UNVERIFIED


def test_a_kind_without_tier_reports_no_readiness() -> None:
    """Tax, INPS and surtax rulesets track no tier: none is invented."""
    ruleset = tax_ruleset("tax/2026/industria")

    assert ruleset.kind is RulesetKind.TAX
    assert ruleset.readiness is None
    assert not ruleset.readiness_tracked
    assert ruleset.confidence is _UNVERIFIED
    assert not ruleset.confidence_contradicts_readiness
    assert not ruleset.is_production


def test_identity_fields_are_exposed() -> None:
    """Id, hash and the id@version form come from the identity."""
    identity = ruleset_identity("ccnl/x")
    ruleset = ccnl_ruleset(_EXPLORATORY)

    assert ruleset.identity == identity
    assert ruleset.id == "ccnl/x"
    assert ruleset.source_hash == identity.source_hash
    assert str(ruleset) == "ccnl/x@2026.1"
    assert ruleset.readiness_tracked


@pytest.mark.parametrize(
    ("readiness", "confidence", "contradicts", "production"),
    [
        (_EXPLORATORY, _UNVERIFIED, False, False),
        (_REVIEWED, _VERIFIED, False, False),
        (_REVIEWED, _UNVERIFIED, True, False),
        (_REVIEWED, VerificationStatus.NEEDS_REVIEW, True, False),
        (_PRODUCTION, _UNVERIFIED, True, False),
        (_PRODUCTION, _VERIFIED, False, True),
    ],
)
def test_confidence_must_back_a_cleared_tier(
    readiness: RulesetReadiness,
    confidence: VerificationStatus,
    *,
    contradicts: bool,
    production: bool,
) -> None:
    """A reviewed or production tier needs a verified confidence."""
    ruleset = ccnl_ruleset(readiness, confidence)

    assert ruleset.confidence_contradicts_readiness is contradicts
    assert ruleset.is_production is production
