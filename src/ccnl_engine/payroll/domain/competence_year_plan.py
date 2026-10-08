"""Public input of the runs of one competence year and their payment dates."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from types import MappingProxyType

from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
from ccnl_engine.payroll.domain.current_year import CurrentYearTaxFacts
from ccnl_engine.payroll.domain.employer import EmployerProfile
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.inputs import PeriodFacts
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId, RunKind
from ccnl_engine.payroll.domain.tax_year import (
    DEFAULT_PAYMENT_DAY,
    LAST_PAYMENT_DAY,
    monthly_payment_date,
)
from ccnl_engine.shared.domain.collection_validation import (
    Item,
    items_of_type,
    mapping_of,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    reject,
    require_instances,
    require_int,
)

__all__ = ["CompetenceYearPlan"]

_FEATURE = "competence_year_plan"
_OWNER = "CompetenceYearPlan"

type RunKeyed[V] = Mapping[int, V] | Mapping[str, V] | Mapping[int | str, V]


def _any_key(value: object, _path: str) -> object:
    return value


def _a_date(value: object, path: str) -> date:
    if isinstance(value, datetime) or not isinstance(value, date):
        reject(path, "a date (not a datetime)", value, feature=_FEATURE)
    return value


@dataclass(frozen=True)
class CompetenceYearPlan:
    """The runs of one competence year, their facts and when each is paid.

    The runs follow from the calendar and the employment period: the twelve
    months and the extra months of :attr:`year`.  Each run takes its
    :class:`PeriodFacts` from :attr:`periods` and, when it has no entry,
    from :attr:`default_facts`.  Each run is paid on :attr:`payment_day` of
    its own month unless :attr:`payment_dates` says otherwise; the payment
    date sets the tax year of the run (TUIR art. 51 c. 1), so December paid
    on 13 January of the next year is income of the next tax year.

    Attributes:
        year: The competence year of the runs.
        employment: Contract, level and worker facts.
        employer: The employer.  Required: its headcount selects the INPS
            rate tier.
        prior_year: Prior-year income and waivers.  Defaults to unknown
            income and no waiver.
        current_year: Income beyond this employment of the tax year of the
            runs, read by the family deductions; runs paid in another tax
            year ignore it.  Its INPS base of other employments counts
            toward the massimale of the runs of the same competence year.
            ``None`` means not known.
        periods: Facts per run, keyed by run id (``"2026-12-thirteenth"``,
            any run kind) or by month number (1-12, the regular run of the
            month).  :attr:`facts_by_run` holds them keyed by run id.  An
            entry replaces :attr:`default_facts` for its run: repeat the
            jurisdiction and family in it, e.g. with
            ``dataclasses.replace(default_facts, events=...)``.
        default_facts: Facts of every run without an entry in
            :attr:`periods`, extra-month runs included.  Must carry no event.
        calendar_override: A calendar that replaces the CCNL standard one,
            with its reason.  ``None`` runs the standard calendar.  An
            override that drops or lowers an extra month the CCNL grants, or
            does not match its reason, raises when the year is calculated.
        payment_day: Day of the run month on which a run is paid, 1-28,
            unless :attr:`payment_dates` names its date or the CCNL fixes
            the day of its quattordicesima (Commercio: 1 July) and the plan
            has no :attr:`calendar_override`.
        payment_dates: Payment date per run, keyed like :attr:`periods`:
            ``{12: date(2027, 1, 13)}`` pays the December salary on 13
            January 2027; an employer that pays in arrears names every
            month.  A date before the first day of the run month is
            rejected.
        opening_state: State the first run opens with, read by
            ``calculate_competence_year``.  ``None`` is the zero state, the
            fact only for an employment whose stated start falls in
            :attr:`year`; otherwise the runs have a ``missing_fact
            opening_state`` blocker.  Pass ``close_tax_year()`` of the
            previous tax year, imported balances,
            or the ``next_opening_state`` of the previous competence year
            when its December was paid in this tax year.  A state that
            already closed some runs of :attr:`year` with the same payment
            resumes after them.  Leave it ``None`` in a ``TaxYearPlan``,
            which carries its own.

    Raises:
        InvalidInputError: When a field is not of its type, a key of
            :attr:`periods` or :attr:`payment_dates` is not a month or a
            run id of :attr:`year`, two keys name the same run,
            :attr:`default_facts` carries events, a payment date precedes
            its run month, or ``payment_day`` is outside 1-28.
    """

    year: int
    employment: Employment
    employer: EmployerProfile
    prior_year: PriorYearTaxFacts = field(default_factory=PriorYearTaxFacts)
    current_year: CurrentYearTaxFacts | None = None
    periods: RunKeyed[PeriodFacts] = field(default_factory=dict)
    default_facts: PeriodFacts = field(default_factory=PeriodFacts)
    calendar_override: CalendarOverride | None = None
    payment_day: int = DEFAULT_PAYMENT_DAY
    payment_dates: RunKeyed[date] = field(default_factory=dict)
    opening_state: PeriodState | None = None
    _facts_by_run: dict[str, PeriodFacts] = field(
        init=False, repr=False, compare=False, default_factory=dict
    )
    _dates_by_run: dict[str, date] = field(
        init=False, repr=False, compare=False, default_factory=dict
    )

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.year, f"{_OWNER}.year", feature=_FEATURE, minimum=1970, maximum=9998
        )
        require_instances(
            _OWNER,
            (
                ("employment", self.employment, Employment, False),
                ("employer", self.employer, EmployerProfile, False),
                ("prior_year", self.prior_year, PriorYearTaxFacts, False),
                ("current_year", self.current_year, CurrentYearTaxFacts, True),
                ("default_facts", self.default_facts, PeriodFacts, False),
                ("calendar_override", self.calendar_override, CalendarOverride, True),
                ("opening_state", self.opening_state, PeriodState, True),
            ),
            feature=_FEATURE,
        )
        require_int(
            self.payment_day,
            f"{_OWNER}.payment_day",
            feature=_FEATURE,
            minimum=1,
            maximum=LAST_PAYMENT_DAY,
        )
        if self.default_facts.events:
            msg = (
                "default_facts must carry no event: it applies to every run "
                "without an entry in periods; put events in periods"
            )
            raise InvalidInputError(
                msg, field=f"{_OWNER}.default_facts", feature=_FEATURE
            )
        for name in ("periods", "payment_dates"):
            value = getattr(self, name)
            if isinstance(value, Mapping):
                object.__setattr__(self, name, dict(value))
        facts = items_of_type(PeriodFacts, feature=_FEATURE)
        object.__setattr__(
            self, "_facts_by_run", self._by_run(self.periods, "periods", facts)
        )
        dates = self._by_run(self.payment_dates, "payment_dates", _a_date)
        for run_id, paid_on in dates.items():
            PaymentId(PayrollRunId.parse(run_id), paid_on)
        object.__setattr__(self, "_dates_by_run", dates)
        period = self.employment.employment_period
        if period is None or period.started_on.year < self.year:
            self.employment.check_seniority_in(self.year, 1)
        elif period.started_on.year == self.year:
            self.employment.check_seniority_in(self.year, period.started_on.month)

    def _by_run[V](self, entries: object, name: str, item: Item[V]) -> dict[str, V]:
        """Return ``entries`` keyed by run id.

        Returns:
            One entry per run, keyed by its run id.

        Raises:
            InvalidInputError: When ``entries`` is not a mapping, a key is
                not a month or a run id of :attr:`year`, two keys name the
                same run, or a value is rejected by ``item``.
        """
        path = f"{_OWNER}.{name}"
        validated = mapping_of(entries, path, _any_key, item, feature=_FEATURE)
        normalized: dict[str, V] = {}
        for key, value in validated.items():
            run_id = self._run_id(key, f"{path}[{key!r}]")
            if run_id in normalized:
                msg = (
                    f"{name} names run {run_id!r} twice (by month and by run "
                    "id); supply it once"
                )
                raise InvalidInputError(msg, field=f"{path}[{key!r}]", feature=_FEATURE)
            normalized[run_id] = value
        return normalized

    def _run_id(self, key: object, path: str) -> str:
        """Return the run id a key of :attr:`periods` names.

        A key that is neither a month 1-12 nor a run id of :attr:`year` is
        rejected with ``InvalidInputError``.

        Returns:
            The run id: the regular run of a month number, or the key itself.
        """
        if isinstance(key, int) and not isinstance(key, bool) and 1 <= key <= 12:
            return str(PayrollRunId(year=self.year, month=key, kind=RunKind.REGULAR))
        try:
            run_id = PayrollRunId.parse(key) if isinstance(key, str) else None
        except InvalidInputError:
            run_id = None
        if run_id is None or run_id.year != self.year:
            reject(
                path,
                f"keyed by a month 1-12 or a run id of {self.year} such as "
                f"'{self.year}-12-thirteenth'",
                key,
                feature=_FEATURE,
            )
        return str(run_id)

    def facts_for(self, run: PayrollRun) -> PeriodFacts:
        """Return the facts of ``run``.

        Returns:
            The entry of :attr:`periods` for the run, else
            :attr:`default_facts`.
        """
        return self._facts_by_run.get(run.run_id, self.default_facts)

    def payment_for(self, run: PayrollRun) -> PaymentId:
        """Return the payment of ``run``: the run and the day it is paid.

        Returns:
            The entry of :attr:`payment_dates` for the run, else
            :attr:`payment_day` of the run month.
        """
        paid_on = self._dates_by_run.get(run.run_id)
        if paid_on is None:
            paid_on = monthly_payment_date(run.year, run.month, self.payment_day)
        return PaymentId(run.identifier, paid_on)

    @property
    def facts_by_run(self) -> Mapping[str, PeriodFacts]:
        """Entries of :attr:`periods` keyed by run id, e.g. ``"2026-03-regular"``."""
        return MappingProxyType(self._facts_by_run)

    @property
    def dated_runs(self) -> frozenset[str]:
        """Run ids :attr:`payment_dates` names."""
        return frozenset(self._dates_by_run)
