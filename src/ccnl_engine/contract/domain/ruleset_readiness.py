"""Assurance of a CCNL ruleset, built from its identity and verification.

The single builder used both by a payroll run, to report the CCNL it read,
and by the engine catalog, to inspect a CCNL before any run, so the two can
never disagree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.provenance.domain.ruleset_assurance import (
    RulesetAssurance,
    RulesetKind,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL

__all__ = ["ccnl_ruleset_assurance"]


def ccnl_ruleset_assurance(ccnl: CCNL) -> RulesetAssurance | None:
    """Return the assurance of the ruleset of ``ccnl``.

    Readiness and confidence come from ``ccnl.verification``, the only
    place a reviewer records them.

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
    )
