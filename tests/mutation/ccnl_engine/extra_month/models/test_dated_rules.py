"""An accrual clause that a renewal changed: each month follows its own.

CCNL Turismo: until 30 June 2024 the fractions of month were cumulated (art.
160 c. 2 of 2010); from 1 July 2024 a month worked in part accrues its days
from Monday to Saturday in twenty-sixths (renewal of 5 July 2024).
Hired on 20 May 2024: May (12 days) and the months before July follow the
old rule, the rest the new one.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.models import AccrualComparison
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual, MonthAccrualRule
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule

_TREDICESIMA = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="tredicesima",
    payment_month=12,
    accrual_window_start_month=1,
)
_OLD = MonthAccrualRule(min_days=None, comparison=AccrualComparison.CUMULATED_FRACTIONS)
_RULE = MonthAccrualRule(
    min_days=None,
    comparison=AccrualComparison.WORKING_DAYS_26,
    valid_from=date(2024, 7, 1),
    previous=_OLD,
)


def test_each_month_follows_the_rule_in_force() -> None:
    """20-31 May 2024: 12 days cumulated, under 15: nothing; June-Dec whole."""
    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA, 2024, EmploymentPeriod(date(2024, 5, 20)), rule=_RULE
    )
    assert (accrual.months, accrual.day_units) == (7, Decimal(0))


def test_a_month_after_the_change_takes_the_new_rule() -> None:
    """Ended on 13 November 2024: 1-13 November, 11 days Monday to Saturday."""
    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA,
        2024,
        EmploymentPeriod(date(2024, 1, 1), date(2024, 11, 13)),
        rule=_RULE,
    )
    assert accrual.months == 10
    assert accrual.day_units == Decimal(11) / Decimal(26)


def test_the_bundle_turismo_clause_is_undated() -> None:
    """Federalberghi: twenty-sixths before and after 2024 (arts. 225 and 277)."""
    rule = month_accrual_rule(load_ccnl("turismo-federalberghi"))
    assert rule.at(date(2024, 6, 1)).comparison is AccrualComparison.WORKING_DAYS_26
    assert rule.at(date(2024, 7, 1)).comparison is AccrualComparison.WORKING_DAYS_26
