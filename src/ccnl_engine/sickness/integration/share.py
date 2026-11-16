"""The annual daily share of a fixed-term worker."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["FixedTermDailyShare"]


class FixedTermDailyShare(BaseModel):
    """The annual daily share as the CCNL grants it to a fixed-term worker.

    Florovivaisti art. 62: after thirty continuous days of work with the
    same employer, the same 25% 'a partire dal trentunesimo giorno dalla
    data di assunzione e per la durata di quarantacinque giornate in un
    anno'.

    Attributes:
        from_day: Day of the employment, counted from the hiring day as the
            first, from which the share is paid.
        annual_max_days: Days a year the share is paid at most.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    from_day: int = Field(ge=1)
    annual_max_days: int = Field(ge=1)
