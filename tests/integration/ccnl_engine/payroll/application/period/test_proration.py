"""The partial-month rule a run reads from the bundled CCNL data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.contract.domain.absence import DailyDivisorMethod
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.application.period._proration import (
    FULL_MONTH,
    PRORATED,
    RULE_MISSING,
    run_proration,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.types import MonthlyPayChain

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

_FEDERMECCANICA = "metalmeccanico-federmeccanica.json"
_VETRO = "vetro-meccanizzato-assovetro.json"
_SANITA = "dirigenza-sanitaria-area-sanita-aran.json"
_CHAIN = MonthlyPayChain(
    base=Decimal("2158.26"), seniority=Decimal("0.00"), allowances=()
)


def _request(
    started_on: date, year: int = 2026, month: int = 3
) -> PeriodCalculationRequest:
    """Return the fields of a request the proration reads.

    Returns:
        A request of ``year``-``month`` for an employment from ``started_on``.
    """
    fake = SimpleNamespace(
        employment_period=EmploymentPeriod(started_on=started_on),
        period_id=SimpleNamespace(year=year, month=month),
    )
    return cast("PeriodCalculationRequest", fake)


def test_full_month_keeps_the_monthly_pay() -> None:
    """A month employed from its first day is not prorated."""
    proration = run_proration(
        _request(date(2026, 3, 1)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration is FULL_MONTH
    assert proration.reason is None
    assert proration.inputs() == {}
    assert proration.issue() is None
    assert proration.apply(_CHAIN) is _CHAIN


@pytest.mark.parametrize(
    "kind", [RunKind.THIRTEENTH, RunKind.TERMINATION, RunKind.ADJUSTMENT]
)
def test_only_the_regular_run_is_prorated(kind: RunKind) -> None:
    """An extra-month, termination or adjustment run keeps its own rule."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_FEDERMECCANICA), kind
    )

    assert proration is FULL_MONTH


def test_untracked_employment_is_a_full_month() -> None:
    """Without an employment period every month is a full month."""
    fake = SimpleNamespace(
        employment_period=None, period_id=SimpleNamespace(year=2026, month=3)
    )
    proration = run_proration(
        cast("PeriodCalculationRequest", fake),
        load_ccnl(_FEDERMECCANICA),
        RunKind.REGULAR,
    )

    assert proration is FULL_MONTH


def test_federmeccanica_reads_its_absence_rule() -> None:
    """Hired 15 March 2026: 14 twenty-sixths of 2,158.26 is 1,162.14."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration.reason == PRORATED
    assert [rule for rule, _ in proration.rules] == [
        "ccnl/metalmeccanico-federmeccanica:work_rules.absence_rules"
    ]
    assert proration.source is not None
    assert proration.inputs() == {
        "employed_from": "2026-03-15",
        "employed_until": "2026-03-31",
        "divisor_method": "by_26",
        "payable_days": "14",
        "divisor": Decimal(26),
    }
    assert proration.apply(_CHAIN).base == Decimal("1162.14")


def test_span_worth_a_month_keeps_the_monthly_pay() -> None:
    """Hired Monday 2 March 2026: 26 payable days, the full monthly pay."""
    proration = run_proration(
        _request(date(2026, 3, 2)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration.reason == PRORATED
    assert proration.apply(_CHAIN) is _CHAIN


def test_ccnl_without_rule_pays_nothing_and_raises_an_issue() -> None:
    """The vetro CCNL records no daily divisor: the month is undetermined."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_VETRO), RunKind.REGULAR
    )
    issue = proration.issue()

    assert proration.reason == RULE_MISSING
    assert proration.rules == ()
    assert proration.apply(_CHAIN).base == Decimal("0.00")
    assert proration.inputs()["payable_days"] == "none"
    assert issue is not None
    assert issue.code == RULE_MISSING
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.fact is None


def test_hourly_rule_reads_the_hourly_divisor() -> None:
    """16-30 April 2026: 11 weekdays of 7.6 hours over 165 monthly hours."""
    proration = run_proration(
        _request(date(2026, 4, 16), month=4), load_ccnl(_SANITA), RunKind.REGULAR
    )

    assert proration.proration is not None
    assert proration.proration.method is DailyDivisorMethod.BY_HOURLY
    assert proration.proration.units == Decimal("83.6")
    assert [rule for rule, _ in proration.rules] == [
        "ccnl/dirigenza-sanitaria-area-sanita-aran:work_rules.absence_rules",
        "ccnl/dirigenza-sanitaria-area-sanita-aran:hourly_divisor[2019-12-19]",
    ]


def test_hourly_rule_before_the_divisor_series_is_missing() -> None:
    """The hourly divisor starts on 19 December 2019: no quota before it."""
    proration = run_proration(
        _request(date(2019, 6, 16), year=2019, month=6),
        load_ccnl(_SANITA),
        RunKind.REGULAR,
    )

    assert proration.reason == RULE_MISSING
    assert proration.rules[-1] == (
        "ccnl/dirigenza-sanitaria-area-sanita-aran:hourly_divisor",
        None,
    )
