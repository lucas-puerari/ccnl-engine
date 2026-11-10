"""Documented conditions that may qualify for an extended sickness comporto."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["SeriousIllnessKind"]


class SeriousIllnessKind(StrEnum):
    """Documented conditions used by agreement-specific sickness rules.

    ``ONCOLOGICAL`` has its own ABI art. 66 c. 5 limit; the other ABI
    diagnoses share the serious-illness limit of the seniority band.
    ``CERTIFIED_LISTED_GRAVE_PATHOLOGY`` requires a current specialist
    certificate identifying a condition in the agreement's exhaustive list.
    ``CERTIFIED_L68_99_DISABILITY`` requires certified civil disability under
    L. 68/99; ``CERTIFIED_RELATED_LIFE_SAVING_THERAPY`` requires a certificate
    of therapy related to one of those two qualifying conditions.
    """

    ONCOLOGICAL = "oncological"
    MULTIPLE_SCLEROSIS = "multiple_sclerosis"
    MUSCULAR_DYSTROPHY = "muscular_dystrophy"
    TUBERCULOSIS_CARE = "tuberculosis_care"
    AIDS = "aids"
    SEVERE_DISABILITY = "severe_disability"
    CERTIFIED_LISTED_GRAVE_PATHOLOGY = "certified_listed_grave_pathology"
    CERTIFIED_L68_99_DISABILITY = "certified_l68_99_disability"
    CERTIFIED_RELATED_LIFE_SAVING_THERAPY = "certified_related_life_saving_therapy"
