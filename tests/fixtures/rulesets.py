"""Builders of ruleset identities and assurances for unit tests."""

from __future__ import annotations

from datetime import date

from ccnl_engine.provenance.domain.ruleset_assurance import (
    RulesetAssurance,
    RulesetKind,
)
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetIdentity,
    RulesetReadiness,
    SourceType,
    VerificationStatus,
)

__all__ = ["ccnl_ruleset", "ruleset_identity", "tax_ruleset"]


def ruleset_identity(ruleset_id: str) -> RulesetIdentity:
    """Return an unverified identity of version 2026.1 for ``ruleset_id``.

    Returns:
        The identity.
    """
    return RulesetIdentity(
        id=ruleset_id,
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="unavailable",
        source_type=SourceType.DERIVED,
        source_hash="0" * 64,
        verification_status=VerificationStatus.UNVERIFIED,
    )


def tax_ruleset(ruleset_id: str) -> RulesetAssurance:
    """Return the assurance of a tax ruleset, which tracks no readiness.

    Returns:
        The assurance.
    """
    return RulesetAssurance.without_tier(ruleset_identity(ruleset_id), RulesetKind.TAX)


def ccnl_ruleset(
    readiness: RulesetReadiness,
    confidence: VerificationStatus = VerificationStatus.VERIFIED,
    ruleset_id: str = "ccnl/x",
) -> RulesetAssurance:
    """Return the assurance of a CCNL ruleset at ``readiness``.

    Returns:
        The assurance.
    """
    return RulesetAssurance(
        ruleset_identity(ruleset_id), RulesetKind.CCNL, readiness, confidence
    )
