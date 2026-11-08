"""The increments of the staff in service on a day of an old renewal."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["InServiceCohort"]


class InServiceCohort(BaseModel):
    """A higher maximum of increments for the staff in service on a day.

    BCC artt. 101 and 113: "al personale in servizio alla data del
    31.12.1997, gli scatti di anzianità competono nel numero massimo di 12"
    (9 for the 3rd and 4th level of the quadri direttivi), where the others
    have 8 (7).

    Attributes:
        in_service_on: The day the worker must have been in service on.
        maximum_count: The maximum of the cohort.
        maximum_count_by_level: The maximum of the cohort by level code.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    in_service_on: date
    maximum_count: int = Field(ge=0)
    maximum_count_by_level: Mapping[str, int] = Field(default_factory=dict)
