"""Canonical request types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.domain.period import PeriodState

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["PayrollRequest", "PayrollYearRequest"]


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
        opening_state: YTD state entering this run.  Use
            :meth:`~ccnl_engine.payroll.domain.period.PeriodState.zero`
            for January.
        events: Variable work events for this run.
        contract_type: Employment contract type.
        num_employees: Employer headcount for INPS rate resolution.
        regione: ISO region code for regional surtax.  ``None`` skips.
        comune_belfiore: Belfiore code for municipal surtax.  ``None`` skips.
        family_composition: Dependent family composition for tax credits.
        has_dependent_children: Higher fringe-benefit threshold when True.
    """

    run: PayrollRun
    payment_date: date
    ccnl_slug: str
    level_code: str
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    events: tuple[WorkEvent, ...] = field(default_factory=tuple)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    num_employees: int = 50
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
        period_events: Optional mapping from month number (1-12) to events.
        contract_type: Employment contract type.
        num_employees: Employer headcount for INPS rate resolution.
        regione: ISO region code for regional surtax.
        comune_belfiore: Belfiore code for municipal surtax.
        family_composition: Dependent family composition.
        has_dependent_children: Higher fringe-benefit threshold when True.
    """

    year: int
    ccnl_slug: str
    level_code: str
    calendar: WorkCalendar
    period_events: dict[int, tuple[WorkEvent, ...]] = field(default_factory=dict)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    num_employees: int = 50
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False
