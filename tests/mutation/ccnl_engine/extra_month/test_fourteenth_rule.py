"""Hand oracle: a quattordicesima counted apart from the tredicesima.

Recapito FISE art. 40 c. 2: "La frazione di mese superiore a 15 giorni
lavorativi si considera [...] come mese intero"; art. 41 c. 3: the
quattordicesima counts a fraction "se superiore a 15 giorni".  Hired on
Tuesday 15 July 2025: 17 calendar days, 15 working days (Sundays 20 and
27 out).  July is a month of the 14th, not of the 13th.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule

_HIRED = EmploymentPeriod(date(2025, 7, 15), None)
_RULE = month_accrual_rule(load_ccnl("recapito-corrispondenza-fise"))


def _months(kind: ExtraMonthKind, paid: int, start: int, year: int) -> int:
    schedule = ExtraMonthSchedule(
        kind=kind,
        name=kind.value,
        payment_month=paid,
        accrual_window_start_month=start,
    )
    return ExtraMonthAccrual.of(schedule, year, _HIRED, rule=_RULE).months


def test_the_thirteenth_counts_working_days() -> None:
    """15 working days in July: August to December, five months."""
    assert _months(ExtraMonthKind.THIRTEENTH, 12, 1, 2025) == 5


def test_the_fourteenth_counts_calendar_days() -> None:
    """17 calendar days in July: July to June, twelve months."""
    assert _months(ExtraMonthKind.FOURTEENTH, 6, 7, 2026) == 12


def test_a_rule_without_its_own_fourteenth_counts_both_alike() -> None:
    """Without a clause of the 14th, the 13th clause counts it."""
    schedule = ExtraMonthSchedule(
        kind=ExtraMonthKind.FOURTEENTH,
        name="fourteenth",
        payment_month=6,
        accrual_window_start_month=7,
    )
    rule = _RULE.fourteenth
    assert rule is not None
    plain = ExtraMonthAccrual.of(schedule, 2026, _HIRED, rule=rule)
    assert plain.months == 12
    assert plain.rule is rule
