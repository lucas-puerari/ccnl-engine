"""Shared provenance model for bundled rulesets.

Every ruleset in the knowledge base (a CCNL contract, a tax/INPS year file, a
surtax year file) carries a :class:`RulesetIdentity` that gives it a stable
identity, versioning, validity window and an integrity hash.  The loaders
expose this block so that a
:class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation` can record
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
        source_hash: sha256 hex digest of the underlying data file, used by
            the loaders for fail-hard integrity verification.
        verification_status: Confidence level in the recorded data.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    version: str
    effective_from: date
    effective_until: date | None = None
    published_at: date
    source: str
    source_hash: str
    verification_status: VerificationStatus

    def __str__(self) -> str:
        """Collapse the identity to a compact ``id@version`` string.

        Returns:
            The ``id@version`` identifier, e.g. ``"tax/2026/industria@2026.1"``.
        """
        return f"{self.id}@{self.version}"

    def as_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        Returns:
            A plain dict with ISO-8601 date strings (JSON-serialisable).
        """
        return {
            "id": self.id,
            "version": self.version,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat()
                if self.effective_until is not None
                else None
            ),
            "published_at": self.published_at.isoformat(),
            "source": self.source,
            "source_hash": self.source_hash,
            "verification_status": str(self.verification_status),
        }
