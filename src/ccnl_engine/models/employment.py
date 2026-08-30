"""Employment contract type models.

Each concrete type is a discriminated union member identified by its ``type``
field. Use :data:`Employment` as the annotation wherever a contract type is
expected; pydantic will deserialize the correct variant based on the
``"type"`` key in the input data.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Permanent(BaseModel):
    """Standard open-ended (permanent) employment contract."""

    type: Literal["permanent"]


class FixedTerm(BaseModel):
    """Fixed-term contract (*contratto a tempo determinato*).

    Fixed-term contracts attract an additional INPS contribution
    (contributo addizionale NASpI) on top of the standard employer rate.
    """

    type: Literal["fixed_term"]


class Apprentice(BaseModel):
    """Apprenticeship contract (*contratto di apprendistato*).

    Attributes:
        months_elapsed: Number of months completed since the hire date.
            Used to look up the applicable salary percentage or under-
            classification level from the CCNL apprenticeship table.
    """

    type: Literal["apprentice"]
    months_elapsed: int


#: Discriminated union of all supported employment contract types.
Employment = Annotated[
    Permanent | FixedTerm | Apprentice,
    Field(discriminator="type"),
]
