"""Shared provenance model for bundled rulesets.

Every ruleset in the knowledge base (a CCNL contract, a tax/INPS year file, a
surtax year file) carries a :class:`RulesetIdentity` that gives it a stable
identity, versioning, validity window and an integrity hash.  The loaders
expose this block so that a payroll result can record
exactly which ruleset versions produced a pay calculation, making the result
reproducible years later.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class VerificationStatus(StrEnum):
    """How confident we are in the data behind a ruleset."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NEEDS_REVIEW = "needs_review"


class SourceType(StrEnum):
    """Origin classification of the data behind a ruleset.

    Values:
        official_primary: Official text published by the signing parties
            or a government body (e.g. CNEL, MEF, INPS circulars).
        contracting_party: Published directly by one of the parties
            (employer federation or union), but not an official consolidated
            text.
        institutional_secondary: Published by a public institution but
            derived from primary sources (e.g. CNEL summaries, INPS guides).
        commercial_secondary: Third-party commercial site or aggregator
            (e.g. lavoro-economia.it, contractivo.it).
        derived: Values computed by back-calculation or inference from other
            known values; no direct source quote.
        estimated: Values approximated without a primary source; confidence
            cannot reach ``high`` without an explicit human review.
    """

    OFFICIAL_PRIMARY = "official_primary"
    CONTRACTING_PARTY = "contracting_party"
    INSTITUTIONAL_SECONDARY = "institutional_secondary"
    COMMERCIAL_SECONDARY = "commercial_secondary"
    DERIVED = "derived"
    ESTIMATED = "estimated"


class RulesetReadiness(StrEnum):
    """Production readiness of a CCNL ruleset.

    Separate from :class:`VerificationStatus` (which measures data confidence
    at the value level). Readiness classifies whether the ruleset as a whole
    is cleared for a given use context.

    Values:
        exploratory: Extracted and traced; no human review of key values.
            Safe for demos, research, and prototyping.
        reviewed: Key salary table values and primary sources verified by a
            person. Suitable for product simulations with an explicit
            disclaimer and ruleset-level scope.
        production: Full review, at least one reference case from an
            independent source, a named owner, and a tracked update policy.
            Suitable for operational flows where figures are shown to end
            users or used in decisions.

    Promotion criteria:
        exploratory → reviewed: a human has cross-checked at least L1 values
            (base salary, seniority table, additional months) against the
            primary CCNL source, and the source URL is recorded.
        reviewed → production: all L1+L2 values verified, at least one
            reference case from an official source or real payslip
            (anonymised), a named owner assigned, and an update-policy entry.
    """

    EXPLORATORY = "exploratory"
    REVIEWED = "reviewed"
    PRODUCTION = "production"


def source_hash(payload: object) -> str:
    """Return a stable sha256 hex digest of *payload*.

    The payload is serialised with sorted keys, compact separators and
    ``ensure_ascii=False`` so the digest is deterministic across runs,
    platforms and Python versions.

    Any key named ``source_hash`` (typically the nested ``ruleset.source_hash``
    of the very payload being hashed) is stripped recursively before hashing,
    so the recorded digest never depends on itself.

    Args:
        payload: Any JSON-serialisable object (typically the raw ruleset dict).

    Returns:
        A 64-character lowercase hex digest.
    """
    serialised = json.dumps(
        _strip_hash_fields(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()


def _strip_hash_fields(value: object) -> object:
    """Recursively remove every ``source_hash`` key from *value*.

    Returns:
        *value* with all ``source_hash`` entries removed, ``None`` included.
    """
    if isinstance(value, dict):
        return {
            k: _strip_hash_fields(v) for k, v in value.items() if k != "source_hash"
        }
    if isinstance(value, list):
        return [_strip_hash_fields(v) for v in value]
    return value


class RulesetIdentity(BaseModel):
    """Identity and provenance metadata for a single ruleset.

    Attributes:
        id: Stable identifier for the ruleset
            (e.g. ``"ccnl/metalmeccanico-federmeccanica"`` or
            ``"tax/2026/industria"``).
        version: Dataset version this ruleset ships in
            (e.g. ``"2026.1"`` — the knowledge base ``__version__``).
        effective_from: First date the ruleset is applicable.
        effective_until: Last date the ruleset is applicable. ``None`` when
            the ruleset is still open-ended.
        published_at: Date the data file was published/recorded. Falls back
            to the current date when unknown (backfilled "as of today").
        source: Primary source reference (URL or identifier). ``"unavailable"``
            when no source is recorded.
        source_type: Origin classification of the underlying data.
        source_hash: sha256 hex digest of the underlying data file, used by
            the loaders for fail-hard integrity verification.
        verification_status: Confidence level in the recorded data.
        verified_by: Identifier of the person who verified this ruleset;
            required when ``verification_status`` is ``"verified"``.
        verified_at: Date the ruleset was verified; required when
            ``verification_status`` is ``"verified"``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    version: str
    effective_from: date
    effective_until: date | None = None
    published_at: date
    source: str
    source_type: SourceType
    source_hash: str
    verification_status: VerificationStatus
    verified_by: str | None = None
    verified_at: date | None = None

    def __str__(self) -> str:
        """Collapse the identity to a compact ``id@version`` string.

        Returns:
            The ``id@version`` identifier, e.g. ``"tax/2026/industria@2026.1"``.
        """
        return f"{self.id}@{self.version}"
