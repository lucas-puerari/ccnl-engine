"""The base salary of the workers hired by a date.

CCNL consorzi di bonifica, Allegato A: one table for the "dipendenti in
servizio al 15 luglio 2000" and one for those "in servizio dal 15 luglio
2000".
"""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries

__all__ = ["ClassTable", "CohortSalary", "SalaryClass"]


class CohortSalary(BaseModel):
    """The base salary of a level for the workers hired by ``hired_until``.

    Attributes:
        hired_until: Last hire date of the cohort.
        base_salary: Its monthly base salary, in place of the level's.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hired_until: date
    base_salary: TimeSeries


class SalaryClass(BaseModel):
    """The salary of one seniority class of a class table.

    Attributes:
        months_from: Months of service from which the class is paid.
        base_salary: Its monthly salary.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    months_from: int = Field(ge=0)
    base_salary: TimeSeries


class ClassTable(BaseModel):
    """A salary table by seniority class, in place of base and increments.

    ANIA art. 113: "Gli scatti per anzianità sono regolati dalle tabelle
    contrattualmente in atto (Allegato 2/A per il personale già alle
    dipendenze dell'impresa alla data di stipula del CCNL 18 dicembre 1999,
    Allegato 2/B per il personale assunto successivamente)".

    Attributes:
        hired_until: Last hire date of the cohort; ``None`` for every
            later hire.
        classes: The classes, in increasing ``months_from`` from 0.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hired_until: date | None = None
    classes: tuple[SalaryClass, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        starts = [c.months_from for c in self.classes]
        if starts[0] != 0 or starts != sorted(set(starts)):
            msg = f"class table must start at 0 and rise: {starts}"
            raise ValueError(msg)
        return self

    def salary(self, months: int) -> TimeSeries:
        """Return the salary of the class ``months`` of service fall in.

        Returns:
            The base salary of the last class starting by ``months``.
        """
        return [c for c in self.classes if c.months_from <= months][-1].base_salary
