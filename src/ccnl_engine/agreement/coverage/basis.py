"""Why a capability a CCNL leaves to the caller is not a gap of its model.

A capability the engine computes from a rule of the CCNL (overtime, night,
holiday and shift work, travel) is a gap of a CCNL that holds no such rule.
Some CCNLs hold none because they hand the amount to the integrative
bargaining of each employer: the amount is then a fact of the employer, as
the criterion for silent clauses has it, and the caller states it.  The
record keeps the clause that hands it down, with its source.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["CapabilityBasis", "CapabilityBasisKind"]


class CapabilityBasisKind(StrEnum):
    """Why the CCNL sets no rule of a capability.

    Attributes:
        DELEGATED_TO_SECOND_LEVEL: The CCNL hands the amount to the
            integrative (second-level) bargaining of the employer.
    """

    DELEGATED_TO_SECOND_LEVEL = "delegated_to_second_level"


class CapabilityBasis(BaseModel):
    """The clause that leaves a capability's amount to the employer.

    Attributes:
        kind: Why the CCNL sets no rule.
        provenance: The clause, quoted.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: CapabilityBasisKind
    provenance: RuleProvenance
