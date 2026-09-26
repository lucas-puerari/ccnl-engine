"""Employment contract types, employment fact value objects and relationship."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employer import Employer

_FEATURE = "employment_facts"


def _require_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        msg = f"{name} must be an int; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class Headcount:
    """Employer headcount used to select INPS contribution tiers.

    At least one: the worker being paid is an employee of the employer.

    Attributes:
        value: Number of employees, ``>= 1``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is below 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        _require_int(self.value, "num_employees")
        if self.value < 1:
            msg = f"num_employees must be >= 1; got {self.value}"
            raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class WeeklyHours:
    """Weekly working hours, contracted or full-time.

    Attributes:
        value: Hours per week, ``> 0``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is not positive.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        _require_int(self.value, "weekly_hours")
        if self.value <= 0:
            msg = f"weekly_hours must be > 0; got {self.value}"
            raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class SeniorityMonths:
    """Months of continuous service used for seniority increments.

    Attributes:
        value: Completed months of service, ``>= 0``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is negative.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        _require_int(self.value, "seniority_months")
        if self.value < 0:
            msg = f"seniority_months must be >= 0; got {self.value}"
            raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class ContributableHours:
    """Hours worked and paid in a period that are subject to INPS contributions.

    Zero is valid (a period with no paid hours).

    Attributes:
        value: Finite :class:`~decimal.Decimal` number of hours, ``>= 0``.

    Raises:
        InvalidInputError: When ``value`` is not a finite Decimal or is negative.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            msg = f"contributable_hours must be a finite Decimal; got {self.value!r}"
            raise InvalidInputError(msg, feature=_FEATURE)
        if self.value < 0:
            msg = f"contributable_hours must be >= 0; got {self.value}"
            raise InvalidInputError(msg, feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class EmploymentPeriod:
    """Start and optional end of the employment relationship.

    Attributes:
        started_on: First day of employment.
        ended_on: Last day of employment, or ``None`` for an open-ended
            relationship.  Must not precede ``started_on``.

    Raises:
        InvalidInputError: When ``ended_on`` is before ``started_on``.
    """

    started_on: date
    ended_on: date | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.ended_on is not None and self.ended_on < self.started_on:
            msg = (
                f"ended_on ({self.ended_on}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(msg, feature=_FEATURE)

    @classmethod
    def from_dates(
        cls, started_on: date | None, ended_on: date | None
    ) -> EmploymentPeriod | None:
        """Build a period from optional dates, as supplied by callers.

        Returns:
            ``None`` when neither date is given, otherwise the validated period.

        Raises:
            InvalidInputError: When only ``ended_on`` is given, or when
                ``ended_on`` precedes ``started_on``.
        """
        if started_on is None:
            if ended_on is not None:
                msg = f"ended_on ({ended_on}) requires started_on"
                raise InvalidInputError(msg, feature=_FEATURE)
            return None
        return cls(started_on=started_on, ended_on=ended_on)


def check_within_full_time(
    weekly_hours: WeeklyHours | None, full_time_weekly_hours: WeeklyHours | None
) -> None:
    """Reject contracted weekly hours above the full-time weekly hours.

    Raises:
        InvalidInputError: When both are given and ``weekly_hours`` exceeds
            ``full_time_weekly_hours``.
    """
    if (
        weekly_hours is not None
        and full_time_weekly_hours is not None
        and weekly_hours.value > full_time_weekly_hours.value
    ):
        msg = (
            f"weekly_hours ({weekly_hours.value}) must not exceed "
            f"full_time_weekly_hours ({full_time_weekly_hours.value})"
        )
        raise InvalidInputError(msg, feature=_FEATURE)


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
