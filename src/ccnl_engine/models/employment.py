"""Employment contract type models."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Permanent(BaseModel):
    """Standard open-ended (permanent) employment contract."""

    type: Literal["permanent"] = "permanent"


class FixedTerm(BaseModel):
    """Fixed-term contract; attracts NASpI addizionale on employer INPS."""

    type: Literal["fixed_term"] = "fixed_term"


class Apprentice(BaseModel):
    """Apprenticeship contract; salary is derived from CCNL apprenticeship rules."""

    type: Literal["apprentice"] = "apprentice"
    months_elapsed: int = Field(ge=0)


#: Discriminated union of all supported employment contract types.
Employment = Annotated[
    Permanent | FixedTerm | Apprentice,
    Field(discriminator="type"),
]
