"""A threshold counted on working days: CCNL Cooperative sociali art. 79.

"La frazione di mese superiore ai 15 giorni lavorativi va considerata come
mese intero"; art. 60 counts the working days "su una settimana lavorativa
di 6 giorni", so Monday to Saturday.

Hired on Friday 13 November 2026: 13-30 November is 18 calendar days but
15 days from Monday to Saturday (Sundays 15, 22 and 29), so the month does
not count; hired on Thursday 12 November, 16 working days, it counts.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.compensation.models import AccrualComparison, ExtraMonthAccrualRule
from ccnl_engine.employment.fact.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual, MonthAccrualRule
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance

_TREDICESIMA = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="tredicesima",
    payment_month=12,
    accrual_window_start_month=1,
)
_RULE = MonthAccrualRule(
    min_days=15, comparison=AccrualComparison.MORE_THAN, working_days=True
)


@pytest.mark.parametrize(("hired", "months"), [(13, 1), (12, 2)])
def test_november_counts_on_more_than_15_working_days(hired: int, months: int) -> None:
    """December whole; November counts only with 16 working days."""
    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA, 2026, EmploymentPeriod(date(2026, 11, hired)), rule=_RULE
    )

    assert accrual.months == months


def test_calendar_days_would_count_the_same_month() -> None:
    """18 calendar days pass a calendar threshold of 15."""
    calendar_rule = MonthAccrualRule(
        min_days=15, comparison=AccrualComparison.MORE_THAN
    )

    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA, 2026, EmploymentPeriod(date(2026, 11, 13)), rule=calendar_rule
    )

    assert accrual.months == 2


def test_day_based_rule_takes_no_working_days() -> None:
    """Working days qualify a threshold, not a day-based comparison."""
    source = RuleProvenance(status=ProvenanceStatus.ASSUMED, note="test")
    with pytest.raises(ValueError, match="leave min_days and working_days out"):
        ExtraMonthAccrualRule(
            comparison=AccrualComparison.DAYS_365, working_days=True, provenance=source
        )
