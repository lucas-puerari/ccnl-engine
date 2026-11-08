"""Consorzi di bonifica, Allegato A: two tables by hire cohort.

PDF p. 157 "DIPENDENTI IN SERVIZIO AL 15 LUGLIO 2000", p. 159 "IN SERVIZIO
DAL 15 LUGLIO 2000"; Allegato Q (p. 230): the higher table is for those
"assunti a decorrere dal 15/7/2000".  Parameter 100 (D100) from 1 January
2026: 1,513.09 and 1,534.16.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.cohort.rules import hire_date, with_hire_cohort
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource

_CCNL = load_ccnl("consorzi-di-bonifica-snebi")
_JANUARY = date(2026, 1, 1)


def _d100(hired_on: date | None) -> Decimal:
    ccnl = with_hire_cohort(_CCNL, hired_on)
    return ccnl.level_by_code("D100").base_salary.value_at(_JANUARY)


@pytest.mark.parametrize(
    ("hired_on", "salary"),
    [
        (date(1995, 3, 1), "1513.09"),
        (date(2000, 7, 14), "1513.09"),
        (date(2000, 7, 15), "1534.16"),
        (date(2010, 1, 1), "1534.16"),
        (None, "1534.16"),
    ],
)
def test_the_hire_date_picks_the_table(hired_on: date | None, salary: str) -> None:
    """Hired by 14 July 2000: the lower table; from 15 July: the level's."""
    assert _d100(hired_on) == Decimal(salary)


def test_a_ccnl_without_cohorts_is_unchanged() -> None:
    """Commercio has one table."""
    ccnl = load_ccnl("commercio-confcommercio")
    assert with_hire_cohort(ccnl, date(1990, 1, 1)) is ccnl


def test_the_hire_date_is_stated_or_taken_from_the_seniority() -> None:
    """The employment period first, else the months before the as_of."""
    period = EmploymentPeriod(date(1999, 5, 10), None)
    seniority = SeniorityFact(320, _JANUARY, SenioritySource.PAYSLIP)
    assert hire_date(period, seniority) == date(1999, 5, 10)
    assert hire_date(None, seniority) == date(1999, 5, 1)
    assert hire_date(None, None) is None
