"""Employment contract type models."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class Permanent(BaseModel):
    """Standard open-ended (permanent) employment contract."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["permanent"] = "permanent"


class FixedTerm(BaseModel):
    """Fixed-term contract; attracts NASpI addizionale on employer INPS."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["fixed_term"] = "fixed_term"


class Apprentice(BaseModel):
    """Apprenticeship contract; salary is derived from CCNL apprenticeship rules.

    Attributes:
        months_elapsed: Months of apprenticeship service elapsed so far.
            Used to look up the applicable ``apprenticeship_pct`` in the
            CCNL percentage track, or the under-classification level in
            under-classification tracks.
        track: Name of the CCNL apprenticeship track to apply. Required
            only when more than one track covers the destination level;
            ``None`` lets the engine select the unique applicable track.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["apprentice"] = "apprentice"
    months_elapsed: int = Field(ge=0)
    track: str | None = None


#: Discriminated union of all supported employment contract types.
Employment = Annotated[
    Permanent | FixedTerm | Apprentice,
    Field(discriminator="type"),
]
