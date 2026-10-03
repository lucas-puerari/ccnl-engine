"""The public error contract: bad input fails early, nothing leaks untyped.

An integration catches :class:`~ccnl_engine.CcnlEngineError`.  Input the
engine cannot use must be rejected when it is built, with
:class:`~ccnl_engine.InvalidInputError`; a calculation either returns a
result or raises a typed engine error, never a bare ``ValueError`` or
``AttributeError``; a feature the catalog declares computed must not be
refused as out of scope.
"""

from __future__ import annotations

import contextlib
from datetime import date

import pytest

from ccnl_engine import (
    CcnlEngineError,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    OutOfScopeError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    SeniorityFact,
    SenioritySource,
)
from tests.fixtures.sickness_episode import march_sickness_episode

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _regular(
    employment: Employment, month: int, facts: PeriodFacts | None = None
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=facts or PeriodFacts(),
        )
    )


@pytest.mark.xfail(
    strict=True,
    raises=ValueError,
    reason="a rule series not yet valid escapes as a bare ValueError",
)
@pytest.mark.parametrize(
    "seniority",
    [None, SeniorityFact(0, date(2026, 6, 1), SenioritySource.PAYSLIP)],
    ids=["seniority_not_given", "zero_seniority"],
)
def test_rule_series_not_yet_valid_is_a_typed_error(
    seniority: SeniorityFact | None,
) -> None:
    """Grafica editoria AIEG, level E, June 2026.

    The base pay of June exists; the seniority amount series starts on
    1 July 2026.  Today the run reads the series before multiplying by the
    increment count and raises ``ValueError: no value for 2026-06-01``,
    even with zero increments due.
    """
    employment = Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="E",
        seniority=seniority,
    )

    with contextlib.suppress(CcnlEngineError):  # A typed error is the contract.
        _regular(employment, month=6)


@pytest.mark.xfail(
    strict=True,
    raises=pytest.fail.Exception,
    reason="period facts accept events that are not work events",
)
def test_period_facts_reject_an_event_that_is_not_a_work_event() -> None:
    """Today the facts are built and the run fails with ``AttributeError``."""
    with pytest.raises(InvalidInputError):
        PeriodFacts(events=(object(),))  # type: ignore[arg-type]


@pytest.mark.xfail(
    strict=True,
    raises=pytest.fail.Exception,
    reason="employment accepts role codes that are not strings",
)
def test_employment_rejects_a_role_that_is_not_a_string() -> None:
    """Today the role is accepted, ignored, and the result is ``final``."""
    with pytest.raises(InvalidInputError):
        Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            roles=frozenset({1}),  # type: ignore[arg-type]
        )


@pytest.mark.xfail(
    strict=True,
    raises=OutOfScopeError,
    reason="sickness with earlier sick days in the year is refused as out of scope",
)
def test_sickness_after_earlier_sick_days_is_computed() -> None:
    """The catalog declares sickness computed.

    An episode after ten sick days in the year needs the cumulative INPS
    and CCNL tiers.  Today building the episode raises ``OutOfScopeError``
    with reason ``cumulative_tiers_not_implemented`` and asks the caller to
    compute the tier.
    """
    episode = march_sickness_episode(cumulative_sick_days_ytd=10)

    result = _regular(
        Employment(ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"),
        month=3,
        facts=PeriodFacts(events=(episode,)),
    )

    assert result.period_gross > 0
