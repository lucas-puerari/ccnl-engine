"""The documented diagnoses a CCNL gives a longer comporto (ABI art. 66)."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["SeriousIllnessKind"]


class SeriousIllnessKind(StrEnum):
    """A diagnosis of ABI art. 66 c. 4-5 that extends the comporto.

    ``ONCOLOGICAL`` has its own limit; the others share the serious-illness
    limit of the seniority band.
    """

    ONCOLOGICAL = "oncological"
    TUBERCULOSIS_CARE = "tuberculosis_care"
    AIDS = "aids"
    SEVERE_DISABILITY = "severe_disability"
