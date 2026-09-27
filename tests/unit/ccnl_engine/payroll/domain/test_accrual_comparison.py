"""The comparison of a month-qualification rule and the partly accrued months."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.contract.domain.compensation import AccrualComparison
from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_ACCRUAL_RULE_ID,
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
    partial_months,
)
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.extra_month_schedule import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)

_YEAR = 2026
_TREDICESIMA = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="tredicesima",
    payment_month=12,
    accrual_window_start_month=1,
)
_MORE_THAN = MonthAccrualRule(min_days=15, comparison=AccrualComparison.MORE_THAN)
# Hired on 17 December: 17 to 31 December is exactly 15 calendar days.
_FIFTEEN_DAYS = EmploymentPeriod(date(_YEAR, 12, 17))


def test_default_rule_counts_at_least_fifteen_days() -> None:
    """The engine default is ``at_least`` 15 with no provenance."""
    assert DEFAULT_MONTH_ACCRUAL_RULE.comparison is AccrualComparison.AT_LEAST
    assert DEFAULT_MONTH_ACCRUAL_RULE.rule == DEFAULT_ACCRUAL_RULE_ID
    assert DEFAULT_MONTH_ACCRUAL_RULE.provenance is None


@pytest.mark.parametrize(
    ("rule", "counted"),
    [
        (DEFAULT_MONTH_ACCRUAL_RULE, (False, True, True)),
        (_MORE_THAN, (False, False, True)),
    ],
    ids=["at_least", "more_than"],
)
def test_counts_compares_with_the_threshold(
    rule: MonthAccrualRule, counted: tuple[bool, bool, bool]
) -> None:
    """14, 15 and 16 days: 15 counts only under ``at_least``."""
    assert (rule.counts(14), rule.counts(15), rule.counts(16)) == counted


@pytest.mark.parametrize(
    ("rule", "months"),
    [(DEFAULT_MONTH_ACCRUAL_RULE, 1), (_MORE_THAN, 0)],
    ids=["at_least", "more_than"],
)
def test_month_of_exactly_fifteen_days(rule: MonthAccrualRule, months: int) -> None:
    """A December of 15 employed days is one rateo at least 15, none above 15."""
    accrual = ExtraMonthAccrual.of(_TREDICESIMA, _YEAR, _FIFTEEN_DAYS, rule=rule)
    assert accrual.months == months
    assert accrual.partial_months == 1
    assert accrual.rule is rule


@pytest.mark.parametrize(
    ("comparison", "min_days"),
    [
        (AccrualComparison.AT_LEAST, 0),
        (AccrualComparison.AT_LEAST, 29),
        (AccrualComparison.MORE_THAN, -1),
        (AccrualComparison.MORE_THAN, 28),
    ],
)
def test_threshold_must_let_a_full_month_count(
    comparison: AccrualComparison, min_days: int
) -> None:
    """A threshold a 28-day February cannot pass, or below one day, fails."""
    with pytest.raises(ValueError, match="min_days must be between"):
        MonthAccrualRule(min_days=min_days, comparison=comparison)


def test_more_than_zero_counts_any_accruing_day() -> None:
    """``more_than`` 0 is the lowest threshold: one day counts."""
    rule = MonthAccrualRule(min_days=0, comparison=AccrualComparison.MORE_THAN)
    assert rule.counts(1)
    assert not rule.counts(0)


def test_whole_months_are_not_partial() -> None:
    """A window worked in full, or not at all, has no partly accrued month."""
    window = _TREDICESIMA.accrual_window(_YEAR, None)
    assert partial_months(window) == 0
    assert partial_months(window, ended_on=date(_YEAR, 6, 30)) == 0
    assert partial_months(window, ended_on=date(_YEAR, 6, 10)) == 1


def test_absence_days_make_a_month_partial() -> None:
    """Days of an accrual-suspending absence leave the month partly accrued."""
    window = _TREDICESIMA.accrual_window(_YEAR, None)
    absent = frozenset({date(_YEAR, 3, 2), date(_YEAR, 3, 3)})
    assert partial_months(window, non_accruing_days=absent) == 1
