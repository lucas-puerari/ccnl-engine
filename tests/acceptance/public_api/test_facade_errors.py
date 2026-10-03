"""Only public engine errors escape the :class:`~ccnl_engine.PayrollEngine`.

Whatever a caller passes, a facade method returns a result or raises a
:class:`~ccnl_engine.CcnlEngineError` exported at the root, whose ``code``
is one of the public codes.  A technical exception (``AttributeError``,
``TypeError``, ``KeyError``, a bare ``ValueError``, a ``decimal`` signal or
an internal series lookup error) never does.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import ccnl_engine
from ccnl_engine import (
    AbsenceEvent,
    BonusEvent,
    CcnlEngineError,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    FringeEvent,
    Headcount,
    InvalidInputError,
    MissingRuleError,
    NightShiftEvent,
    OvertimeEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    SeniorityFact,
    SenioritySource,
    WelfareEvent,
    YearInput,
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
        _ENGINE.calculate_year,
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
                YearInput(year=_YEAR, employment=employment, employer=_EMPLOYER)
        else:
            assert YearInput(year=_YEAR, employment=employment, employer=_EMPLOYER)


class TestYearOfContractStartingDuringTheYear:
    """The first missing rule of the year is the pay of its first run."""

    def test_a_year_from_january_reports_the_missing_base_salary(self) -> None:
        """ANAS pay tables start on 1 March 2026: January has no base salary."""
        request = YearInput(
            year=_YEAR,
            employment=Employment(ccnl_slug="anas.json", level_code="C1"),
            employer=_EMPLOYER,
        )
        with pytest.raises(MissingRuleError) as raised:
            _ENGINE.calculate_year(request)
        assert raised.value.feature == "base_salary"
        assert raised.value.as_of == date(_YEAR, 1, 1)

    def test_a_year_hired_after_the_start_is_computed(self) -> None:
        """A worker hired in April runs on the ANAS tables of March."""
        employment = Employment(
            ccnl_slug="anas.json",
            level_code="C1",
            employment_period=EmploymentPeriod(started_on=date(_YEAR, 4, 1)),
        )
        result = _ENGINE.calculate_year(
            YearInput(year=_YEAR, employment=employment, employer=_EMPLOYER)
        )
        assert result.period_results[0].period_id.month == 4


_AMOUNTS = st.decimals(min_value=Decimal("0.01"), max_value=Decimal(10_000), places=2)
_EVENTS = st.lists(
    st.one_of(
        st.builds(
            OvertimeEvent,
            event_date=st.just(date(_YEAR, 6, 10)),
            hours=st.decimals(
                min_value=Decimal("0.5"), max_value=Decimal(80), places=1
            ),
            hourly_rate=_AMOUNTS,
        ),
        st.builds(
            NightShiftEvent,
            event_date=st.just(date(_YEAR, 6, 11)),
            supplement_amount=_AMOUNTS,
        ),
        st.builds(BonusEvent, event_date=st.just(date(_YEAR, 6, 12)), amount=_AMOUNTS),
        st.builds(FringeEvent, event_date=st.just(date(_YEAR, 6, 13)), amount=_AMOUNTS),
        st.builds(
            WelfareEvent, event_date=st.just(date(_YEAR, 6, 14)), amount=_AMOUNTS
        ),
        st.builds(
            AbsenceEvent,
            event_date=st.just(date(_YEAR, 6, 15)),
            hours=st.decimals(min_value=Decimal(1), max_value=Decimal(200), places=0),
            hourly_rate=_AMOUNTS,
        ),
    ),
    max_size=4,
)


@settings(max_examples=40, deadline=None)
@given(events=_EVENTS)
def test_any_valid_events_give_a_result_or_a_public_error(events: list[object]) -> None:
    """Large overtime, absences above the pay, bonuses: nothing leaks."""
    facts = PeriodFacts(events=tuple(events))  # type: ignore[arg-type]
    _public_outcome(lambda: _ENGINE.calculate_period(_june(_METAL, facts)))
