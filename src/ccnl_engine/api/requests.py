"""Canonical request types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.domain.period import PeriodState

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["EmploymentFacts", "PayrollRequest", "PayrollYearRequest"]


@dataclass(frozen=True)
class EmploymentFacts:
    """Employment-side facts used to resolve contribution rates and ceilings.

    Attributes:
        contract_type: Employment contract type (permanent, fixed-term, apprentice).
        num_employees: Employer headcount for INPS rate resolution.
        ceiling_status: Whether the IVS massimale contribution ceiling applies.
            Defaults to
            :attr:`~ccnl_engine.payroll.domain.eligibility.ContributionCeilingStatus.UNKNOWN`.
        weekly_hours: Contracted weekly hours.  Required for domestic CCNLs
            (CCNL lavoro domestico) to select the INPS contribution bracket.
            ``None`` for non-domestic CCNLs.
        contributable_hours: Actual hours worked in the period.  Required for
            domestic CCNLs to compute flat-rate INPS contributions.  ``None``
            for non-domestic CCNLs.
        full_time_weekly_hours: Standard full-time weekly hours for the CCNL,
            used to compute the part-time fraction.  ``None`` when not applicable.
        started_on: Employment start date.  Used to compute the accrual window
            for the first year of service.  ``None`` when not tracked.
        ended_on: Employment end date.  ``None`` for open-ended contracts.
        seniority_months: Months of continuous service, used to activate
            seniority-based allowances.  ``None`` when not tracked.
        roles: Set of role codes that unlock role-specific contractual
            allowances (e.g. ``{"caposquadra"}``).  Empty set by default.
        category: Worker category code (e.g. ``"operaio"``, ``"impiegato"``).
            ``None`` when not applicable or unknown.
    """

    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    num_employees: int = 50
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN
    weekly_hours: int | None = None
    contributable_hours: Decimal | None = None
    full_time_weekly_hours: int | None = None
    started_on: date | None = None
    ended_on: date | None = None
    seniority_months: int | None = None
    roles: frozenset[str] = field(default_factory=frozenset)
    category: str | None = None


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
        employment_facts: Employment-side facts (contract type, headcount,
            IVS ceiling eligibility).
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
        calendar: Year-level payroll calendar; governs the run sequence.
        employment_facts: Employment-side facts (contract type, headcount,
            IVS ceiling eligibility).
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
    """

    year: int
    ccnl_slug: str
    level_code: str
    calendar: WorkCalendar
    employment_facts: EmploymentFacts = field(default_factory=EmploymentFacts)
    period_events: dict[int, tuple[WorkEvent, ...]] = field(default_factory=dict)
    per_run_events: dict[str, tuple[WorkEvent, ...]] = field(default_factory=dict)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False
