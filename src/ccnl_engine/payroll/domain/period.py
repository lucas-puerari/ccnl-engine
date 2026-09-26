"""Domain types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, final

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
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
from ccnl_engine.payroll.domain.tax_year import TaxYearPolicy
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.capability_catalog import CapabilityReport
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.run import PayrollRun
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax import TaxComputation

_ZERO = Decimal(0)


@final
@dataclass(frozen=True)
class PeriodState:
    """YTD state entering a period-first payroll calculation.

    Pass :meth:`zero` for January (no prior periods closed this tax year).

    Attributes:
        regular_periods_closed: Number of regular (``run_kind="regular"``)
            payroll periods already closed this tax year.  Not used for the
            extra-month ratei, which are counted from the employment dates
            (:class:`~ccnl_engine.payroll.domain.accrual.ExtraMonthAccrual`).
        tax_withholding_periods_closed: Number of periods that have consumed
            an IRPEF withholding slot (regular + thirteenth + fourteenth;
            not adjustment).  Used for the conguaglio divisor.
        closed_run_ids: Frozen set of ``run_id`` strings for every run
            already closed this tax year.  Prevents reprocessing the same
            run and enforces monotonic ordering.
        earnings: Running totals for earned income and INPS contribution
            bases (gross, taxable, INPS base, employee INPS).
        fringe: Running totals for fringe benefits and PdR (value, taxed
            base, PdR eligible amount).
        tax: Running totals for tax withheld this year (IRPEF, surtax).
        trattamento: YTD credit account for trattamento integrativo,
            including any active installment recovery plan.
        somma_esente: YTD credit account for the somma esente bonus
            (L. 207/2024).
        work_time_regime: YTD usage of the annual cap of the night, holiday
            and shift supplement substitute tax (L. 199/2025 art. 1
            cc. 10-11).
    """

    SCHEMA_VERSION: ClassVar[int] = 1

    tax_year: int | None = None
    regular_periods_closed: int = 0
    tax_withholding_periods_closed: int = 0
    closed_run_ids: frozenset[str] = field(default_factory=frozenset)
    earnings: EarningsYtd = field(default_factory=EarningsYtd)
    fringe: FringeYtd = field(default_factory=FringeYtd)
    tax: TaxYtd = field(default_factory=TaxYtd)
    trattamento: TrattamentoAccount = field(default_factory=TrattamentoAccount)
    somma_esente: SommaEsenteAccount = field(default_factory=SommaEsenteAccount)
    work_time_regime: RegimeCapAccount = field(default_factory=RegimeCapAccount)

    def __post_init__(self) -> None:
        """Validate structural invariants on construction.

        Raises:
            ValueError: When any field violates a range or ordering constraint.
        """
        if self.tax_year is not None and self.tax_year < 2020:
            msg = f"tax_year must be >= 2020; got {self.tax_year}"
            raise ValueError(msg)
        if self.regular_periods_closed < 0:
            msg = (
                f"regular_periods_closed must be >= 0; "
                f"got {self.regular_periods_closed}"
            )
            raise ValueError(msg)
        if self.regular_periods_closed > 12:
            msg = (
                f"regular_periods_closed must be <= 12; "
                f"got {self.regular_periods_closed}"
            )
            raise ValueError(msg)
        if self.tax_withholding_periods_closed < self.regular_periods_closed:
            msg = (
                f"tax_withholding_periods_closed "
                f"({self.tax_withholding_periods_closed}) "
                f"must be >= regular_periods_closed "
                f"({self.regular_periods_closed})"
            )
            raise ValueError(msg)
        if self.tax_withholding_periods_closed > 14:
            msg = (
                f"tax_withholding_periods_closed must be <= 14; "
                f"got {self.tax_withholding_periods_closed}"
            )
            raise ValueError(msg)

    @classmethod
    def zero(cls) -> PeriodState:
        """Return a zero-valued state for the first period of the year.

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
        opening_state: YTD state entering this period. Use
            :meth:`PeriodState.zero` for January.
        employer: The employer; its headcount resolves INPS rates (some
            rates differ by firm size).  Defaults to an employer with 50
            employees.
        ceiling_status: Whether the IVS massimale contribution ceiling
            applies to this worker.  Use :attr:`ContributionCeilingStatus.POST_1995`
            for post-1995 workers and :attr:`ContributionCeilingStatus.NOT_APPLICABLE`
            for pre-1996 enrollment.  ``UNKNOWN`` (the default) does not apply
            the ceiling to avoid over-deducting contributions.
        events: Variable work events (overtime, absences, bonuses, etc.)
            that occurred in this period. Defaults to no events.
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
            uses it to select the runs of the year; a single period
            calculation carries it without checking the run month.
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
    """

    period_id: PeriodId
    payment_date: date
    ccnl_slug: str
    level_code: str
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    employer: Employer = field(default_factory=Employer)
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
            InvalidInputError: When ``payment_date`` is before the start of
                the competence period, when ``opening_state.tax_year`` is not
                ``None`` and differs from the attributed tax year, or when
                ``withholding_schedule`` belongs to another tax year.
        """
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)
        competence = date(self.period_id.year, self.period_id.month, 1)
        tax_year = TaxYearPolicy().attribute(competence, self.payment_date).tax_year
        opening_year = self.opening_state.tax_year
        if opening_year is not None and opening_year != tax_year:
            msg = (
                f"run {self.period_id.year}-{self.period_id.month:02d} paid on "
                f"{self.payment_date.isoformat()} belongs to tax year {tax_year} "
                f"(TUIR art. 51 c. 1), but opening_state is for tax year "
                f"{opening_year}: pass PeriodState.zero() to start a new tax "
                "year; carrying year-to-date state across tax years is not "
                "supported"
            )
            raise InvalidInputError(msg, feature="tax_year")
        schedule = self.withholding_schedule
        if schedule is not None and schedule.year != tax_year:
            msg = (
                f"withholding_schedule.year ({schedule.year}) "
                f"does not match tax year ({tax_year})"
            )
            raise InvalidInputError(msg, feature="tax_year")


@dataclass(frozen=True)
class PeriodCalculationResult:
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
        closing_state: YTD state after closing this period. Pass as
            ``opening_state`` to the next period's request.
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
