"""A month of sick days against a fixed monthly pay: never a silent amount.

Sick days are deducted at the CCNL daily quota, the monthly pay is fixed.
Where the payable days of the month differ from the divisor no CCNL text in
the bundle says how the month is deducted, so the run raises an issue that
blocks payment:

- February 2026 holds 24 Mondays to Saturdays: sick all month, by 26 the
  run deducts 24/26 of the pay and leaves 2/26 for days nobody worked;
- by 30 day 31 counts as day 30: sick 1 to 30 March, or hired 16 March and
  sick 16 to 30 March, the run deducts the whole pay posted and pays
  nothing for 31 March, a day worked.

An unpaid absence is deducted at the caller's hourly rate: beside sick days
it is an issue, on a sick day it is rejected, and when the two exceed the
pay the computation is out of scope.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
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
)
from ccnl_engine.events import AbsenceEvent, SicknessEpisode, WorkEvent
from ccnl_engine.inputs import EmploymentPeriod, WorkerCategory
from tests.fixtures.seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METALMECCANICO = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    category=WorkerCategory.OPERAIO,
    seniority=new_hire(),
)
_DIRIGENTE = Employment(
    ccnl_slug="dirigenza-funzioni-locali-aran.json", level_code="DIRIGENTE"
)
_MISMATCH = "sickness_month_quota_mismatch"


def _run(month: int, employment: Employment, *events: WorkEvent) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=PeriodFacts(events=events),
        )
    )


def _base_salary(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_a_whole_february_by_26_leaves_pay_and_blocks() -> None:
    """Sick 1 to 28 February: 24/26 of the pay deducted, an issue raised."""
    episode = SicknessEpisode("F", date(2026, 2, 1), date(2026, 2, 28))
    february = _run(2, _METALMECCANICO, episode)
    base = _base_salary(february)
    assert february.unpaid_absence_deduction == (base * 24 / 26).quantize(
        Decimal("0.01")
    )
    assert _MISMATCH in _codes(february)
    assert not february.is_payable


def test_day_31_worked_by_30_is_left_unpaid_and_blocks() -> None:
    """Sick 1 to 30 March by 30: the whole month deducted, an issue raised."""
    episode = SicknessEpisode("M", date(2026, 3, 1), date(2026, 3, 30))
    march = _run(3, _DIRIGENTE, episode)
    assert march.unpaid_absence_deduction == _base_salary(march)
    assert _MISMATCH in _codes(march)


def test_a_partial_month_by_30_leaves_day_31_unpaid_and_blocks() -> None:
    """Hired 16 March, sick 16 to 30 March: 15 of 15 units deducted.

    By 30 the employed days 16-31 March are days 16 to 30 of the commercial
    month, 15 units; so are the sick days 16-30 March.  31 March is worked
    and left unpaid.
    """
    hired = replace(_DIRIGENTE, employment_period=EmploymentPeriod(date(2026, 3, 16)))
    episode = SicknessEpisode("M", date(2026, 3, 16), date(2026, 3, 30))
    march = _run(3, hired, episode)
    assert march.unpaid_absence_deduction == _base_salary(march)
    assert _MISMATCH in _codes(march)


def test_a_whole_month_by_26_deducts_the_pay_without_issue() -> None:
    """Sick all of March: 26 Mondays to Saturdays, the whole pay."""
    episode = SicknessEpisode("M", date(2026, 3, 1), date(2026, 3, 31))
    march = _run(3, _METALMECCANICO, episode)
    assert march.unpaid_absence_deduction == _base_salary(march)
    assert _MISMATCH not in _codes(march)


_EPISODE = SicknessEpisode("M", date(2026, 3, 2), date(2026, 3, 6))


def test_an_unpaid_absence_beside_sick_days_blocks() -> None:
    """Sick 2 to 6 March, absent unpaid 8 hours on 10 March."""
    absence = AbsenceEvent(date(2026, 3, 10), Decimal(8), Decimal("12.47"))
    march = _run(3, _METALMECCANICO, _EPISODE, absence)
    assert "sickness_with_unpaid_absence" in _codes(march)
    assert not march.is_payable


def test_an_unpaid_absence_on_a_sick_day_is_rejected() -> None:
    """4 March is a day of the 2-6 March episode."""
    absence = AbsenceEvent(date(2026, 3, 4), Decimal(8), Decimal("12.47"))
    with pytest.raises(InvalidInputError, match="falls on days of sickness"):
        _run(3, _METALMECCANICO, _EPISODE, absence)


def test_sick_days_and_absences_over_the_pay_are_out_of_scope() -> None:
    """Sick 1 to 30 July (26 working days) and absent 8 hours on 31 July.

    The sick days deduct the whole pay; the absence at the caller's rate
    would deduct more than the month.
    """
    episode = SicknessEpisode("J", date(2026, 7, 1), date(2026, 7, 30))
    absence = AbsenceEvent(date(2026, 7, 31), Decimal(8), Decimal("12.75"))
    with pytest.raises(OutOfScopeError) as raised:
        _run(7, _METALMECCANICO, episode, absence)
    assert raised.value.reason == "sickness_with_unpaid_absence"
