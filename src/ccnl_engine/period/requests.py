"""Request of one period-first payroll calculation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employer.inputs import EmployerProfile
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
    check_pattern_hours,
    check_within_full_time,
)
from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.employment.level_start import check_level_start
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.employment.rota.inputs import Rota
from ccnl_engine.employment.week_days.inputs import check_week_days
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import CurrentYearTaxFacts
from ccnl_engine.period.facts.holiday import PaidHolidayDays
from ccnl_engine.period.opening.requests import validate_tax_year
from ccnl_engine.period.request.fields import period_field_specs
from ccnl_engine.period.request.opening_state import stated_opening
from ccnl_engine.period.request.validators import (
    check_day_counts,
    check_prior_extra_amount,
    employment_gap,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.surtax.jurisdiction.types import check_surtax_codes
from ccnl_engine.validators import require_decimal, require_instances

if TYPE_CHECKING:
    from ccnl_engine.calendar.payment.models import PaymentId
    from ccnl_engine.compensation.individual.inputs import IndividualElement
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.event.facade import WorkEvent
    from ccnl_engine.extra_month.models import ExtraMonthAccrual
    from ccnl_engine.family.inputs import FamilyComposition
    from ccnl_engine.pension_fund.inputs import NoPensionFund, PensionFundEnrolment
    from ccnl_engine.personal_withholding.inputs import PersonalWithholding
    from ccnl_engine.run.models import PayrollRun, PayrollRunId
    from ccnl_engine.withholding.schedule.models import WithholdingSchedule


@dataclass(frozen=True)
class PeriodCalculationRequest:
    """Input for a single period-first payroll calculation.

    Attributes:
        period_id: The competence period (year, month).  Governs the
            contractual lookups: salary table, seniority, allowances.
        payment_date: Date on which the payment is made, not before the
            first day of ``period_id``.  Selects the tax year, hence the tax
            rules and INPS rates
            (:class:`~ccnl_engine.calendar.tax_year.rules.TaxYearPolicy`),
            and is propagated to every ledger entry and pay item.
        ccnl_id: Slug (``metalmeccanico-federmeccanica``) or CNEL code (``E042``).
        level_code: Contractual level code, e.g. ``C3``.
        level_started_on: Date the worker entered the level, if known.
        opening_state: State entering this period, with the history of
            the employment.  :meth:`PeriodState.zero` is the fact only for
            the first run of an employment whose start is stated; use
            :func:`~ccnl_engine.year.tax_year.closing.rules.close_tax_year` for the
            first run of a later tax year.  Missing history gives a
            ``missing_fact opening_state`` issue.
        employer: The employer; its headcount resolves INPS rates (some
            rates differ by firm size) and its activity the applicable regimes.
        contribution_history: Pension history the IVS massimale eligibility
            is derived from.  ``None`` means not known: a run whose INPS base
            crosses the massimale gives a ``missing_fact`` blocker.
        events: Variable work events of the period (overtime, absences...).
        regione: ISO 3166-2:IT region code for the regional surtax, e.g.
            ``"IT-45"``, with ``"IT-BZ"`` / ``"IT-TN"`` for the autonomous
            provinces (:data:`~ccnl_engine.surtax.jurisdiction.types.REGION_CODES`).
            ``None`` is unknown: when the employer withholds,
            a ``residence_unknown`` decision and a ``requirement_unresolved``
            blocker on ``addizionale_regionale``.
        comune_belfiore: Belfiore code for the municipal surtax (``"F257"``),
            ``None`` unknown as for ``regione``, on ``addizionale_comunale``.
        weekly_hours: Contracted weekly hours, positive: the INPS bracket of
            a domestic CCNL, the part time below ``full_time_weekly_hours``.
        contributable_hours: Hours worked and paid subject to INPS
            contributions (domestic CCNLs).  ``ordinary_hours_worked``: the
            ordinary hours actually worked, which a CCNL with ``hourly_pay``
            pays (operai edili) and the Prevedi operai amount is due on.
            ``paid_holiday_days`` separately counts eligible paid holidays.
        full_time_weekly_hours: Full-time weekly hours, at least ``weekly_hours``;
            ``full_time_week_days`` its days, 5 or 6; ``rota`` a guard's rota.
        work_pattern: Vertical or mixed part time: weekday hours summing to
            ``weekly_hours`` and the months worked.  A regular or termination run of a
            month not worked posts no monthly pay, and the months not worked accrue no
            extra-month rateo.  ``None`` for a horizontal part time or a full time.
        employment_period: Start and optional end of the employment, ``None`` when
            not tracked; it selects the runs of the year, and a regular run must
            fall in a month with at least one day of employment.
        weekly_rest_day: Day of the weekly rest, for a CCNL paying a holiday on it.
        seniority: Recognised seniority, aged to the competence month; ``None``
            unknown, a ``missing_fact`` blocker when the level pays on seniority.
        roles: Role codes of allowances and former-worker pay; ``None`` unknown.
        presence_days: Count of days actually present at work in the month.
        site_presence_days: Subset of those days present at the work site.
            ``None`` means the count is missing, not zero.
        meal_benefit_days: Verified eligible days for electronic meal vouchers,
            excluding absences; ``None`` is unknown. Not for paper vouchers.
        individual_elements: Pay agreed above the CCNL minimum, fixed allowances.
        category: Worker category declared on the employment.  ``None``
            takes the category fixed by the level, if any.  Must match the
            level's category when the level fixes one, and is required when
            seniority increments for the level differ by category.
        withholding_schedule: Withholding slots of the tax year, one per
            payment, used by the IRPEF projection and conguaglio.  A year
            or tax-year plan passes the schedule of its payments.  ``None``
            builds it from the payments closed, this one and
            ``planned_payments``.
        planned_payments: Payments of the tax year still planned after this one, in
            payment order; ``()`` makes this payment the conguaglio.  ``None`` projects
            the runs of the CCNL standard calendar that follow this run.
        extra_month_accrual: Rateo of an extra-month run (window, qualifying
            months), from ``calculate_year``; ``None`` counts it from
            ``employment_period`` over the 12 months ending in the run month,
            without absences.  Ignored on a regular run.
        extra_month_settlements: Ratei the run liquidates at the end of the employment,
            as extra-month earnings; ``None`` derives them
            (:mod:`~ccnl_engine.extra_month.liquidation.services`).
        sector: Private or public sector, ``None`` unknown; read by one-sector regimes.
        prior_year: Prior-year income and written waivers, read by every
            preferential tax regime.
        current_year: Income of the tax year beyond this employment, read
            by the family deductions and the somma esente; ``None`` when not
            known.  When its tax year is the competence year of the run, its
            INPS base of other employments is stated in ``opening_state``
            for that year, in place of the one the state carries.
        pension_fund: Enrolment in a CCNL pension fund (``NoPensionFund``: none).
        uncovered_runs: Runs of the competence year the year calculation left out
            because the bundle holds no pay rules on their date. They are reported once,
            as ``run_not_computed`` blockers of the year, so the opening state is not
            judged to miss them.
        tfr_fund: TFR fund at 31 December of the year before, if known;
            ``tfr_treasury_fund`` whether the TFR goes to the Fondo Tesoreria.
        holiday_company_offset: Company compensation already paid for eligible
            former-worker holiday supplements of this month; zero means none.
        prior_extra_month_amount: Full extra monthly remuneration already
            received beyond the thirteenth at contract entry, excluding merit
            bonuses; zero states none, ``None`` is unknown.
        erc_amount: Annual ERC of the CCNL grafici editoriali, if known;
            ``public_end_of_service`` the regime of a public employee.
        personal_withholdings: Garnishments and salary assignments notified
            to the employer, withheld from the net pay.
    """

    period_id: PeriodId
    payment_date: date
    ccnl_id: str
    level_code: str
    employer: EmployerProfile
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    contribution_history: ContributionHistory | None = None
    events: tuple[WorkEvent, ...] = field(default_factory=tuple)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    run: PayrollRun | None = None
    weekly_hours: WeeklyHours | None = None
    contributable_hours: ContributableHours | None = None
    ordinary_hours_worked: ContributableHours | None = None
    paid_holiday_days: PaidHolidayDays | None = None
    full_time_weekly_hours: WeeklyHours | None = None
    full_time_week_days: int | None = None
    rota: Rota | None = None
    work_pattern: WorkPattern | None = None
    weekly_rest_day: Weekday = Weekday.SUNDAY
    employment_period: EmploymentPeriod | None = None
    level_started_on: date | None = None
    seniority: SeniorityFact | None = None
    roles: frozenset[str] | None = None
    presence_days: int | None = None
    site_presence_days: int | None = None
    meal_benefit_days: int | None = None
    individual_elements: tuple[IndividualElement, ...] = ()
    category: WorkerCategory | None = None
    extra_month_accrual: ExtraMonthAccrual | None = None
    extra_month_settlements: tuple[ExtraMonthAccrual, ...] | None = None
    withholding_schedule: WithholdingSchedule | None = None
    planned_payments: tuple[PaymentId, ...] | None = None
    sector: EmploymentSector | None = None
    prior_year: PriorYearTaxFacts = field(default_factory=PriorYearTaxFacts)
    current_year: CurrentYearTaxFacts | None = None
    pension_fund: PensionFundEnrolment | NoPensionFund | None = None
    uncovered_runs: tuple[PayrollRunId, ...] = ()
    tfr_fund: TfrFundBalance | None = None
    tfr_treasury_fund: bool | None = None
    erc_amount: Decimal | None = None
    prior_extra_month_amount: Decimal | None = None
    holiday_company_offset: Decimal | None = None
    public_end_of_service: PublicEndOfService | None = None
    personal_withholdings: tuple[PersonalWithholding, ...] = ()

    def __post_init__(self) -> None:
        """Guard dates, cross-year state or schedule and hours above full time.

        Payment date determines the tax year; the opening state must match.

        Raises:
            InvalidInputError: On malformed fields, absent employment in a
                regular run, invalid level start, payment before competence,
                conflicting tax years or malformed jurisdiction codes.
        """
        require_instances(
            "PeriodCalculationRequest", self._field_specs(), feature="period_request"
        )
        require_decimal(
            self.holiday_company_offset,
            "PeriodCalculationRequest.holiday_company_offset",
            feature="period_request",
            minimum=Decimal(0),
            optional=True,
        )
        check_level_start(
            self.level_started_on,
            self.employment_period,
            (self.period_id.year, self.period_id.month),
        )
        gap = employment_gap(self.period_id, self.run, self.employment_period)
        if gap is not None:
            raise InvalidInputError(gap, feature="employment_facts")
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)
        check_week_days(self.full_time_week_days)
        check_pattern_hours(self.weekly_hours, self.work_pattern)
        check_surtax_codes(self.regione, self.comune_belfiore)
        check_prior_extra_amount(self.prior_extra_month_amount)
        check_day_counts(self)
        validate_tax_year(
            self.period_id,
            self.payment_date,
            self.opening_state,
            self.withholding_schedule,
        )
        object.__setattr__(self, "opening_state", self._stated_opening())

    def _stated_opening(self) -> PeriodState:
        """Return the opening state with the stated base of other employers.

        Returns:
            ``opening_state``, with the INPS base of other employments of
            ``current_year`` when it is of the competence year.
        """
        return stated_opening(self)

    _field_specs = period_field_specs
