"""Only public engine errors escape the :class:`~ccnl_engine.PayrollEngine`.

Whatever a caller passes, a facade method returns a result or raises a
:class:`~ccnl_engine.CcnlEngineError` exported at the root, whose ``code``
is one of the public codes.  A technical exception (``AttributeError``,
``TypeError``, ``KeyError``, a bare ``ValueError``, a ``decimal`` signal or
an internal series lookup error) never does.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import ccnl_engine
from ccnl_engine import (
    CcnlEngineError,
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    MissingRuleError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftWorkEvent,
    SickLeaveEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.inputs import (
    ContributableHours,
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_ENGINE = PayrollEngine.bundled()
_YEAR = 2026
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METAL = Employment(ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3")
_PUBLIC_CODES = {
    "unknown_ccnl",
    "unknown_level",
    "out_of_scope",
    "data_integrity",
    "invalid_input",
    "missing_required_fact",
    "unsupported_tax_year",
    "missing_rule",
}


def _public_outcome(call: Callable[[], object]) -> CcnlEngineError | None:
    """Run ``call``; return the public error it raised, if any.

    Any exception that is not an engine error propagates and fails the
    test; an engine error must be exported at the root with a public code.

    Returns:
        ``None`` for a result, the engine error otherwise.
    """
    error: CcnlEngineError | None = None
    try:
        call()
    except CcnlEngineError as raised:
        error = raised
    if error is not None:
        assert type(error).__name__ in ccnl_engine.__all__
        assert error.code in _PUBLIC_CODES
    return error


def _june(employment: Employment, facts: PeriodFacts) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(_YEAR, 6),
        payment_date=date(_YEAR, 6, 27),
        employment=employment,
        employer=_EMPLOYER,
        facts=facts,
    )


@pytest.mark.parametrize(
    "call",
    [
        _ENGINE.calculate_period,
        _ENGINE.calculate_competence_year,
        _ENGINE.close_tax_year,
        _ENGINE.inspect_ruleset,
        lambda v: PayrollEngine.bundled(mode=v),
    ],
    ids=["period", "year", "close", "inspect", "mode"],
)
@pytest.mark.parametrize("value", [None, 1, {"year": 2026}, object()], ids=repr)
def test_a_facade_argument_of_the_wrong_type_is_invalid_input(
    call: Callable[[object], object], value: object
) -> None:
    """A dict from a JSON payload, ``None`` or a number never reaches a run."""
    with pytest.raises(InvalidInputError) as raised:
        call(value)
    assert raised.value.field is not None


@pytest.mark.parametrize(
    ("slug", "level", "code"),
    [
        ("no-such-ccnl.json", "C3", "unknown_ccnl"),
        ("metalmeccanico-federmeccanica.json", "Z9", "unknown_level"),
    ],
)
def test_an_unknown_contract_is_a_public_error(
    slug: str, level: str, code: str
) -> None:
    """A slug or a level the bundle does not know is a typed error."""
    employment = Employment(ccnl_slug=slug, level_code=level)

    error = _public_outcome(
        lambda: _ENGINE.calculate_period(_june(employment, PeriodFacts()))
    )

    assert error is not None
    assert error.code == code


@pytest.mark.parametrize("slug", ["../ccnl.json", "Metal.json", "metal", "a/b.json"])
def test_a_slug_that_is_not_a_bundle_file_name_is_invalid_input(slug: str) -> None:
    """A path or another extension never reaches the bundle reader."""
    with pytest.raises(InvalidInputError) as raised:
        Employment(ccnl_slug=slug, level_code="C3")
    assert raised.value.field == "Employment.ccnl_slug"


class TestSeniorityOnTheInput:
    """A seniority that cannot be aged to the first run is rejected early."""

    _LATE = SeniorityFact(0, date(_YEAR, 9, 1), SenioritySource.EMPLOYMENT_CONTRACT)

    def test_period_input_rejects_service_starting_after_the_run(self) -> None:
        """Service recognised from September cannot pay a June run."""
        employment = Employment(
            ccnl_slug=_METAL.ccnl_slug, level_code="C3", seniority=self._LATE
        )
        with pytest.raises(InvalidInputError, match="starts after") as raised:
            _june(employment, PeriodFacts())
        assert raised.value.field == "Employment.seniority"

    @pytest.mark.parametrize(
        ("started_on", "rejected"),
        [
            (None, True),
            (date(_YEAR - 3, 2, 1), True),
            (date(_YEAR, 3, 1), True),
            (date(_YEAR, 10, 1), False),
            (date(_YEAR + 1, 1, 1), False),
        ],
        ids=["untracked", "earlier-year", "hired-before", "hired-after", "next-year"],
    )
    def test_year_input_checks_the_first_run_of_the_year(
        self, started_on: date | None, *, rejected: bool
    ) -> None:
        """The first run is in January, or in the hire month of the year."""
        employment = Employment(
            ccnl_slug=_METAL.ccnl_slug,
            level_code="C3",
            seniority=self._LATE,
            employment_period=EmploymentPeriod.from_dates(started_on, None),
        )
        if rejected:
            with pytest.raises(InvalidInputError, match="starts after"):
                CompetenceYearPlan(
                    year=_YEAR, employment=employment, employer=_EMPLOYER
                )
        else:
            assert CompetenceYearPlan(
                year=_YEAR, employment=employment, employer=_EMPLOYER
            )


class TestYearOfContractStartingDuringTheYear:
    """A year computes the runs the pay tables cover and lists the others.

    The ANAS pay tables of the CCNL 2025-2027 (signed 18 December 2025,
    https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/\
CCNL-2025-2027.pdf, "Tabella retributiva") start with the tranche of
    1 March 2026; the bundle holds no earlier table.
    """

    def test_the_summary_tells_when_the_tables_start(self) -> None:
        """The catalog predicts the first covered day before any run."""
        (anas,) = (c for c in _ENGINE.list_contracts() if c.ccnl_id == "anas")
        assert anas.validity is not None
        assert anas.validity.first_day == date(_YEAR, 3, 1)
        assert not anas.validity.covers(date(_YEAR, 2, 1))

    def test_a_year_from_january_is_partial_and_not_payable(self) -> None:
        """January and February are left out with a typed blocker each."""
        request = CompetenceYearPlan(
            year=_YEAR,
            employment=Employment(ccnl_slug="anas.json", level_code="C1"),
            employer=_EMPLOYER,
        )
        result = _ENGINE.calculate_competence_year(request)

        left_out = [str(u.payment.run_id) for u in result.uncovered_runs]
        assert left_out == ["2026-01-regular", "2026-02-regular"]
        errors = [u.error for u in result.uncovered_runs]
        assert all(isinstance(e, MissingRuleError) for e in errors)
        assert [e.as_of for e in errors] == [date(_YEAR, 1, 1), date(_YEAR, 2, 1)]
        assert {e.feature for e in errors} == {"base_salary"}
        assert result.period_results[0].period_id.month == 3
        assert not result.is_payable
        not_computed = [
            b.detail for b in result.blockers if b.code == "run_not_computed"
        ]
        assert not_computed == left_out
        assert [str(c) for c in result.conguagli] == ["2026-12-thirteenth@2026-12-28"]

    def test_a_year_with_no_run_in_force_raises(self) -> None:
        """Employed only in January and February: nothing to compute."""
        employment = Employment(
            ccnl_slug="anas.json",
            level_code="C1",
            employment_period=EmploymentPeriod(
                started_on=date(_YEAR, 1, 1), ended_on=date(_YEAR, 2, 28)
            ),
        )
        request = CompetenceYearPlan(
            year=_YEAR, employment=employment, employer=_EMPLOYER
        )
        with pytest.raises(MissingRuleError) as raised:
            _ENGINE.calculate_competence_year(request)
        assert raised.value.feature == "base_salary"
        assert raised.value.as_of == date(_YEAR, 1, 1)

    def test_a_year_hired_after_the_start_is_computed(self) -> None:
        """A worker hired in April runs on the ANAS tables of March."""
        employment = Employment(
            ccnl_slug="anas.json",
            level_code="C1",
            employment_period=EmploymentPeriod(started_on=date(_YEAR, 4, 1)),
        )
        result = _ENGINE.calculate_competence_year(
            CompetenceYearPlan(year=_YEAR, employment=employment, employer=_EMPLOYER)
        )
        assert result.period_results[0].period_id.month == 4


_AMOUNT = st.decimals(min_value=Decimal(0), max_value=Decimal(99_999), places=2)
_POSITIVE = st.decimals(min_value=Decimal("0.01"), max_value=Decimal(9_999), places=2)
_RATE = st.decimals(min_value=Decimal(0), max_value=Decimal(1), places=3)


def _events(month: int) -> st.SearchStrategy[list[object]]:
    """Return lists of up to five valid events dated in ``month``.

    Returns:
        The strategy.
    """
    day = st.dates(min_value=date(_YEAR, month, 1), max_value=date(_YEAR, month, 28))
    return st.lists(
        st.one_of(
            st.builds(
                OvertimeEvent,
                event_date=day,
                hours=_POSITIVE,
                hourly_rate=_POSITIVE,
                multiplier=st.one_of(st.none(), _POSITIVE),
                kind=st.sampled_from(list(OvertimeKind)),
            ),
            st.builds(NightShiftEvent, event_date=day, supplement_amount=_AMOUNT),
            st.builds(HolidayWorkEvent, event_date=day, supplement_amount=_AMOUNT),
            st.builds(ShiftWorkEvent, event_date=day, supplement_amount=_AMOUNT),
            st.builds(
                AbsenceEvent,
                event_date=day,
                hours=st.decimals(
                    min_value=Decimal(1), max_value=Decimal(24), places=1
                ),
                hourly_rate=_POSITIVE,
                suspends_accrual=st.booleans(),
            ),
            st.builds(
                SickLeaveEvent,
                event_date=day,
                amount=_AMOUNT,
                sick_days=st.integers(1, 30),
            ),
            st.builds(
                BonusEvent,
                event_date=day,
                amount=_AMOUNT,
                kind=st.sampled_from([
                    "bonus",
                    "productivity_bonus",
                    "contract_renewal",
                ]),
            ),
            st.builds(FringeEvent, event_date=day, amount=_AMOUNT),
            st.builds(WelfareEvent, event_date=day, amount=_AMOUNT),
            st.builds(
                ArrearsEvent, event_date=day, amount=_AMOUNT, separate_tax_rate=_RATE
            ),
            st.builds(
                BilateralFundEvent,
                event_date=day,
                employee_amount=_AMOUNT,
                employer_amount=_AMOUNT,
            ),
            st.builds(
                TerminationTFREvent,
                event_date=day,
                amount=_AMOUNT,
                separate_tax_rate=_RATE,
            ),
        ),
        max_size=5,
    )


_CONTRACTS = st.sampled_from([
    ("metalmeccanico-federmeccanica.json", "C3"),
    ("commercio-confcommercio.json", "4"),
    ("lavoro-domestico-non-convivente.json", "BS"),
])
_DEPENDENTS = st.lists(
    st.builds(
        Dependent,
        relationship=st.sampled_from([
            DependentRelationship.CHILD,
            DependentRelationship.ASCENDANT,
        ]),
        birth_date=st.dates(date(1940, 1, 1), date(2026, 12, 31)),
        own_income=st.none() | _AMOUNT,
        dependent_from=st.none() | st.dates(date(2025, 1, 1), date(2027, 12, 31)),
        dependent_until=st.none(),
    ),
    max_size=3,
)


def _employment(contract: tuple[str, str], weekly_hours: int | None) -> Employment:
    slug, level = contract
    hours = None if weekly_hours is None else WeeklyHours(weekly_hours)
    return Employment(ccnl_slug=slug, level_code=level, weekly_hours=hours)


@settings(max_examples=50, deadline=None)
@given(
    data=st.data(),
    month=st.integers(1, 12),
    paid_after=st.integers(0, 40),
    contract=_CONTRACTS,
    weekly_hours=st.one_of(st.none(), st.integers(1, 40)),
    hours=st.one_of(st.none(), _AMOUNT),
    dependents=_DEPENDENTS,
    income=st.one_of(st.none(), _AMOUNT),
)
def test_any_period_gives_a_result_or_a_public_error(
    data: st.DataObject,
    month: int,
    paid_after: int,
    contract: tuple[str, str],
    weekly_hours: int | None,
    hours: Decimal | None,
    dependents: list[Dependent],
    income: Decimal | None,
) -> None:
    """Any valid events, payment date, family and hours: nothing leaks."""
    events = data.draw(_events(month))
    facts = PeriodFacts(
        events=tuple(events),  # type: ignore[arg-type]
        contributable_hours=None if hours is None else ContributableHours(hours),
        family_composition=FamilyComposition(dependents=tuple(dependents)),
        regione="IT-45",
        comune_belfiore="F257",
    )
    request = PeriodInput(
        run=PayrollRun.regular(_YEAR, month),
        payment_date=date(_YEAR, month, 1) + timedelta(days=paid_after),
        employment=_employment(contract, weekly_hours),
        employer=_EMPLOYER,
        facts=facts,
        prior_year=PriorYearTaxFacts(employment_income=income),
    )
    _public_outcome(lambda: _ENGINE.calculate_period(request))


@settings(max_examples=8, deadline=None)
@given(
    data=st.data(),
    months=st.sets(st.integers(1, 12), max_size=3),
    contract=_CONTRACTS,
    weekly_hours=st.one_of(st.none(), st.integers(1, 40)),
)
def test_any_year_and_its_closing_give_a_result_or_a_public_error(
    data: st.DataObject,
    months: set[int],
    contract: tuple[str, str],
    weekly_hours: int | None,
) -> None:
    """A year with events in any month, then the opening of the next one."""
    periods = {month: data.draw(_events(month)) for month in sorted(months)}
    request = CompetenceYearPlan(
        year=_YEAR,
        employment=_employment(contract, weekly_hours),
        employer=_EMPLOYER,
        periods={
            month: PeriodFacts(events=tuple(events))  # type: ignore[arg-type]
            for month, events in periods.items()
        },
    )
    results: list[CompetenceYearResult] = []
    error = _public_outcome(
        lambda: results.append(_ENGINE.calculate_competence_year(request))
    )
    if error is None:
        closing = results[0].period_results[-1].closing_state
        _public_outcome(lambda: _ENGINE.close_tax_year(closing))
