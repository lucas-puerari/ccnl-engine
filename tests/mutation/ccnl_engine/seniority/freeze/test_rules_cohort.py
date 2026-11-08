"""CED art. 166: increments only for the staff in service on 31 December 2018.

Stesura of 9 March 2022, p. 106: "La normativa sulla maturazione degli
scatti di anzianità [...] continuerà viceversa ad essere applicata
esclusivamente per il personale in forza al 31-12-2018"; five biennial
increments, 4th level 30 EUR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import (
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.seniority.freeze.rules import months_in_cohort
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.support import regular_period

_JANUARY = date(2026, 1, 1)


@pytest.mark.parametrize(
    ("months", "expected"),
    [(84, 84), (85, 85), (83, 0), (12, 0)],
)
def test_months_in_cohort(months: int, expected: int) -> None:
    """84 whole months separate 31 December 2018 from 1 January 2026."""
    assert months_in_cohort(months, date(2018, 12, 31), _JANUARY) == expected


@pytest.mark.parametrize(
    ("hired_on", "expected"),
    [(date(2018, 12, 31), 84), (date(2019, 1, 1), 0)],
)
def test_the_hire_date_decides_when_stated(hired_on: date, expected: int) -> None:
    """In service on 31 December 2018, or hired the day after."""
    assert months_in_cohort(84, date(2018, 12, 31), _JANUARY, hired_on) == expected


def test_no_cohort_keeps_the_months() -> None:
    """A CCNL without hired_until counts every month."""
    assert months_in_cohort(12, None, _JANUARY) == 12


def _seniority(months: int) -> Decimal:
    result = regular_period(
        employment=Employment(
            ccnl_id="ced-assoced",
            level_code="4",
            seniority=SeniorityFact(months, _JANUARY, SenioritySource.PAYSLIP),
            pension_fund=NoPensionFund(),
            contract_type=Permanent(),
        ),
        current_year=employment_only(),
    )
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


def test_staff_in_service_in_2018_keep_maturing() -> None:
    """100 months of service: four biennial increments of 30 EUR."""
    assert _seniority(100) == Decimal("120.00")


def test_staff_hired_after_2018_have_none() -> None:
    """72 months of service, hired in 2020: no increment."""
    assert _seniority(72) == 0
