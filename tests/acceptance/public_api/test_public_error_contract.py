"""The public error contract: bad input fails early, nothing leaks untyped.

An integration catches :class:`~ccnl_engine.CcnlEngineError`.  Input the
engine cannot use must be rejected when it is built, with
:class:`~ccnl_engine.InvalidInputError`; a calculation either returns a
result or raises a typed engine error, never a bare ``ValueError`` or
``AttributeError``; a feature the catalog declares computed must not be
refused as out of scope.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CcnlEngineError,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    MissingRuleError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import SeniorityFact, SenioritySource, WorkerCategory
from ccnl_engine.results import BlockerCode, CalculationDecision
from tests.fixtures.sickness_episode import metalmeccanico_c3, sickness_episode

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


def _grafica_e(month: int, months_of_service: int | None) -> Employment:
    """Grafica editoria AIEG, level E, seniority known on the run month.

    The base pay of every month of 2026 is in the bundle; the seniority
    amount series starts on 1 July 2026 and the months before are a gap
    the data declares ``missing``.

    Returns:
        The employment, with ``months_of_service`` as of the run month.
    """
    return Employment(
        ccnl_slug="grafica-editoria-aieg.json",
        level_code="E",
        seniority=(
            None
            if months_of_service is None
            else SeniorityFact(
                months_of_service, date(2026, month, 1), SenioritySource.PAYSLIP
            )
        ),
    )


def _seniority_decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = [d for d in result.decisions if d.capability == "seniority"]
    return decision


def test_rule_series_not_yet_valid_without_seniority_is_a_missing_fact() -> None:
    """Level E in June 2026, seniority not given.

    No increment is counted without the fact, so the missing amount series
    is never read: the run returns a result whose seniority is a missing
    fact, not payable.
    """
    result = _regular(_grafica_e(6, None), month=6)

    decision = _seniority_decision(result)
    assert decision.reason_code == "required_fact_missing"
    assert decision.amount is None
    assert (BlockerCode.MISSING_FACT, None, "seniority") in {
        (b.code, b.feature, b.detail) for b in result.blockers
    }
    assert result.is_payable is False


def test_rule_series_not_yet_valid_with_zero_increments_is_computed() -> None:
    """Level E in June 2026, no month of service: no increment is due.

    Zero increments pay zero whatever the amount of one increment, so the
    run does not read the series and confirms a zero seniority.
    """
    result = _regular(_grafica_e(6, 0), month=6)

    decision = _seniority_decision(result)
    assert decision.reason_code == "zero_confirmed"
    assert decision.amount == Decimal(0)


def test_increments_due_where_the_series_is_missing_raise_a_typed_error() -> None:
    """Level E in June 2026, ten years of service: five increments due.

    Their amount before July 2026 is not in the bundle: the run raises
    :class:`MissingRuleError` naming the CCNL, the feature, the date, the
    declared gap and the first date the amount is known.
    """
    with pytest.raises(MissingRuleError) as raised:
        _regular(_grafica_e(6, 120), month=6)

    error = raised.value
    assert isinstance(error, CcnlEngineError)
    assert error.code == "missing_rule"
    assert error.ruleset == "grafica-editoria-aieg"
    assert error.feature == "seniority"
    assert error.as_of == date(2026, 6, 1)
    assert error.gap_kind == "missing"
    assert error.remediation is not None
    assert "2026-07-01" in error.remediation


def test_increments_on_the_first_date_of_the_series_are_paid() -> None:
    """Level E in July 2026, ten years of service: five increments.

    Source: kitech.it, Grafici July 2026 breakdown, scatto of level E
    10.33 EUR, at most five biennial increments.  Ten years (120 months)
    mature 1 + (120 - 24) // 24 = 5 increments: 5 x 10.33 = 51.65 EUR.
    """
    result = _regular(_grafica_e(7, 120), month=7)

    decision = _seniority_decision(result)
    assert decision.reason_code == "increments_applied"
    assert decision.amount == Decimal("51.65")


def test_run_before_the_first_tranche_raises_a_typed_error() -> None:
    """ANAS, first level, January 2026.

    The bundle has the ANAS pay tables from 1 March 2026: a run of January
    has no base salary and raises :class:`MissingRuleError`, not a bare
    ``ValueError``.
    """
    employment = Employment(ccnl_slug="anas.json", level_code="C1", seniority=None)

    with pytest.raises(MissingRuleError) as raised:
        _regular(employment, month=1)

    error = raised.value
    assert error.ruleset == "anas"
    assert error.feature == "base_salary"
    assert error.as_of == date(2026, 1, 1)
    assert error.gap_kind is None
    assert error.remediation is not None
    assert "2026-03-01" in error.remediation


def test_period_facts_reject_an_event_that_is_not_a_work_event() -> None:
    """An object that is not a work event is rejected with its position."""
    with pytest.raises(InvalidInputError) as raised:
        PeriodFacts(events=(object(),))  # type: ignore[arg-type]

    assert raised.value.field == "PeriodFacts.events[0]"
    assert raised.value.remediation is not None


def test_employment_rejects_a_role_that_is_not_a_string() -> None:
    """A role code that is not a string is rejected, not ignored."""
    with pytest.raises(InvalidInputError) as raised:
        Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            roles=frozenset({1}),  # type: ignore[arg-type]
        )

    assert raised.value.field == "Employment.roles[1]"


def test_sickness_after_earlier_sick_days_is_computed() -> None:
    """The catalog declares sickness computed, after earlier sick days too.

    Metalmeccanico C3 operaio, 2158.26 EUR a month, daily quota by 26:
    83.01 EUR a day.  Ten sick days from Monday 2 February 2026 (eight of
    them Monday to Saturday); the March episode, Monday 9 to Friday 13, is a
    relapse of it, so its days are days 11 to 15 of one episode: no waiting
    period, INPS 50% (days 4-20), CCNL integration to 100%.

    By hand: five days 2158.26 * 5 / 26 = 415.05 deducted and paid back,
    INPS 415.05 * 0.50 = 207.525 -> 207.53, employer 415.05 - 207.53 =
    207.52.
    """
    employment = metalmeccanico_c3(WorkerCategory.OPERAIO)
    february = sickness_episode("2026-02-02", date(2026, 2, 2), date(2026, 2, 11))
    first = _regular(employment, 2, PeriodFacts(events=(february,)))
    relapse = sickness_episode(
        "2026-03-09", date(2026, 3, 9), date(2026, 3, 13), relapse_of="2026-02-02"
    )

    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=PeriodFacts(events=(relapse,)),
            opening_state=first.closing_state,
        )
    )

    amounts = {
        item.kind: item.amount for item in result.pay_items if "_evt" in item.item_id
    }
    assert amounts == {
        "absence_deduction": Decimal("415.05"),
        "sickness_inps_item": Decimal("207.53"),
        "sickness_item": Decimal("207.52"),
    }
    (decision,) = (d for d in result.decisions if d.capability == "sickness")
    assert decision.reason_code == "sickness_episode_paid"
