"""Public input of every payroll run of a tax year."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
from ccnl_engine.payroll.domain.employer import EmployerProfile
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.inputs import PeriodFacts
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId, RunKind
from ccnl_engine.payroll.domain.tax_year import DEFAULT_PAYMENT_DAY
from ccnl_engine.shared.domain.collection_validation import items_of_type, mapping_of
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import reject, require_instances, require_int

__all__ = ["YearInput"]

_FEATURE = "year_input"


def _any_key(value: object, _path: str) -> object:
    return value


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
        require_int(
            self.year, "YearInput.year", feature=_FEATURE, minimum=1970, maximum=9999
        )
        require_instances(
            "YearInput",
            (
                ("employment", self.employment, Employment, False),
                ("employer", self.employer, EmployerProfile, False),
                ("prior_year", self.prior_year, PriorYearTaxFacts, False),
                ("default_facts", self.default_facts, PeriodFacts, False),
                ("calendar_override", self.calendar_override, CalendarOverride, True),
                ("opening_state", self.opening_state, PeriodState, True),
            ),
            feature=_FEATURE,
        )
        require_int(
            self.payment_day,
            "YearInput.payment_day",
            feature=_FEATURE,
            minimum=1,
            maximum=28,
        )
        if self.default_facts.events:
            msg = (
                "default_facts must carry no event: it applies to every run "
                "without an entry in periods; put events in periods"
            )
            raise InvalidInputError(
                msg, field="YearInput.default_facts", feature=_FEATURE
            )
        object.__setattr__(self, "_facts_by_run", self._normalized_periods())
        period = self.employment.employment_period
        if period is None or period.started_on.year < self.year:
            self.employment.check_seniority_in(self.year, 1)
        elif period.started_on.year == self.year:
            self.employment.check_seniority_in(self.year, period.started_on.month)

    def _normalized_periods(self) -> dict[str, PeriodFacts]:
        """Return :attr:`periods` keyed by run id.

        Returns:
            One entry per run, keyed by its run id.

        Raises:
            InvalidInputError: When :attr:`periods` is not a mapping, a key
                is not a month or a run id of :attr:`year`, two keys name
                the same run, or a value is not a :class:`PeriodFacts`.
        """
        facts = items_of_type(PeriodFacts, feature=_FEATURE)
        entries = mapping_of(
            self.periods, "YearInput.periods", _any_key, facts, feature=_FEATURE
        )
        normalized: dict[str, PeriodFacts] = {}
        for key, value in entries.items():
            run_id = self._run_id(key)
            if run_id in normalized:
                msg = (
                    f"periods names run {run_id!r} twice (by month and by run "
                    "id); supply its facts once"
                )
                raise InvalidInputError(
                    msg, field=f"YearInput.periods[{key!r}]", feature=_FEATURE
                )
            normalized[run_id] = value
        return normalized

    def _run_id(self, key: object) -> str:
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
                f"YearInput.periods[{key!r}]",
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

    @property
    def facts_by_run(self) -> Mapping[str, PeriodFacts]:
        """Entries of :attr:`periods` keyed by run id, e.g. ``"2026-03-regular"``."""
        return MappingProxyType(self._facts_by_run)
