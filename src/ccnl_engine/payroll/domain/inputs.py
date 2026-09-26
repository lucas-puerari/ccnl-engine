"""Public inputs of one payroll run.

:class:`PeriodInput` describes one payroll run; :class:`~ccnl_engine\
.payroll.domain.year_input.YearInput` every run of a tax year.  Both group
the facts by owner: :class:`~ccnl_engine.payroll.domain.employment.Employment`
for the contract and the worker,
:class:`~ccnl_engine.payroll.domain.employer.EmployerProfile` for the
employer, :class:`~ccnl_engine.payroll.domain.prior_year.PriorYearTaxFacts`
for what the tax regimes read once a year, and :class:`PeriodFacts` for what
holds in one run.  Every input is validated on construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.employer import EmployerProfile
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.employment_facts import ContributableHours
from ccnl_engine.payroll.domain.family import FamilyComposition
from ccnl_engine.payroll.domain.jurisdiction import check_surtax_codes
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.request_checks import raise_on, type_error
from ccnl_engine.payroll.domain.run import PayrollRun

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule

__all__ = ["PeriodFacts", "PeriodInput"]


@dataclass(frozen=True)
class PeriodFacts:
    """Facts that hold in one payroll run.

    Attributes:
        contributable_hours: Hours worked and paid in the run that are
            subject to INPS contributions.  Required for domestic CCNLs.
        events: Variable work events of the run (overtime, absences,
            bonuses, supplements).  A list is accepted and stored as a tuple.
        regione: ISO 3166-2:IT region code for the regional surtax, e.g.
            ``"IT-45"``, ``"IT-BZ"`` / ``"IT-TN"`` for the autonomous
            provinces.  ``None`` skips the regional surtax.
        comune_belfiore: Belfiore code for the municipal surtax, e.g.
            ``"F257"``.  ``None`` skips the municipal surtax.
        family_composition: Dependents for the Art. 12 TUIR deductions.
        has_dependent_children: Whether the worker has a fiscally dependent
            child; selects the higher fringe-benefit threshold.

    Raises:
        InvalidInputError: When a field is not of its type or a surtax code
            is malformed.
    """

    contributable_hours: ContributableHours | None = None
    events: tuple[WorkEvent, ...] = ()
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        raise_on(
            type_error((
                (
                    "contributable_hours",
                    self.contributable_hours,
                    ContributableHours,
                    True,
                ),
                ("events", self.events, (tuple, list), False),
                ("regione", self.regione, str, True),
                ("comune_belfiore", self.comune_belfiore, str, True),
                (
                    "family_composition",
                    self.family_composition,
                    FamilyComposition,
                    True,
                ),
                ("has_dependent_children", self.has_dependent_children, bool, False),
            )),
            "period_facts",
        )
        object.__setattr__(self, "events", tuple(self.events))
        check_surtax_codes(self.regione, self.comune_belfiore)


@dataclass(frozen=True)
class PeriodInput:
    """Input of one payroll run.

    Attributes:
        run: The run: its month, year and kind.
        payment_date: Date the run is paid.  Selects the tax year
            (:class:`~ccnl_engine.payroll.domain.tax_year.TaxYearPolicy`).
        employment: Contract, level and worker facts.
        employer: The employer.  Required: its headcount selects the INPS
            rate tier.
        facts: Facts of the run.  Defaults to a run with no event and no
            surtax jurisdiction.
        prior_year: Prior-year income and waivers.  Defaults to unknown
            income and no waiver.
        opening_state: State entering the run.  Use
            :meth:`~ccnl_engine.payroll.domain.period_state.PeriodState.zero` for
            the first run of an employment, the ``closing_state`` of the
            previous run within a tax year, or ``close_tax_year()`` of the
            last run of the previous year.

    Raises:
        InvalidInputError: When a field is not of its type, a regular run
            falls outside the employment, the payment precedes the run month,
            or ``opening_state`` belongs to another tax year.
    """

    run: PayrollRun
    payment_date: date
    employment: Employment
    employer: EmployerProfile
    facts: PeriodFacts = field(default_factory=PeriodFacts)
    prior_year: PriorYearTaxFacts = field(default_factory=PriorYearTaxFacts)
    opening_state: PeriodState = field(default_factory=PeriodState.zero)

    def __post_init__(self) -> None:  # noqa: D105
        raise_on(
            type_error((
                ("run", self.run, PayrollRun, False),
                ("payment_date", self.payment_date, date, False),
                ("employment", self.employment, Employment, False),
                ("employer", self.employer, EmployerProfile, False),
                ("facts", self.facts, PeriodFacts, False),
                ("prior_year", self.prior_year, PriorYearTaxFacts, False),
                ("opening_state", self.opening_state, PeriodState, False),
            )),
            "period_input",
        )
        self.calculation_request()

    def calculation_request(
        self,
        *,
        extra_month_accrual: ExtraMonthAccrual | None = None,
        extra_month_settlements: tuple[ExtraMonthAccrual, ...] = (),
        withholding_schedule: WithholdingSchedule | None = None,
    ) -> PeriodCalculationRequest:
        """Map this input to the request of the period calculation.

        The only mapping from the public input to the internal request, used
        by both the single-run and the year calculation.

        Args:
            extra_month_accrual: Rateo of an extra-month run, supplied by the
                year calculation.
            extra_month_settlements: Ratei liquidated on this run because the
                employment ends before their payment month.
            withholding_schedule: Withholding slots of the tax year.
                ``None`` uses the standard calendar of the CCNL.

        Returns:
            The validated request.
        """
        employment, facts = self.employment, self.facts
        return PeriodCalculationRequest(
            period_id=PeriodId(year=self.run.year, month=self.run.month),
            payment_date=self.payment_date,
            ccnl_slug=employment.ccnl_slug,
            level_code=employment.level_code,
            employer=self.employer,
            opening_state=self.opening_state,
            contract_type=employment.contract_type,
            ceiling_status=employment.ceiling_status,
            events=facts.events,
            regione=facts.regione,
            comune_belfiore=facts.comune_belfiore,
            family_composition=facts.family_composition,
            has_dependent_children=facts.has_dependent_children,
            run=self.run,
            weekly_hours=employment.weekly_hours,
            contributable_hours=facts.contributable_hours,
            full_time_weekly_hours=employment.full_time_weekly_hours,
            employment_period=employment.employment_period,
            seniority_months=employment.seniority_months,
            roles=employment.roles,
            category=employment.category,
            sector=employment.sector,
            prior_year=self.prior_year,
            extra_month_accrual=extra_month_accrual,
            extra_month_settlements=extra_month_settlements,
            withholding_schedule=withholding_schedule,
        )
