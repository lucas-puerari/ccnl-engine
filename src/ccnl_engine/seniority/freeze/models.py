"""A period the seniority increments do not accrue in."""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

__all__ = ["SeniorityFreeze"]


class SeniorityFreeze(BaseModel):
    """A period the CCNL leaves out of the seniority of the increments.

    Bancari ABI art. 103 c. 3: no seniority for the scatti accrues from
    1 January 2013 to 31 July 2014.

    Attributes:
        valid_from: First day of the frozen period.
        valid_until: First day after it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    valid_from: date
    valid_until: date

    @model_validator(mode="after")
    def _check_order(self) -> Self:
        if self.valid_until <= self.valid_from:
            msg = "a seniority freeze ends after it starts"
            raise ValueError(msg)
        return self
