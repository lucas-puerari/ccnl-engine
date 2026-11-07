"""First- and third-level apprenticeship tracks of a CCNL.

The pay of a first-level (art. 43) or third-level (art. 45) apprentice
splits the hours: the training in the educational institution is unpaid,
the training at the employer takes :attr:`DualTrack.company_training_rate`
(10% unless the CCNL says otherwise, D.Lgs. 81/2015 art. 43 c. 7 and art.
45 c. 3), the work takes the rate of the period of the track.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.employment.apprentice.inputs import ApprenticeshipProgramme
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["BASE", "SENIORITY", "DualPeriod", "DualTrack"]

#: Element code of the base salary (minimo, T.E.M.) in an element list.
BASE = "base"
#: Element code of the seniority increments in an element list.
SENIORITY = "seniority"


class DualPeriod(BaseModel):
    """Pay of the work hours in one stretch of a dual track.

    A period holds when every selector it sets matches the apprentice:
    the school year, the half of the programme, its length.

    Attributes:
        school_year: Year of the school course the period pays.
        half: Half of the programme (1 or 2) the period pays.
        programme_months_up_to: Longest programme the period pays.
        programme_months_over: Programme length the period pays above.
        work_rate: Share of the pay elements paid on the work hours.
        levels_below: Levels below the reference level the hours are
            paid at.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    school_year: int | None = Field(default=None, ge=1)
    half: Literal[1, 2] | None = None
    programme_months_up_to: int | None = Field(default=None, ge=1)
    programme_months_over: int | None = Field(default=None, ge=1)
    work_rate: Decimal = Field(gt=0, le=1)
    levels_below: int = Field(default=0, ge=0)


class DualTrack(BaseModel):
    """A CCNL rule for the pay of first- or third-level apprentices.

    Attributes:
        name: Identifier of the track, unique in the CCNL (the course of
            a first-level apprentice: qualifica, diploma...).
        programme: The apprenticeship it pays.
        destination_levels: Levels the apprentice is hired towards.
        reference_level: Level whose pay the rates apply to, when the CCNL
            sets a conventional one (Alimentari art. 21: 3°A); ``None``
            for the destination level.
        periods: The pay of the work hours by stretch.
        work_elements: Pay elements paid on the work hours (``base``,
            ``seniority`` and allowance codes); ``None`` for all.
        company_training_rate: Share paid on the training hours at the
            employer.
        company_training_on: Whether that share is of the pay of the
            ``reference`` level or of the ``work`` pay of the period.
        company_training_elements: Pay elements the training share is
            paid on; ``None`` for all.
        provenance: Source of the track.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    programme: Literal[
        ApprenticeshipProgramme.FIRST_LEVEL, ApprenticeshipProgramme.THIRD_LEVEL
    ]
    destination_levels: tuple[str, ...] = Field(min_length=1)
    reference_level: str | None = None
    periods: tuple[DualPeriod, ...] = Field(min_length=1)
    work_elements: tuple[str, ...] | None = None
    company_training_rate: Decimal = Field(ge=0, le=1)
    company_training_on: Literal["reference", "work"]
    company_training_elements: tuple[str, ...] | None = None
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _distinct_periods(self) -> Self:
        keys = [
            (
                p.school_year,
                p.half,
                p.programme_months_up_to,
                p.programme_months_over,
            )
            for p in self.periods
        ]
        if len(keys) != len(set(keys)):
            msg = f"dual track {self.name!r} repeats a period: {keys}"
            raise ValueError(msg)
        return self
