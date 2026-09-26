"""Canonical request types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.category import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employer import Employer
from ccnl_engine.payroll.domain.employment import (
    ContributableHours,
    EmploymentPeriod,
    Permanent,
    SeniorityMonths,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.domain.period import PeriodState

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["EmploymentFacts", "PayrollRequest", "PayrollYearRequest"]


@dataclass(frozen=True)
class EmploymentFacts:
    """Worker-side employment facts used to resolve pay, contributions and ceilings.

    Employer-side facts such as the headcount are not employment facts: pass
    them as :class:`~ccnl_engine.payroll.domain.employer.Employer` on the
    request.

    Facts are validated on construction: impossible values raise
    :class:`~ccnl_engine.engine.errors.InvalidInputError` (a ``ValueError``)
    instead of producing a payslip.  The validated value objects are exposed
    as properties and are what the engine consumes.

    Attributes:
        contract_type: Employment contract type (permanent, fixed-term, apprentice).
        ceiling_status: Whether the IVS massimale contribution ceiling applies.
            Defaults to
            :attr:`~ccnl_engine.payroll.domain.eligibility.ContributionCeilingStatus.UNKNOWN`.
        weekly_hours: Contracted weekly hours, positive.  Required for domestic
            CCNLs (CCNL lavoro domestico) to select the INPS contribution
            bracket.  Must not exceed ``full_time_weekly_hours`` when both are
            given.  ``None`` for non-domestic CCNLs.
        contributable_hours: Actual hours worked in the period, a non-negative
            ``Decimal``.  Required for domestic CCNLs to compute flat-rate INPS
            contributions.  ``None`` for non-domestic CCNLs.
        full_time_weekly_hours: Standard full-time weekly hours for the CCNL,
            positive, used to compute the part-time fraction.  ``None`` when
            not applicable.
        started_on: Employment start date.  ``None`` when not tracked.
        ended_on: Employment end date, not before ``started_on``; requires
            ``started_on``.  ``None`` for open-ended contracts.
        seniority_months: Months of continuous service, non-negative, used to
            activate seniority-based allowances.  ``None`` when not tracked.
        roles: Set of role codes that unlock role-specific contractual
            allowances (e.g. ``{"caposquadra"}``).  Empty set by default.
        category: Worker category (:class:`~ccnl_engine.engine.contract.domain\
.category.WorkerCategory`); its string value (e.g. ``"operaio"``) is
            accepted and normalized.  ``None`` takes the category fixed by the
            level, if any.  The calculation raises when the category differs
            from the one the level fixes, or when it is ``None`` and seniority
            increments for the level differ by category.
    """

    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN
    weekly_hours: int | None = None
    contributable_hours: Decimal | None = None
    full_time_weekly_hours: int | None = None
    started_on: date | None = None
    ended_on: date | None = None
    seniority_months: int | None = None
    roles: frozenset[str] = field(default_factory=frozenset)
    category: WorkerCategory | None = None

    def __post_init__(self) -> None:
        """Validate every fact by building its value object.

        The value objects raise ``InvalidInputError`` for impossible facts:
        negative seniority or contributable hours,
        non-positive weekly hours, weekly hours above full time, an end
        date before the start date, or an unknown worker category.  A
        category given as its string value is normalized to the enum.
        """
        _ = (self.seniority, self.contributable, self.period)
        object.__setattr__(self, "category", parse_worker_category(self.category))
        check_within_full_time(self.contracted_hours, self.full_time_hours)

    @property
    def contracted_hours(self) -> WeeklyHours | None:
        """Validated contracted weekly hours, or ``None``."""
        return None if self.weekly_hours is None else WeeklyHours(self.weekly_hours)

    @property
    def full_time_hours(self) -> WeeklyHours | None:
        """Validated full-time weekly hours, or ``None``."""
        if self.full_time_weekly_hours is None:
            return None
        return WeeklyHours(self.full_time_weekly_hours)

    @property
    def contributable(self) -> ContributableHours | None:
        """Validated contributable hours, or ``None``."""
        if self.contributable_hours is None:
            return None
        return ContributableHours(self.contributable_hours)

    @property
    def seniority(self) -> SeniorityMonths | None:
        """Validated months of service, or ``None``."""
        if self.seniority_months is None:
            return None
        return SeniorityMonths(self.seniority_months)

    @property
    def period(self) -> EmploymentPeriod | None:
        """Validated employment period, or ``None`` when no dates are given."""
        return EmploymentPeriod.from_dates(self.started_on, self.ended_on)


@dataclass(frozen=True)
class PayrollRequest:
    """Input for a single payroll run.

    Uses :class:`~ccnl_engine.payroll.domain.run.PayrollRun` as the
    primary identifier, enforcing run identity and kind through the type
    system rather than a plain month number.

    Attributes:
        run: The payroll run being computed.  Carries ``run_id``,
            ``run_kind``, ``month`` and ``year``.
        payment_date: Date on which the payment is made.
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``"metalmeccanico-federmeccanica.json"``.
        level_code: Worker's contractual level code, e.g. ``"C3"``.
        employment_facts: Worker-side employment facts (contract type,
            hours, seniority, IVS ceiling eligibility).
        employer: The employer; its headcount selects the INPS rate tier.
            Defaults to an employer with 50 employees.
        opening_state: YTD state entering this run.  Use
            :meth:`~ccnl_engine.payroll.domain.period.PeriodState.zero`
            for January.
        events: Variable work events for this run.
        regione: ISO region code for regional surtax.  ``None`` skips.
        comune_belfiore: Belfiore code for municipal surtax.  ``None`` skips.
        family_composition: Dependent family composition for tax credits.
        has_dependent_children: Higher fringe-benefit threshold when True.
    """

    run: PayrollRun
    payment_date: date
    ccnl_slug: str
    level_code: str
    employment_facts: EmploymentFacts
    employer: Employer = field(default_factory=Employer)
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    events: tuple[WorkEvent, ...] = field(default_factory=tuple)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False


@dataclass(frozen=True)
class PayrollYearRequest:
    """Input for a full payroll year computation.

    Attributes:
        year: The tax year.
        ccnl_slug: Knowledge-bundle CCNL filename.
        level_code: Worker's contractual level code.
        calendar: Optional
            :class:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride`.
            ``None`` (the default) runs the standard calendar derived from the
            CCNL ``additional_months``.  An override carries a domain reason
            and is rejected with
            :class:`~ccnl_engine.engine.errors.InvalidInputError` when it
            drops or lowers an extra month the CCNL grants, or does not match
            its reason.  A bare ``WorkCalendar`` is rejected.
        employment_facts: Worker-side employment facts (contract type,
            hours, seniority, IVS ceiling eligibility).
        employer: The employer; its headcount selects the INPS rate tier.
            Defaults to an employer with 50 employees.
        period_events: Optional mapping from month number (1-12) to events.
            Extra-month runs (thirteenth, fourteenth) are not addressable here;
            use ``per_run_events`` for explicit run-level allocation.
        per_run_events: Optional mapping from ``run_id`` to events for that
            specific run.  Supports any run kind (regular, thirteenth, etc.).
            A run present in both sources raises :class:`ValueError`.
        regione: ISO region code for regional surtax.
        comune_belfiore: Belfiore code for municipal surtax.
        family_composition: Dependent family composition.
        has_dependent_children: Higher fringe-benefit threshold when True.

    Raises:
        InvalidInputError: When ``calendar`` is neither ``None`` nor a
            :class:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride`,
            e.g. a bare ``WorkCalendar``.
    """

    year: int
    ccnl_slug: str
    level_code: str
    calendar: CalendarOverride | None = None
    employment_facts: EmploymentFacts = field(default_factory=EmploymentFacts)
    employer: Employer = field(default_factory=Employer)
    period_events: dict[int, tuple[WorkEvent, ...]] = field(default_factory=dict)
    per_run_events: dict[str, tuple[WorkEvent, ...]] = field(default_factory=dict)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        _require_calendar_override(self.calendar)


def _require_calendar_override(value: object) -> None:
    if value is not None and not isinstance(value, CalendarOverride):
        msg = (
            f"calendar must be a CalendarOverride or None; got "
            f"{type(value).__name__}: wrap a custom calendar in a "
            f"CalendarOverride with its reason"
        )
        raise InvalidInputError(msg, feature="calendar_override")
