"""Assurance of one ruleset: its identity, its readiness and its confidence.

A payroll result reads rules from several rulesets: the CCNL, the tax and
INPS year files, the variable-pay and family-deduction rules and the surtax
tables.  :class:`RulesetAssurance` reports, for each of them, which file was
read (identity and integrity hash) and how far a person has cleared it.

Only CCNL rulesets carry a readiness tier.  The tax, INPS and surtax files
record provenance per rule and no tier, so their :attr:`RulesetAssurance\
.readiness` is ``None``: not tracked, never assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ccnl_engine.provenance.ruleset.models import (
    RulesetIdentity,
    RulesetReadiness,
    VerificationStatus,
)

__all__ = ["RulesetAssurance", "RulesetKind"]


class RulesetKind(StrEnum):
    """Which part of the bundle a ruleset belongs to.

    The kind is set by the loader that read the ruleset, never inferred from
    its id.

    Attributes:
        CCNL: A collective agreement: salary tables, allowances, work rules.
        TAX: A tax year file: IRPEF, deductions, variable pay, family
            deductions.
        INPS: An INPS contribution year file.
        SURTAX: A regional or municipal surtax table.
    """

    CCNL = "ccnl"
    TAX = "tax"
    INPS = "inps"
    SURTAX = "surtax"


_CLEARED = frozenset({RulesetReadiness.REVIEWED, RulesetReadiness.PRODUCTION})


@dataclass(frozen=True, slots=True)
class RulesetAssurance:
    """Identity, readiness and confidence of one ruleset.

    Attributes:
        identity: Id, version, validity, source and integrity hash.
        kind: Part of the bundle the ruleset belongs to.
        readiness: Readiness tier set by a reviewer; ``None`` when the kind
            tracks no tier (every kind but :attr:`RulesetKind.CCNL`).
        confidence: Editorial confidence in the values: the CCNL
            ``verification.confidence``, or the identity
            ``verification_status`` for the other kinds.
    """

    identity: RulesetIdentity
    kind: RulesetKind
    readiness: RulesetReadiness | None
    confidence: VerificationStatus

    @classmethod
    def without_tier(
        cls, identity: RulesetIdentity, kind: RulesetKind
    ) -> RulesetAssurance:
        """Report a ruleset whose kind tracks no readiness tier.

        Returns:
            The assurance, with no readiness and the confidence of the
            identity.
        """
        return cls(identity, kind, None, identity.verification_status)

    def __str__(self) -> str:
        """Collapse to the ``id@version`` of the identity.

        Returns:
            The identity as ``id@version``.
        """
        return str(self.identity)

    @property
    def id(self) -> str:
        """Stable id of the ruleset, e.g. ``ccnl/metalmeccanico-federmeccanica``."""
        return self.identity.id

    @property
    def source_hash(self) -> str:
        """sha256 of the data file the ruleset was read from."""
        return self.identity.source_hash

    @property
    def readiness_tracked(self) -> bool:
        """Whether the ruleset carries a readiness tier at all."""
        return self.readiness is not None

    @property
    def confidence_contradicts_readiness(self) -> bool:
        """Whether the tier claims a review the confidence does not record.

        A ``reviewed`` or ``production`` ruleset must record
        ``confidence = verified`` (see the promotion criteria in the
        readiness documentation); one that does not is inconsistent.
        """
        return (
            self.readiness in _CLEARED
            and self.confidence is not VerificationStatus.VERIFIED
        )

    @property
    def is_production(self) -> bool:
        """Whether the ruleset is ``production`` and its confidence agrees."""
        return (
            self.readiness is RulesetReadiness.PRODUCTION
            and not self.confidence_contradicts_readiness
        )
