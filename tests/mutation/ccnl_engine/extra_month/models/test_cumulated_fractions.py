"""Cumulated fractions of month: CCNL Pubblici Esercizi art. 183 c. 2.

"le frazioni di mese saranno cumulate. La somma così ottenuta comporterà la
corresponsione di un rateo mensile per ogni trenta giorni di calendario,
nonché per la eventuale frazione residua pari o superiore a quindici giorni".

A whole month accrues a rateo; the days of the months worked in part are
summed.  Every count is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.compensation.models import AccrualComparison
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual, MonthAccrualRule
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule

_TREDICESIMA = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="tredicesima",
    payment_month=12,
    accrual_window_start_month=1,
)
_RULE = MonthAccrualRule(
    min_days=None, comparison=AccrualComparison.CUMULATED_FRACTIONS
)


@pytest.mark.parametrize(
    ("hired", "ended", "months", "units"),
    [
        # 10-31 March 22 days + 1-20 October 20 days = 42: 1 rateo, 12 left.
        (date(2026, 3, 10), date(2026, 10, 20), 6, "1"),
        # 22 + 1-25 October 25 days = 47: 1 rateo and 17 >= 15, one more.
        (date(2026, 3, 10), date(2026, 10, 25), 6, "2"),
        # 17-31 December 15 days alone: the remainder of 15 accrues.
        (date(2026, 12, 17), None, 0, "1"),
        # 18-31 December 14 days: nothing.
        (date(2026, 12, 18), None, 0, "0"),
    ],
    ids=["42_days", "47_days", "15_days", "14_days"],
)
def test_partial_months_are_summed(
    hired: date, ended: date | None, months: int, units: str
) -> None:
    """Whole months count one each; the partial days count by 30 and 15."""
    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA, 2026, EmploymentPeriod(hired, ended), rule=_RULE
    )

    assert (accrual.months, accrual.day_units) == (months, Decimal(units))
