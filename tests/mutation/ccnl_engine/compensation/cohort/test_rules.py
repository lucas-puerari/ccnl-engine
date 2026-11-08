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

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.cohort.models import ClassTable, SalaryClass
from ccnl_engine.compensation.cohort.rules import hire_date, with_hire_cohort
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource

_CCNL = load_ccnl("consorzi-di-bonifica-snebi")
_JANUARY = date(2026, 1, 1)
_PERIOD = PeriodId(year=2026, month=1)


def _d100(hired_on: date | None) -> Decimal:
    period = None if hired_on is None else EmploymentPeriod(hired_on, None)
    ccnl = with_hire_cohort(_CCNL, period, None, _PERIOD)
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
    period = EmploymentPeriod(date(1990, 1, 1), None)
    assert with_hire_cohort(ccnl, period, None, _PERIOD) is ccnl


def test_the_hire_date_is_stated_or_taken_from_the_seniority() -> None:
    """The employment period first, else the months before the as_of."""
    period = EmploymentPeriod(date(1999, 5, 10), None)
    seniority = SeniorityFact(320, _JANUARY, SenioritySource.PAYSLIP)
    assert hire_date(period, seniority) == date(1999, 5, 10)
    assert hire_date(None, seniority) == date(1999, 5, 1)
    assert hire_date(None, None) is None


_ANIA = load_ccnl("assicurazioni-ania")


def _ania(hired_on: date, months: int | None) -> tuple[Decimal, int]:
    seniority = (
        None
        if months is None
        else SeniorityFact(months, _JANUARY, SenioritySource.PAYSLIP)
    )
    ccnl = with_hire_cohort(_ANIA, EmploymentPeriod(hired_on, None), seniority, _PERIOD)
    increments = ccnl.parameters.seniority_increments.maximum_count
    return ccnl.level_by_code("L7").base_salary.value_at(_JANUARY), increments


@pytest.mark.parametrize(
    ("hired_on", "months", "salary"),
    [
        (date(1995, 3, 1), 150, "3470.72"),  # 2/A cl 7 (13-14-15 years)
        (date(1999, 12, 17), 72, "3183.15"),  # 2/A cl 4 (7-8 years)
        (date(2010, 1, 1), 190, "3287.62"),  # 2/B cl 5 (14-15-16 years)
        (date(2020, 1, 1), 70, "3001.64"),  # 2/B cl 2 (5-6-7 years)
        (date(2024, 1, 1), 24, "2906.31"),  # 2/B cl 1 (1-2-3-4 years)
    ],
)
def test_ania_pays_the_class_of_the_cohort(
    hired_on: date, months: int, salary: str
) -> None:
    """Allegato 2/A to the staff in service on 18/12/1999, 2/B after (2026)."""
    assert _ania(hired_on, months) == (Decimal(salary), 0)


def test_ania_without_the_seniority_keeps_the_level_table() -> None:
    """No service months: the level's own table and increments."""
    salary, increments = _ania(date(2010, 1, 1), None)
    assert salary == Decimal("2906.31")
    assert increments == _ANIA.parameters.seniority_increments.maximum_count


def test_a_class_table_starts_at_zero_and_rises() -> None:
    """The classes are ordered from no service on."""
    series = TimeSeries(
        periods=(
            ValidityPeriod(valid_from=_JANUARY, valid_until=None, value=Decimal(1)),
        )
    )
    with pytest.raises(ValueError, match="must start at 0"):
        ClassTable(classes=(SalaryClass(months_from=12, base_salary=series),))
