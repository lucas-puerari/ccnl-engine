"""Employment contract types and the employment relationship."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.contract.domain.category import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employment_facts import (
    FEATURE,
    EmploymentPeriod,
    SeniorityMonths,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.domain.request_checks import type_error
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.tax.domain.preferential_regime import EmploymentSector


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
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError` (a ``ValueError``)
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
            raise InvalidInputError(problem, feature=FEATURE)
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
        raise InvalidInputError(msg, feature=FEATURE) from None
