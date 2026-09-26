"""Domain types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, final

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.tax.domain.preferential_regime import EmploymentSector
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    SeniorityMonths,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.domain.jurisdiction import check_surtax_codes
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.request_checks import (
    FieldSpec,
    employment_gap,
    type_error,
)
from ccnl_engine.payroll.domain.tax_year import TaxYearPolicy
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState

if TYPE_CHECKING:
    from ccnl_engine.engine.capability_catalog import CapabilityReport
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.run import PayrollRun
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax import TaxComputation


@final
@dataclass(frozen=True)
class PeriodState:
    """State entering a payroll run: the tax year and the lasting obligations.

    Pass :meth:`zero` for the first run of an employment.  Between runs of
    one tax year, pass the ``closing_state`` of the previous run.  To open
    the next tax year, pass the closing state of the last run of the year to
    :func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`:
    it resets :attr:`ytd` and carries :attr:`obligations`.

    Attributes:
        ytd: Counters and YTD accounts of the current tax year; they
            restart every tax year.
        obligations: Obligations that survive the change of tax year, such
            as an installment recovery of trattamento integrativo or somma
            esente.
    """

    SCHEMA_VERSION: ClassVar[int] = 3

    ytd: TaxYearState = field(default_factory=TaxYearState)
    obligations: EmploymentObligations = field(default_factory=EmploymentObligations)

    def __post_init__(self) -> None:
        """Reject an obligation opened after the tax year of the state.

        Raises:
            ValueError: When a recovery originates in a year later than
                ``ytd.tax_year``.
        """
        latest = self.obligations.latest_tax_year
        if self.tax_year is not None and latest is not None and latest > self.tax_year:
            msg = (
                f"obligations include a recovery opened in {latest}, after the "
                f"tax year of the state ({self.tax_year})"
            )
            raise ValueError(msg)

    @property
    def tax_year(self) -> int | None:
        """Tax year of :attr:`ytd`; ``None`` when not yet bound to a year."""
        return self.ytd.tax_year

    @classmethod
    def zero(cls) -> PeriodState:
        """Return the state of a new employment: no run closed, no obligation.

        Returns:
            A :class:`PeriodState` with all counters and accumulators at zero.
        """
        return cls()


@dataclass(frozen=True)
class PeriodCalculationRequest:
    """Input for a single period-first payroll calculation.

    Attributes:
        period_id: The competence period (year, month).  Governs the
            contractual lookups: salary table, seniority, allowances.
        payment_date: Date on which the payment is made, not before the
            first day of ``period_id``.  Selects the tax year, hence the tax
            rules and INPS rates
            (:class:`~ccnl_engine.payroll.domain.tax_year.TaxYearPolicy`),
            and is propagated to every ledger entry and pay item.
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``metalmeccanico-federmeccanica.json``.
        level_code: Worker's contractual level code, e.g. ``C3``.
        opening_state: State entering this period.  Use
            :meth:`PeriodState.zero` for the first run of an employment and
            :func:`~ccnl_engine.payroll.application.close_tax_year\
.close_tax_year` for the first run of a later tax year.
        employer: The employer; its headcount resolves INPS rates (some
            rates differ by firm size) and its activity the regimes that
            exclude some activities.
        ceiling_status: Whether the IVS massimale contribution ceiling
            applies to this worker.  Use :attr:`ContributionCeilingStatus.POST_1995`
            for post-1995 workers and :attr:`ContributionCeilingStatus.NOT_APPLICABLE`
            for pre-1996 enrollment.  ``UNKNOWN`` (the default) does not apply
            the ceiling to avoid over-deducting contributions.
        events: Variable work events (overtime, absences, bonuses, etc.)
            that occurred in this period. Defaults to no events.
        regione: ISO 3166-2:IT region code for the regional surtax, e.g.
            ``"IT-45"``, with ``"IT-BZ"`` / ``"IT-TN"`` for the autonomous
            provinces (:data:`~ccnl_engine.payroll.domain.jurisdiction\
.REGION_CODES`).  ``None`` skips the regional surtax.
        comune_belfiore: Belfiore code for the municipal surtax, e.g.
            ``"F257"``.  ``None`` skips the municipal surtax.
        has_dependent_children: Whether the worker has at least one
            fiscally dependent child (figlio a carico).  Selects the
            higher fringe-benefit exemption threshold under Art. 51 c. 3
            TUIR.  Defaults to ``False``.
        weekly_hours: Contracted weekly hours, positive.  Required for
            domestic CCNLs (``lavoro-domestico`` tax sector) to select the
            INPS contribution bracket (above or below the hours threshold).
            Below ``full_time_weekly_hours`` it scales the pay chain for
            part time.
        contributable_hours: Actual hours worked and paid in the period
            that are subject to INPS contributions, non-negative.  Required
            for domestic CCNLs.  Ignored for standard sectors.
        full_time_weekly_hours: Full-time weekly hours of the contract,
            positive.  ``weekly_hours`` must not exceed it.
        employment_period: Start and optional end of the employment.
            ``None`` when not tracked.
            :func:`~ccnl_engine.payroll.application.calculate_year.calculate_year`
            uses it to select the runs of the year.  A regular run must fall
            in a month with at least one day of employment.
        seniority_months: Months of continuous service, non-negative.
            ``None`` means seniority increments are not applied.
        roles: Role codes that unlock role-specific contractual allowances.
        category: Worker category declared on the employment.  ``None``
            takes the category fixed by the level, if any.  Must match the
            level's category when the level fixes one, and is required when
            seniority increments for the level differ by category.
        withholding_schedule: Withholding slots of the tax year, one per
            payslip, used by the IRPEF projection and conguaglio.
            :func:`~ccnl_engine.payroll.application.calculate_year.calculate_year`
            passes the schedule of the runs it computes.  ``None`` uses the
            standard calendar of the CCNL ``additional_months``.
        extra_month_accrual: Rateo of an extra-month run: its window,
            clipped to the hire date, and the qualifying months.
            :func:`~ccnl_engine.payroll.application.calculate_year.calculate_year`
            supplies it.  ``None`` on an extra-month run counts it from
            ``employment_period`` over the 12 months ending in the run month,
            without absences.  Ignored on a regular run.
        extra_month_settlements: Ratei liquidated on this run because the
            employment ends before their payment month.  Each is paid as an
            extra-month earning next to the regular pay.
        sector: Private or public sector of the employment, ``None`` when
            not known.  Read by the regimes restricted to one sector.
        prior_year: Prior-year income and written waivers, read by every
            preferential tax regime.
    """

    period_id: PeriodId
    payment_date: date
    ccnl_slug: str
    level_code: str
    employer: EmployerProfile
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN
    events: tuple[WorkEvent, ...] = field(default_factory=tuple)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False
    run: PayrollRun | None = None
    weekly_hours: WeeklyHours | None = None
    contributable_hours: ContributableHours | None = None
    full_time_weekly_hours: WeeklyHours | None = None
    employment_period: EmploymentPeriod | None = None
    seniority_months: SeniorityMonths | None = None
    roles: frozenset[str] = field(default_factory=frozenset)
    category: WorkerCategory | None = None
    extra_month_accrual: ExtraMonthAccrual | None = None
    extra_month_settlements: tuple[ExtraMonthAccrual, ...] = ()
    withholding_schedule: WithholdingSchedule | None = None
    sector: EmploymentSector | None = None
    prior_year: PriorYearTaxFacts = field(default_factory=PriorYearTaxFacts)

    def __post_init__(self) -> None:
        """Guard dates, cross-year state or schedule and hours above full time.

        The tax year of the run is attributed from ``payment_date`` by
        :class:`~ccnl_engine.payroll.domain.tax_year.TaxYearPolicy`.  When
        ``opening_state.tax_year`` is set, it must match that tax year.
        States produced by :func:`~ccnl_engine.payroll.application\
.calculate_period.calculate_period` always carry ``tax_year``; manually
        constructed states default to ``None`` and are not checked.
        ``weekly_hours`` above ``full_time_weekly_hours`` raises
        :class:`ValueError`.

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
        problem = type_error(self._field_specs())
        if problem is not None:
            raise InvalidInputError(problem, feature="period_request")
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
        latest = self.opening_state.obligations.latest_tax_year
        if latest is not None and latest > tax_year:
            msg = (
                f"opening_state carries a recovery opened in {latest}, after "
                f"the tax year of the run ({tax_year})"
            )
            raise InvalidInputError(msg, feature="tax_year")
        schedule = self.withholding_schedule
        if schedule is not None and schedule.year != tax_year:
            msg = (
                f"withholding_schedule.year ({schedule.year}) "
                f"does not match tax year ({tax_year})"
            )
            raise InvalidInputError(msg, feature="tax_year")

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
            ("ceiling_status", self.ceiling_status, ContributionCeilingStatus, False),
            ("events", self.events, (tuple, list), False),
            ("weekly_hours", self.weekly_hours, WeeklyHours, True),
            ("contributable_hours", self.contributable_hours, ContributableHours, True),
            ("full_time_weekly_hours", self.full_time_weekly_hours, WeeklyHours, True),
            ("employment_period", self.employment_period, EmploymentPeriod, True),
            ("seniority_months", self.seniority_months, SeniorityMonths, True),
            ("sector", self.sector, EmploymentSector, True),
            ("prior_year", self.prior_year, PriorYearTaxFacts, False),
        )


@dataclass(frozen=True)
class PeriodResult:
    """Result of one period-first payroll calculation.

    Attributes:
        period_id: The competence period, identical to the request.
        payment_date: Payment date, identical to the request.
        period_gross: Contractual gross entitlement for this period
            (sum of CASH_EARNINGS ledger entries). This is the theoretical
            wage the worker is entitled to before absence deductions.
        period_net: Net pay for this period only.
        period_employer_cost: Total employer cost net of unpaid absences:
            ``period_gross - unpaid_absence_deduction + employer_contributions
            + bilateral_fund_employer + tfr_accrual + non_cash_benefits``.
        unpaid_absence_deduction: Sum of EMPLOYEE_DEDUCTIONS ledger entries.
            Represents wages not paid due to unpaid absences or sickness.
            Zero when no absences are present.
        closing_state: State after closing this period: the tax year state
            and the obligations.  Pass as ``opening_state`` to the next
            run of the same tax year, or to
            :func:`~ccnl_engine.payroll.application.close_tax_year\
.close_tax_year` after the last run of the year.
        pay_items: All pay items produced for this period.
        ledger_entries: All ledger entries posted for this period.
        contribution_breakdown: Per-component INPS breakdown for audit
            and compliance tracing.
        benefit_breakdown: Per-axis fringe/welfare benefit breakdown for
            audit and cost-centre reporting.
        issues: Conditions that lower the reliability of this result, in
            the order they were raised.  Empty when every capability
            decided from known rules and facts.
        decisions: What the capabilities that record a decision decided in
            this run, e.g. the eligibility of a pay item for a preferential
            tax regime, in the order they were taken.
    """

    period_id: PeriodId
    payment_date: date
    period_gross: Decimal
    period_net: Decimal
    period_employer_cost: Decimal
    closing_state: PeriodState
    pay_items: tuple[PayItem, ...]
    ledger_entries: tuple[LedgerEntry, ...]
    capability_report: CapabilityReport
    contribution_breakdown: ContributionBreakdown
    tax_computation: TaxComputation
    benefit_breakdown: BenefitBreakdown
    run: PayrollRun | None = None
    unpaid_absence_deduction: Decimal = Decimal(0)
    bundle_version: str | None = None
    issues: tuple[CalculationIssue, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()

    @property
    def status(self) -> CalculationStatus:
        """Worst status implied by :attr:`issues`; final when there are none."""
        return CalculationStatus.worst(issue.status for issue in self.issues)
