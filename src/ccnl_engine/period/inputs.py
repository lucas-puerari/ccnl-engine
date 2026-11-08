"""Public inputs of one payroll run.

:class:`PeriodInput` describes one payroll run; the year plans
(:class:`~ccnl_engine.year.competence.inputs.CompetenceYearPlan`,
:class:`~ccnl_engine.year.tax_year.inputs.TaxYearPlan`) every run of
a tax year.  Both group
the facts by owner: :class:`~ccnl_engine.employment.inputs.Employment`
for the contract and the worker,
:class:`~ccnl_engine.employer.inputs.EmployerProfile` for the
employer, :class:`~ccnl_engine.irpef.declaration.inputs.PriorYearTaxFacts`
for what the tax regimes read once a year, and :class:`PeriodFacts` for what
holds in one run.  Every input is validated on construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.calendar.payment.models import PaymentId
from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.employer.inputs import EmployerProfile
from ccnl_engine.employment.inputs import Employment
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import CurrentYearTaxFacts
from ccnl_engine.period.facts.inputs import PeriodFacts as PeriodFacts  # noqa: PLC0414
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId
from ccnl_engine.validators import require_date, require_instances

if TYPE_CHECKING:
    from ccnl_engine.extra_month.models import ExtraMonthAccrual
    from ccnl_engine.run.models import PayrollRunId
    from ccnl_engine.withholding.schedule.models import WithholdingSchedule

__all__ = ["PeriodFacts", "PeriodInput"]


@dataclass(frozen=True)
class PeriodInput:
    """Input of one payroll run.

    Attributes:
        run: The run: its month, year and kind.
        payment_date: Date the run is paid.  Selects the tax year
            (:class:`~ccnl_engine.calendar.tax_year.rules.TaxYearPolicy`).
        employment: Contract, level and worker facts.
        employer: The employer.  Required: its headcount selects the INPS
            rate tier.
        facts: Facts of the run.  Defaults to a run with no event and no
            surtax jurisdiction.
        prior_year: Prior-year income and waivers.  Defaults to unknown
            income and no waiver.
        current_year: Income of the tax year beyond this employment, which
            the family deductions add to the employment income of the year
            to get the reddito complessivo, and the INPS base of the other
            employments of the year.  ``None`` means not known: with a
            dependent that gives right to a deduction, or INPS rules with a
            massimale or a 1% threshold and no base of other employments in
            ``opening_state``, the result is not payable.
        opening_state: State entering the run, with the history of the
            employment.  The default
            :meth:`~ccnl_engine.balance.models.PeriodState.zero`
            is the fact only for the first run of an employment whose
            ``employment_period`` starts in the run month; pass the
            ``closing_state`` of the previous run within a tax year,
            ``close_tax_year()`` of the last run of the previous year, or
            imported balances.  A state that misses the history gives a
            ``missing_fact opening_state`` blocker.
        planned_payments: Payments of the same tax year still planned after
            this one, in payment order, when they differ from the CCNL
            standard calendar.  ``()`` makes this payment the conguaglio:
            pass it on the last payment of a tax year whose December is
            paid after 12 January.  ``None`` (the default) projects the
            standard runs that follow this run and are not yet paid.

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
    current_year: CurrentYearTaxFacts | None = None
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    planned_payments: tuple[PaymentId, ...] | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_instances(
            "PeriodInput",
            (
                ("run", self.run, PayrollRun, False),
                ("employment", self.employment, Employment, False),
                ("employer", self.employer, EmployerProfile, False),
                ("facts", self.facts, PeriodFacts, False),
                ("prior_year", self.prior_year, PriorYearTaxFacts, False),
                ("current_year", self.current_year, CurrentYearTaxFacts, True),
                ("opening_state", self.opening_state, PeriodState, False),
            ),
            feature="period_input",
        )
        require_date(
            self.payment_date, "PeriodInput.payment_date", feature="period_input"
        )
        if self.planned_payments is not None:
            planned = tuple_of(
                self.planned_payments,
                "PeriodInput.planned_payments",
                items_of_type(PaymentId, feature="period_input"),
                feature="period_input",
            )
            object.__setattr__(self, "planned_payments", planned)
        self.employment.check_seniority_in(self.run.year, self.run.month)
        self.calculation_request()

    def calculation_request(
        self,
        *,
        extra_month_accrual: ExtraMonthAccrual | None = None,
        extra_month_settlements: tuple[ExtraMonthAccrual, ...] | None = None,
        withholding_schedule: WithholdingSchedule | None = None,
        uncovered_runs: tuple[PayrollRunId, ...] = (),
    ) -> PeriodCalculationRequest:
        """Map this input to the request of the period calculation.

        The only mapping from the public input to the internal request, used
        by both the single-run and the year calculation.

        Args:
            extra_month_accrual: Rateo of an extra-month run, supplied by the
                year calculation.
            extra_month_settlements: Ratei liquidated on this run because the
                employment ends before their payment month, supplied by the
                year calculation.  ``None`` derives them from the CCNL
                calendar.
            withholding_schedule: Withholding slots of the tax year.
                ``None`` uses the standard calendar of the CCNL.
            uncovered_runs: Runs of the year the year calculation left out
                because the bundle holds no pay rules on their date.

        Returns:
            The validated request.
        """
        employment, facts = self.employment, self.facts
        return PeriodCalculationRequest(
            period_id=PeriodId(year=self.run.year, month=self.run.month),
            payment_date=self.payment_date,
            ccnl_id=employment.ccnl_id,
            level_code=employment.level_code,
            employer=self.employer,
            opening_state=self.opening_state,
            contract_type=employment.contract_type,
            contribution_history=employment.contribution_history,
            events=facts.events,
            regione=facts.regione,
            comune_belfiore=facts.comune_belfiore,
            family_composition=facts.family_composition,
            run=self.run,
            weekly_hours=employment.weekly_hours,
            contributable_hours=facts.contributable_hours,
            ordinary_hours_worked=facts.ordinary_hours_worked,
            full_time_weekly_hours=employment.full_time_weekly_hours,
            full_time_week_days=employment.full_time_week_days,
            rota=employment.rota,
            work_pattern=employment.work_pattern,
            weekly_rest_day=employment.weekly_rest_day,
            employment_period=employment.employment_period,
            level_started_on=employment.level_started_on,
            seniority=employment.seniority,
            roles=employment.roles,
            presence_days=facts.presence_days,
            site_presence_days=facts.site_presence_days,
            individual_elements=employment.individual_elements,
            category=employment.category,
            sector=employment.sector,
            pension_fund=employment.pension_fund,
            tfr_fund=employment.tfr_fund,
            tfr_treasury_fund=employment.tfr_treasury_fund,
            erc_amount=employment.erc_amount,
            public_end_of_service=employment.public_end_of_service,
            personal_withholdings=employment.personal_withholdings,
            prior_year=self.prior_year,
            current_year=self.current_year,
            extra_month_accrual=extra_month_accrual,
            extra_month_settlements=extra_month_settlements,
            withholding_schedule=withholding_schedule,
            uncovered_runs=uncovered_runs,
            planned_payments=self.planned_payments,
        )
