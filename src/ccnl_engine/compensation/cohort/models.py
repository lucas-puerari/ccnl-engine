"""The base salary of the workers hired by a date.

CCNL consorzi di bonifica, Allegato A: one table for the "dipendenti in
servizio al 15 luglio 2000" and one for those "in servizio dal 15 luglio
2000".
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from ccnl_engine.agreement.validity.rules import TimeSeries

__all__ = ["CohortSalary"]


class CohortSalary(BaseModel):
    """The base salary of a level for the workers hired by ``hired_until``.

    Attributes:
        hired_until: Last hire date of the cohort.
        base_salary: Its monthly base salary, in place of the level's.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hired_until: date
    base_salary: TimeSeries
