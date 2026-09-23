"""Employment contract types and Employment relationship."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.payroll.domain.employer import Employer


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
Contract = Annotated[
    Permanent | FixedTerm | Apprentice,
    Field(discriminator="type"),
]


class Employment(BaseModel):
    """The employment relationship.

    Ties together which CCNL applies, the contract type, the employer
    (with headcount), and the reference date for all time-series lookups.

    Attributes:
        ccnl: Bundled CCNL filename (e.g.
            ``"metalmeccanico-federmeccanica.json"``).
        contract: Contract type — :class:`Permanent`, :class:`FixedTerm`,
            or :class:`Apprentice`.
        employer: Employer-side inputs including headcount.
        as_of: Reference date for all time-series lookups (base pay,
            seniority amounts, allowances, additional months). Also the
            upper bound for deriving months of service when seniority is
            expressed as a :class:`~ccnl_engine.engine.payroll.domain\
.employee.SeniorityByDate`.
        tax_year: Override the fiscal year used for tax/INPS rule loading.
            When ``None`` (default), ``as_of.year`` is used.
            Set explicitly when applying a specific year's tax rules to a
            date in a different calendar year (e.g. computing a late-2025
            payslip with 2026 tax rules already in force).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ccnl: str
    contract: Annotated[
        Permanent | FixedTerm | Apprentice,
        Field(discriminator="type"),
    ]
    employer: Employer
    as_of: date
    tax_year: int | None = None
