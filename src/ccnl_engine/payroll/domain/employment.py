"""Employment contract types, employment fact value objects and relationship."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.contract.domain.category import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.tax.domain.preferential_regime import EmploymentSector
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.request_checks import type_error

_FEATURE = "employment_facts"


def _require_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        msg = f"{name} must be an int; got {value!r}"
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

    def overlaps_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers at least one day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the month has at least one employed day.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= last and (
            self.ended_on is None or self.ended_on >= first
        )

    def covers_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers every day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the employment starts on or before the first day
            and does not end before the last day of the month.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= first and (
            self.ended_on is None or self.ended_on >= last
        )

    def days_in_year(self, year: int) -> int:
        """Return the calendar days of ``year`` the employment covers.

        Args:
            year: Calendar year.

        Returns:
            Days from the later of 1 January and ``started_on`` to the
            earlier of 31 December and ``ended_on``, inclusive; zero when
            the employment has no day in ``year``.
        """
        first = max(date(year, 1, 1), self.started_on)
        last = date(year, 12, 31)
        if self.ended_on is not None:
            last = min(last, self.ended_on)
        return max(0, (last - first).days + 1)

    def clip_start(self, day: date) -> date:
        """Return ``day``, or the hire date when ``day`` precedes it.

        Args:
            day: A date, typically the first day of an accrual window.

        Returns:
            ``max(day, started_on)``.
        """
        return max(day, self.started_on)


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """Return the first and last day of a calendar month.

    Returns:
        ``(first, last)`` dates of ``month`` in ``year``.
    """
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    return first, last


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


@dataclass(frozen=True)
class Employment:
    """The employment relationship: contract, level and worker facts.

    Facts are validated on construction: a value of the wrong type or an
    impossible combination raises
    :class:`~ccnl_engine.engine.errors.InvalidInputError` (a ``ValueError``)
    instead of producing a payslip.

    Attributes:
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``"metalmeccanico-federmeccanica.json"``.
        level_code: Contractual level code, e.g. ``"C3"``.
        contract_type: :class:`Permanent`, :class:`FixedTerm` or
            :class:`Apprentice`.
        category: Worker category; its string value (e.g. ``"operaio"``) is
            accepted and normalized.  ``None`` takes the category fixed by
            the level, if any.  The calculation raises when the category
            differs from the one the level fixes, or when it is ``None`` and
            seniority increments for the level differ by category.
        employment_period: Start and optional end of the employment.
            ``None`` when not tracked: a year then computes every run of the
            calendar with full ratei.
        weekly_hours: Contracted weekly hours.  Required for domestic CCNLs
            to select the INPS bracket; below ``full_time_weekly_hours`` it
            scales the pay for part time.
        full_time_weekly_hours: Full-time weekly hours of the contract.
            ``weekly_hours`` must not exceed it.
        seniority_months: Months of continuous service.  ``None`` applies no
            seniority increment.
        roles: Role codes that unlock role-specific contractual allowances.
        ceiling_status: Whether the IVS massimale applies.  ``UNKNOWN`` (the
            default) does not apply it.
        sector: Private or public sector of the employment, for the regimes
            restricted to one sector.  ``None`` means not known: those
            regimes are then ``unknown`` and the result provisional.  It is
            not derived from the CCNL: a public employer may apply a private
            CCNL.

    Raises:
        InvalidInputError: When a field is not of its type, when
            ``weekly_hours`` exceeds ``full_time_weekly_hours``, or when
            ``category`` or ``sector`` names no known value.
    """

    ccnl_slug: str
    level_code: str
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    category: WorkerCategory | None = None
    employment_period: EmploymentPeriod | None = None
    weekly_hours: WeeklyHours | None = None
    full_time_weekly_hours: WeeklyHours | None = None
    seniority_months: SeniorityMonths | None = None
    roles: frozenset[str] = frozenset()
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN
    sector: EmploymentSector | None = None

    def __post_init__(self) -> None:  # noqa: D105
        problem = type_error((
            ("ccnl_slug", self.ccnl_slug, str, False),
            ("level_code", self.level_code, str, False),
            (
                "contract_type",
                self.contract_type,
                (Permanent, Apprentice, FixedTerm),
                False,
            ),
            ("employment_period", self.employment_period, EmploymentPeriod, True),
            ("weekly_hours", self.weekly_hours, WeeklyHours, True),
            ("full_time_weekly_hours", self.full_time_weekly_hours, WeeklyHours, True),
            ("seniority_months", self.seniority_months, SeniorityMonths, True),
            ("roles", self.roles, frozenset, False),
            ("ceiling_status", self.ceiling_status, ContributionCeilingStatus, False),
        ))
        if problem is not None:
            raise InvalidInputError(problem, feature=_FEATURE)
        object.__setattr__(self, "category", parse_worker_category(self.category))
        object.__setattr__(self, "sector", _sector(self.sector))
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)


def _sector(value: object) -> EmploymentSector | None:
    """Return ``value`` as an :class:`EmploymentSector`, or ``None``.

    Returns:
        The sector named by ``value``; ``None`` when ``value`` is ``None``.

    Raises:
        InvalidInputError: When ``value`` names no sector.
    """
    if value is None:
        return None
    try:
        return EmploymentSector(str(value))
    except ValueError:
        valid = [s.value for s in EmploymentSector]
        msg = f"sector must be one of {valid}; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE) from None
