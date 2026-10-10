"""Request of one period-first payroll calculation."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.contribution.inputs_eligibility import ContributionHistory
from ccnl_engine.payroll.contribution.inputs_pension_fund import PENSION_FUND_TYPES
from ccnl_engine.payroll.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile
from ccnl_engine.payroll.employment.inputs_fact import (
    ContributableHours,
    EmploymentPeriod,
    PublicEndOfService,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.employment.inputs_seniority import SeniorityFact
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.validators_request import employment_gap
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.taxation.inputs_current_year import CurrentYearTaxFacts
from ccnl_engine.payroll.taxation.inputs_prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.taxation.types_jurisdiction import check_surtax_codes
from ccnl_engine.payroll.termination.models_tfr_fund import TfrFundBalance
from ccnl_engine.payroll.year.rules_tax_year import TaxYearPolicy
from ccnl_engine.tax.regime.models import EmploymentSector
from ccnl_engine.validation import FieldSpec, require_instances

if TYPE_CHECKING:
    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.payroll.accrual.models import ExtraMonthAccrual
    from ccnl_engine.payroll.contribution.inputs_pension_fund import (
        NoPensionFund,
        PensionFundEnrolment,
    )
    from ccnl_engine.payroll.event.facade import WorkEvent
    from ccnl_engine.payroll.family.inputs import FamilyComposition
    from ccnl_engine.payroll.period.models_run import PayrollRun, PayrollRunId
    from ccnl_engine.payroll.withholding.models_schedule import WithholdingSchedule
    from ccnl_engine.payroll.year.models_payment import PaymentId


@dataclass(frozen=True)
class PeriodCalculationRequest:
    """Input for a single period-first payroll calculation.

    Attributes:
        period_id: The competence period (year, month).  Governs the
            contractual lookups: salary table, seniority, allowances.
        payment_date: Date on which the payment is made, not before the
            first day of ``period_id``.  Selects the tax year, hence the tax
            rules and INPS rates
            (:class:`~ccnl_engine.payroll.year.rules_tax_year.TaxYearPolicy`),
            and is propagated to every ledger entry and pay item.
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``metalmeccanico-federmeccanica.json``.
        level_code: Worker's contractual level code, e.g. ``C3``.
        opening_state: State entering this period, with the history of
            the employment.  :meth:`PeriodState.zero` is the fact only for
            the first run of an employment whose start is stated; use
            :func:`~ccnl_engine.payroll.year.rules_close\
.close_tax_year` for the first run of a later tax year.  A state that
            misses the history gives a ``missing_fact opening_state`` issue
            (:mod:`~ccnl_engine.payroll.state.rules_opening_history`).
        employer: The employer; its headcount resolves INPS rates (some
            rates differ by firm size) and its activity the regimes that
            exclude some activities.
        contribution_history: Pension history the IVS massimale eligibility
            is derived from.  ``None`` means not known: a run whose INPS base
            crosses the massimale is then incomplete, with a ``missing_fact``
            blocker for ``contribution_history``.
        events: Variable work events of the period (overtime, absences...).
        regione: ISO 3166-2:IT region code for the regional surtax, e.g.
            ``"IT-45"``, with ``"IT-BZ"`` / ``"IT-TN"`` for the autonomous
            provinces (:data:`~ccnl_engine.payroll.taxation.types_jurisdiction\
.REGION_CODES`).  ``None`` is unknown: when the employer withholds,
            a ``residence_unknown`` decision and a ``requirement_unresolved``
            blocker on ``addizionale_regionale``.
        comune_belfiore: Belfiore code for the municipal surtax, e.g.
            ``"F257"``.  ``None`` is unknown, as for ``regione``, on
            ``addizionale_comunale``.
        weekly_hours: Contracted weekly hours, positive: the INPS bracket of
            a domestic CCNL, the part time below ``full_time_weekly_hours``.
        contributable_hours: Hours worked and paid subject to INPS
            contributions (domestic CCNLs).  ``ordinary_hours_worked``: the
            ordinary hours actually worked (Prevedi operai).
        full_time_weekly_hours: Full-time weekly hours of the contract,
            positive.  ``weekly_hours`` must not exceed it.
        employment_period: Start and optional end of the employment.
            ``None`` when not tracked.
            :func:`~ccnl_engine.payroll.year.services_tax_year.calculate_tax_year`
            uses it to select the runs of the year.  A regular run must fall
            in a month with at least one day of employment.
        seniority: Recognised seniority, aged to the competence month.
            ``None`` means not known: when the level pays seniority
            increments or service-gated allowances the run has a
            ``missing_fact`` blocker.
        roles: Role codes of the role-specific allowances, ``None`` unknown.
        category: Worker category declared on the employment.  ``None``
            takes the category fixed by the level, if any.  Must match the
            level's category when the level fixes one, and is required when
            seniority increments for the level differ by category.
        withholding_schedule: Withholding slots of the tax year, one per
            payment, used by the IRPEF projection and conguaglio.  A year
            or tax-year plan passes the schedule of its payments.  ``None``
            builds it from the payments closed, this one and
            ``planned_payments``.
        planned_payments: Payments of the tax year still planned after this
            one, in payment order; ``()`` makes this payment the
            conguaglio.  ``None`` projects the runs of the CCNL standard
            calendar that follow this run.
        extra_month_accrual: Rateo of an extra-month run (window, qualifying
            months), from ``calculate_year``; ``None`` counts it from
            ``employment_period`` over the 12 months ending in the run month,
            without absences.  Ignored on a regular run.
        extra_month_settlements: Ratei the run liquidates at the end of the
            employment, as extra-month earnings; ``None`` derives them
            (:mod:`~ccnl_engine.payroll.termination.services_ratei`).
        sector: Private or public sector of the employment, ``None`` when
            not known.  Read by the regimes restricted to one sector.
        prior_year: Prior-year income and written waivers, read by every
            preferential tax regime.
        current_year: Income of the tax year beyond this employment, read
            by the family deductions and the somma esente; ``None`` when not
            known.  When its tax year is the competence year of the run, its
            INPS base of other employments is stated in ``opening_state``
            for that year, in place of the one the state carries.
        pension_fund: Enrolment in a pension fund of the CCNL, if known
            (``NoPensionFund``: not enrolled).
        uncovered_runs: Runs of the competence year the year calculation
            left out because the bundle holds no pay rules on their date.
            They are reported once, as ``run_not_computed`` blockers of the
            year, so the opening state is not judged to miss them.
        tfr_fund: TFR fund at 31 December of the year before, if known.
        tfr_treasury_fund: Whether the TFR goes to the Fondo Tesoreria.
        erc_amount: Annual ERC of the CCNL grafici editoriali, if known.
        public_end_of_service: End-of-service regime of a public employee.
    """

    period_id: PeriodId
    payment_date: date
    ccnl_slug: str
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
    full_time_weekly_hours: WeeklyHours | None = None
    employment_period: EmploymentPeriod | None = None
    seniority: SeniorityFact | None = None
    roles: frozenset[str] | None = None
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
    public_end_of_service: PublicEndOfService | None = None

    def __post_init__(self) -> None:
        """Guard dates, cross-year state or schedule and hours above full time.

        The tax year of the run is attributed from ``payment_date`` by
        :class:`~ccnl_engine.payroll.year.rules_tax_year.TaxYearPolicy`; a set
        ``opening_state.tax_year`` (a calculated state always carries it)
        must match it.

        Raises:
            InvalidInputError: When a field is not of its declared type (for
                example a raw ``int`` for ``weekly_hours``), when a regular
                run falls in a month without a day of employment, when
                ``payment_date`` is before the start of
                the competence period, when ``opening_state.tax_year`` is not
                ``None`` and differs from the attributed tax year, or when
                ``withholding_schedule`` belongs to another tax year, or
                when ``regione`` or ``comune_belfiore`` is malformed.
        """
        require_instances(
            "PeriodCalculationRequest", self._field_specs(), feature="period_request"
        )
        gap = employment_gap(self.period_id, self.run, self.employment_period)
        if gap is not None:
            raise InvalidInputError(gap, feature="employment_facts")
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)
        check_surtax_codes(self.regione, self.comune_belfiore)
        competence = date(self.period_id.year, self.period_id.month, 1)
        tax_year = TaxYearPolicy().attribute(competence, self.payment_date).tax_year
        opening_year = self.opening_state.tax_year
        if opening_year is not None and opening_year != tax_year:
            msg = (
                f"run {self.period_id.year}-{self.period_id.month:02d} paid on "
                f"{self.payment_date.isoformat()} belongs to tax year {tax_year} "
                f"(TUIR art. 51 c. 1), but opening_state is for tax year "
                f"{opening_year}: open the new tax year with close_tax_year() "
                "on the closing state of the last run of the previous year"
            )
            raise InvalidInputError(msg, feature="tax_year")
        latest = self.opening_state.cash.obligations.latest_tax_year
        if latest is not None and latest > tax_year:
            msg = (
                f"opening_state carries an obligation opened in {latest}, after "
                f"the tax year of the run ({tax_year})"
            )
            raise InvalidInputError(msg, feature="tax_year")
        object.__setattr__(self, "opening_state", self._stated_opening())
        schedule = self.withholding_schedule
        if schedule is not None and schedule.year != tax_year:
            msg = (
                f"withholding_schedule.year ({schedule.year}) "
                f"does not match tax year ({tax_year})"
            )
            raise InvalidInputError(msg, feature="tax_year")

    def _stated_opening(self) -> PeriodState:
        """Return the opening state with the stated base of other employers.

        Returns:
            ``opening_state``, with the INPS base of other employments of
            ``current_year`` when it is of the competence year.
        """
        year, facts = self.period_id.year, self.current_year
        if facts is None or facts.tax_year != year:
            return self.opening_state
        accrual = self.opening_state.accrual
        base = accrual.inps_base(year).stating_other_employers(
            facts.other_employment_inps_base
        )
        return replace(self.opening_state, accrual=accrual.with_inps_base(base))

    def _field_specs(self) -> tuple[FieldSpec, ...]:
        """Return the fields an untyped caller may supply with a wrong type.

        Returns:
            One spec per checked field: name, value, types, ``None`` allowed.
        """
        return (
            ("period_id", self.period_id, PeriodId, False),
            ("payment_date", self.payment_date, date, False),
            ("ccnl_slug", self.ccnl_slug, str, False),
            ("level_code", self.level_code, str, False),
            ("opening_state", self.opening_state, PeriodState, False),
            (
                "contract_type",
                self.contract_type,
                (Permanent, Apprentice, FixedTerm),
                False,
            ),
            ("employer", self.employer, EmployerProfile, False),
            (
                "contribution_history",
                self.contribution_history,
                ContributionHistory,
                True,
            ),
            ("events", self.events, (tuple, list), False),
            ("weekly_hours", self.weekly_hours, WeeklyHours, True),
            ("contributable_hours", self.contributable_hours, ContributableHours, True),
            (
                "ordinary_hours_worked",
                self.ordinary_hours_worked,
                ContributableHours,
                True,
            ),
            ("full_time_weekly_hours", self.full_time_weekly_hours, WeeklyHours, True),
            ("employment_period", self.employment_period, EmploymentPeriod, True),
            ("seniority", self.seniority, SeniorityFact, True),
            ("sector", self.sector, EmploymentSector, True),
            ("prior_year", self.prior_year, PriorYearTaxFacts, False),
            ("current_year", self.current_year, CurrentYearTaxFacts, True),
            ("pension_fund", self.pension_fund, PENSION_FUND_TYPES, True),
            ("tfr_fund", self.tfr_fund, TfrFundBalance, True),
            ("tfr_treasury_fund", self.tfr_treasury_fund, bool, True),
            ("erc_amount", self.erc_amount, Decimal, True),
            (
                "public_end_of_service",
                self.public_end_of_service,
                PublicEndOfService,
                True,
            ),
        )
