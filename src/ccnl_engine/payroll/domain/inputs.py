"""Public inputs of a payroll calculation: one run or a whole year.

:class:`PeriodInput` describes one payroll run and :class:`YearInput` every
run of a tax year.  Both group the facts by owner: :class:`~ccnl_engine\
.payroll.domain.employment.Employment` for the contract and the worker,
:class:`~ccnl_engine.payroll.domain.employer.EmployerProfile` for the
employer, :class:`~ccnl_engine.payroll.domain.prior_year.PriorYearTaxFacts`
for what the tax regimes read once a year, and :class:`PeriodFacts` for what
holds in one run.  Every input is validated on construction.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
from ccnl_engine.payroll.domain.employer import EmployerProfile
from ccnl_engine.payroll.domain.employment import ContributableHours, Employment
from ccnl_engine.payroll.domain.family import FamilyComposition
from ccnl_engine.payroll.domain.jurisdiction import check_surtax_codes
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.request_checks import type_error
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId, RunKind
from ccnl_engine.payroll.domain.tax_year import (
    DEFAULT_PAYMENT_DAY,
    monthly_payment_date,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule

__all__ = ["PeriodFacts", "PeriodInput", "YearInput"]


def _raise_on(problem: str | None, feature: str) -> None:
    """Raise ``InvalidInputError`` for ``problem`` when there is one.

    Raises:
        InvalidInputError: When ``problem`` is not ``None``.
    """
    if problem is not None:
        raise InvalidInputError(problem, feature=feature)


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
        _raise_on(
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
            :meth:`~ccnl_engine.payroll.domain.period.PeriodState.zero` for
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
        _raise_on(
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


@dataclass(frozen=True)
class YearInput:
    """Input of every payroll run of a tax year.

    The runs follow from the calendar and the employment period.  Each run
    takes its :class:`PeriodFacts` from :attr:`periods` and, when it has no
    entry, from :attr:`default_facts`.

    Attributes:
        year: The tax year.  Every run is paid in it.
        employment: Contract, level and worker facts.
        employer: The employer.  Required: its headcount selects the INPS
            rate tier.
        prior_year: Prior-year income and waivers.  Defaults to unknown
            income and no waiver.
        periods: Facts per run, keyed by run id (``"2026-12-thirteenth"``,
            any run kind) or by month number (1-12, the regular run of the
            month).  :attr:`facts_by_run` holds them keyed by run id.  An
            entry replaces
            :attr:`default_facts` for its run: repeat the jurisdiction and
            family in it, e.g. with ``dataclasses.replace(default_facts,
            events=...)``.
        default_facts: Facts of every run without an entry in
            :attr:`periods`, extra-month runs included.  Must carry no event.
        calendar_override: A calendar that replaces the CCNL standard one,
            with its reason.  ``None`` runs the standard calendar.  An
            override that drops or lowers an extra month the CCNL grants, or
            does not match its reason, raises when the year is calculated.
        payment_day: Day of the run month on which every run is paid, 1-28.
        opening_state: State the first run opens with.  ``None`` starts a
            new employment; pass ``close_tax_year()`` of the last run of the
            previous year to carry its obligations.

    Raises:
        InvalidInputError: When a field is not of its type, a key of
            :attr:`periods` is not a month or a run id of :attr:`year`, two
            keys name the same run, :attr:`default_facts` carries events, or
            ``payment_day`` is outside 1-28.
    """

    year: int
    employment: Employment
    employer: EmployerProfile
    prior_year: PriorYearTaxFacts = field(default_factory=PriorYearTaxFacts)
    periods: (
        Mapping[int, PeriodFacts]
        | Mapping[str, PeriodFacts]
        | Mapping[int | str, PeriodFacts]
    ) = field(default_factory=dict)
    default_facts: PeriodFacts = field(default_factory=PeriodFacts)
    calendar_override: CalendarOverride | None = None
    payment_day: int = DEFAULT_PAYMENT_DAY
    opening_state: PeriodState | None = None
    _facts_by_run: dict[str, PeriodFacts] = field(
        init=False, repr=False, compare=False, default_factory=dict
    )

    def __post_init__(self) -> None:  # noqa: D105
        _raise_on(
            type_error((
                ("year", self.year, int, False),
                ("employment", self.employment, Employment, False),
                ("employer", self.employer, EmployerProfile, False),
                ("prior_year", self.prior_year, PriorYearTaxFacts, False),
                ("periods", self.periods, Mapping, False),
                ("default_facts", self.default_facts, PeriodFacts, False),
                ("calendar_override", self.calendar_override, CalendarOverride, True),
                ("payment_day", self.payment_day, int, False),
                ("opening_state", self.opening_state, PeriodState, True),
            )),
            "year_input",
        )
        monthly_payment_date(self.year, 1, self.payment_day)
        if self.default_facts.events:
            msg = (
                "default_facts must carry no event: it applies to every run "
                "without an entry in periods; put events in periods"
            )
            raise InvalidInputError(msg, feature="year_input")
        object.__setattr__(self, "_facts_by_run", self._normalized_periods())

    def _normalized_periods(self) -> dict[str, PeriodFacts]:
        """Return :attr:`periods` keyed by run id.

        Returns:
            One entry per run, keyed by its run id.

        Raises:
            InvalidInputError: When a key is not a month or a run id of
                :attr:`year`, two keys name the same run, or a value is not
                a :class:`PeriodFacts`.
        """
        normalized: dict[str, PeriodFacts] = {}
        for key, facts in dict(self.periods).items():
            run_id = self._run_id(key)
            _raise_on(
                type_error(((f"periods[{key!r}]", facts, PeriodFacts, False),)),
                "year_input",
            )
            if run_id in normalized:
                msg = (
                    f"periods names run {run_id!r} twice (by month and by run "
                    "id); supply its facts once"
                )
                raise InvalidInputError(msg, feature="year_input")
            normalized[run_id] = facts
        return normalized

    def _run_id(self, key: object) -> str:
        """Return the run id a key of :attr:`periods` names.

        Returns:
            The run id: the regular run of a month number, or the key itself.

        Raises:
            InvalidInputError: When ``key`` is neither a month 1-12 nor a
                run id of :attr:`year`.
        """
        if isinstance(key, int) and not isinstance(key, bool) and 1 <= key <= 12:
            return str(PayrollRunId(year=self.year, month=key, kind=RunKind.REGULAR))
        try:
            run_id = PayrollRunId.parse(key) if isinstance(key, str) else None
        except ValueError:
            run_id = None
        if run_id is None or run_id.year != self.year:
            msg = (
                f"periods keys must be a month 1-12 or a run id of {self.year} "
                f"such as '{self.year}-12-thirteenth'; got {key!r}"
            )
            raise InvalidInputError(msg, feature="year_input")
        return str(run_id)

    def facts_for(self, run: PayrollRun) -> PeriodFacts:
        """Return the facts of ``run``.

        Returns:
            The entry of :attr:`periods` for the run, else
            :attr:`default_facts`.
        """
        return self._facts_by_run.get(run.run_id, self.default_facts)

    @property
    def facts_by_run(self) -> Mapping[str, PeriodFacts]:
        """Entries of :attr:`periods` keyed by run id, e.g. ``"2026-03-regular"``."""
        return MappingProxyType(self._facts_by_run)
