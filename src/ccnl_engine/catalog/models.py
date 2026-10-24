"""Assurance of a CCNL ruleset, built from its identity and verification.

The single builder used both by a payroll run, to report the CCNL it read,
and by the engine catalog, to inspect a CCNL before any run, so the two can
never disagree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.agreement.metadata.review.models import ReviewIndependence
from ccnl_engine.provenance.ruleset.assurance.models import (
    AssuranceAxes,
    RulesetAssurance,
    RulesetKind,
)
from ccnl_engine.provenance.ruleset.models import VerificationStatus

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

__all__ = ["ccnl_axes", "ccnl_ruleset_assurance"]


def ccnl_axes(ccnl: CCNL) -> AssuranceAxes:
    """Return the separate kinds of evidence ``ccnl.verification`` records.

    Returns:
        The axes of the CCNL.
    """
    verification = ccnl.verification
    reviews = verification.reviews
    return AssuranceAxes(
        source_checked=verification.confidence is VerificationStatus.VERIFIED
        and any(review.sources for review in reviews),
        externally_compared=verification.verified_cases > 0,
        human_signed_off=any(
            review.independence is ReviewIndependence.HUMAN for review in reviews
        ),
    )


def ccnl_ruleset_assurance(ccnl: CCNL) -> RulesetAssurance | None:
    """Return the assurance of the ruleset of ``ccnl``.

    Readiness, confidence and the next review date come from
    ``ccnl.verification``, the only place a reviewer records them.

    Returns:
        The assurance, or ``None`` when the CCNL records no ruleset
        identity.
    """
    if ccnl.ruleset is None:
        return None
    return RulesetAssurance(
        identity=ccnl.ruleset,
        kind=RulesetKind.CCNL,
        readiness=ccnl.verification.readiness,
        confidence=ccnl.verification.confidence,
        review_due=ccnl.verification.review_due,
        axes=ccnl_axes(ccnl),
    )
