"""Run-scoped facts supplied for a single payroll period."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.compensation.presence.inputs import validate_presence_days
from ccnl_engine.employment.fact.inputs import ContributableHours
from ccnl_engine.event.facade import WORK_EVENT_TYPES
from ccnl_engine.family.inputs import FamilyComposition
from ccnl_engine.period.facts.holiday import PaidHolidayDays
from ccnl_engine.surtax.jurisdiction.types import check_surtax_codes
from ccnl_engine.validators import (
    require_decimal,
    require_instances,
    require_int,
    require_str,
)

if TYPE_CHECKING:
    from ccnl_engine.event.facade import WorkEvent


@dataclass(frozen=True)
class PeriodFacts:
    """Facts that hold in one payroll run.

    Attributes:
        contributable_hours: Hours worked and paid in the run that are
            subject to INPS contributions.  Required for domestic CCNLs.
        ordinary_hours_worked: Ordinary hours actually worked in the month,
            sickness, ferie, permits, festività and other paid absences
            left out: the hours a CCNL with ``hourly_pay`` pays its worker
            (the operai of the building CCNLs) and the base of the Prevedi
            contractual contribution of an operaio.  ``None`` is unknown:
            an operaio then has a ``missing_fact`` blocker.  An
            ``AbsenceEvent`` of a worker paid by the hour is rejected: its
            hours are already left out of them.
        hourly_pay_elements: Sum of additional hourly remuneration elements
            applicable to contractual hourly pay, excluding monthly elements
            already in monthly pay. ``None`` means unknown, zero confirms none.
        paid_holiday_days: Caller-stated eligible holidays in this run, distinct
            from hours worked; ``None`` leaves holiday treatment unrequested.
        presence_days: Days actually present at work in this month; ``None``
            means not supplied, zero means no qualifying days.
        site_presence_days: Of those days, days actually present at the
            contractual work site; ``None`` means not supplied.
        events: Variable work events of the run (overtime, absences,
            bonuses, supplements), each one of the
            :data:`~ccnl_engine.event.types.WorkEvent` types.  A
            list is accepted and stored as a tuple.
        regione: ISO 3166-2:IT region code for the regional surtax, e.g.
            ``"IT-45"``, ``"IT-BZ"`` / ``"IT-TN"`` for the autonomous
            provinces.  ``None`` is unknown: when the employer
            withholds, a ``residence_unknown`` decision and a
            ``requirement_unresolved`` blocker on
            ``addizionale_regionale``.
        comune_belfiore: Belfiore code for the municipal surtax, e.g.
            ``"F257"``.  ``None`` is unknown: when the employer
            withholds, a ``residence_unknown`` decision and a
            ``requirement_unresolved`` blocker on
            ``addizionale_comunale``.
        meal_benefit_days: Days verified as eligible for an electronic
            contractual meal voucher (including the employer's canteen and
            shift conditions). ``None`` is unknown: a CCNL with a daily meal
            rate reports a missing fact; zero declares no eligible days.
            Exclude absences from the count. Paper vouchers have different
            tax limits and must not be declared here.
        family_composition: Dependents for the Art. 12 TUIR deductions.
            ``None`` is unknown: when the employer withholds, a
            ``requirement_unresolved`` blocker on ``family_deductions``;
            ``FamilyComposition()`` states that there is no dependant.  Its
            children also select the fringe-benefit threshold: the higher
            one when a child is within the own-income limit of art. 12
            c. 2 TUIR (L. 207/2024 art. 1 c. 390).

    Raises:
        InvalidInputError: When a field is not of its type, an event is not
            a work event, or a surtax code is malformed.
    """

    contributable_hours: ContributableHours | None = None
    ordinary_hours_worked: ContributableHours | None = None
    paid_holiday_days: PaidHolidayDays | None = None
    hourly_pay_elements: Decimal | None = None
    presence_days: int | None = None
    site_presence_days: int | None = None
    events: tuple[WorkEvent, ...] = ()
    regione: str | None = None
    comune_belfiore: str | None = None
    meal_benefit_days: int | None = None
    family_composition: FamilyComposition | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "period_facts"
        require_instances(
            "PeriodFacts",
            (
                (
                    "contributable_hours",
                    self.contributable_hours,
                    ContributableHours,
                    True,
                ),
                (
                    "ordinary_hours_worked",
                    self.ordinary_hours_worked,
                    ContributableHours,
                    True,
                ),
                ("paid_holiday_days", self.paid_holiday_days, PaidHolidayDays, True),
                (
                    "family_composition",
                    self.family_composition,
                    FamilyComposition,
                    True,
                ),
            ),
            feature=feature,
        )
        require_str(self.regione, "PeriodFacts.regione", feature=feature, optional=True)
        require_str(
            self.comune_belfiore,
            "PeriodFacts.comune_belfiore",
            feature=feature,
            optional=True,
        )
        require_decimal(
            self.hourly_pay_elements,
            "PeriodFacts.hourly_pay_elements",
            feature=feature,
            minimum=Decimal(0),
            optional=True,
        )
        validate_presence_days(
            self.presence_days, self.site_presence_days, owner="PeriodFacts"
        )
        require_int(
            self.meal_benefit_days,
            "PeriodFacts.meal_benefit_days",
            feature=feature,
            minimum=0,
            maximum=31,
            optional=True,
        )
        events = tuple_of(
            self.events,
            "PeriodFacts.events",
            items_of_type(WORK_EVENT_TYPES, feature=feature, name="a WorkEvent"),
            feature=feature,
        )
        object.__setattr__(self, "events", events)
        check_surtax_codes(self.regione, self.comune_belfiore)
