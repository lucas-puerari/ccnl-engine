"""RuleProvenance, the leaf of the provenance chain.

A :class:`RuleProvenance` ties one extracted rule to the exact source
document, page and section it came from, together with the extraction
trace that produced it and a :class:`ProvenanceStatus` stating how far the
value can be trusted.  Domain models that embody a rule carry one; values
that add a per-period override carry their own.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.provenance.domain.extraction import ExtractionTrace  # noqa: TC001
from ccnl_engine.provenance.domain.source import SourceLocation  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Iterable


class ProvenanceStatus(StrEnum):
    """How far the value of a rule is backed by its source.

    Members are listed from the strongest to the weakest backing; compare
    them with :attr:`rank` or combine them with :meth:`weakest`.

    Attributes:
        VERIFIED: A named reviewer checked the value against the cited
            location on a recorded date: a person, or an AI review the
            owner of the ruleset authorised (``verified_by`` names the
            model and the owner).
        DERIVED: The value is taken or computed from a cited document
            location, without a recorded human check.
        ASSUMED: The value is adopted without a located citation: an
            unchecked AI extraction, a reconstruction or estimate, or a
            value whose clause was never located.
        MISSING: No source backs the value.
    """

    VERIFIED = "verified"
    DERIVED = "derived"
    ASSUMED = "assumed"
    MISSING = "missing"

    @property
    def rank(self) -> int:
        """Weakness of this status, ``0`` for verified up to ``3`` for missing."""
        return _RANK[self]

    @classmethod
    def weakest(cls, statuses: Iterable[ProvenanceStatus]) -> ProvenanceStatus:
        """Return the weakest status in ``statuses``.

        Args:
            statuses: Statuses to combine; must not be empty.

        Returns:
            The status with the highest :attr:`rank`.
        """
        return max(statuses, key=_RANK.__getitem__)


_RANK: dict[ProvenanceStatus, int] = {
    status: rank for rank, status in enumerate(ProvenanceStatus)
}

#: Statuses that require a located citation.
_LOCATED = frozenset({ProvenanceStatus.VERIFIED, ProvenanceStatus.DERIVED})


class RuleProvenance(BaseModel):
    """Provenance of a single extracted rule.

    Attributes:
        status: How far the value is backed by its source.
        location: Pointer into the source document (page/section/quote);
            required for ``verified`` and ``derived``, forbidden for
            ``missing``.
        extraction: How the rule was extracted, its validity period and who
            verified it; required for ``verified``.  ``None`` when the data
            records no extraction, in which case the validity period is the
            one of the ruleset that holds the rule.
        transformation: How the source text became the stored value (a
            formula, a unit change, a reconstruction), when not verbatim.
        note: Free-form context (e.g. a known simplification).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ProvenanceStatus
    location: SourceLocation | None = None
    extraction: ExtractionTrace | None = None
    transformation: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _check_status(self) -> Self:
        status = self.status
        if status in _LOCATED and self.location is None:
            msg = f"status {status.value!r} requires a source location"
            raise ValueError(msg)
        if status is ProvenanceStatus.MISSING and self.location is not None:
            msg = "status 'missing' cannot cite a source location"
            raise ValueError(msg)
        if status is ProvenanceStatus.VERIFIED and not _has_reviewer(self.extraction):
            msg = "status 'verified' requires extraction.verified_by and verified_at"
            raise ValueError(msg)
        return self


def _has_reviewer(extraction: ExtractionTrace | None) -> bool:
    return (
        extraction is not None
        and extraction.verified_by is not None
        and extraction.verified_at is not None
    )
