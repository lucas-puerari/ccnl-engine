"""Day-based accrual of the extra months: 26ths, 365ths and 360ths.

- ``working_days_26``: CCNL Turismo 2024 art. 160 c. 2, the days worked in
  a month not worked in full accrue in twenty-sixths of a rateo;
- ``days_365``: CCNL Sanità 2022-2024 art. 60 c. 4, a twelfth per whole
  month and a 365th of the year per day of a month served in part;
- ``days_360``: CCNL Area I 21 April 2006 art. 63 c. 4, the same with a
  360th;
- ``service_days_365``: CCNL Funzioni Locali 16 November 2022 art. 75 c. 3,
  a 365th of the year for every day served.

Hired on Tuesday 17 November 2026: 17-30 November is 14 days, 12 of them
from Monday to Saturday (Sundays 22 and 29); December is whole.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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
_HIRED = EmploymentPeriod(date(2026, 11, 17))
_TWELVE = Decimal(12)


def _accrual(mode: AccrualComparison, **kwargs: object) -> ExtraMonthAccrual:
    rule = MonthAccrualRule(min_days=None, comparison=mode)
    return ExtraMonthAccrual.of(_TREDICESIMA, 2026, _HIRED, rule=rule, **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("mode", "months", "units"),
    [
        (AccrualComparison.WORKING_DAYS_26, 1, Decimal(12) / 26),
        (AccrualComparison.DAYS_365, 1, Decimal(14) * _TWELVE / 365),
        (AccrualComparison.DAYS_360, 1, Decimal(14) / 30),
        (AccrualComparison.SERVICE_DAYS_365, 0, Decimal(14 + 31) * _TWELVE / 365),
    ],
    ids=["26ths", "365ths", "360ths", "service_365ths"],
)
def test_partial_month_accrues_its_days(
    mode: AccrualComparison, months: int, units: Decimal
) -> None:
    """December whole, 17-30 November by days."""
    accrual = _accrual(mode)

    assert (accrual.months, accrual.day_units) == (months, units)
    assert accrual.fraction == (months + units) / _TWELVE


def test_absence_days_do_not_accrue() -> None:
    """Two suspended days of November leave 10 working days."""
    suspended = frozenset({date(2026, 11, 18), date(2026, 11, 19)})

    accrual = _accrual(AccrualComparison.WORKING_DAYS_26, non_accruing_days=suspended)

    assert accrual.day_units * 26 == Decimal(10)


def test_unknown_days_mark_the_units_undetermined() -> None:
    """Days whose suspension is not stated change the units."""
    accrual = _accrual(
        AccrualComparison.DAYS_365, unknown_days=frozenset({date(2026, 11, 18)})
    )

    assert accrual.undetermined


def test_whole_year_of_service_caps_at_twelve() -> None:
    """365 days of 2026 accrue 12 months, never more."""
    rule = MonthAccrualRule(
        min_days=None, comparison=AccrualComparison.SERVICE_DAYS_365
    )

    accrual = ExtraMonthAccrual.of(_TREDICESIMA, 2026, rule=rule)

    assert accrual.accrued == _TWELVE


def test_working_days_cap_at_one_rateo() -> None:
    """A month of 27 working days missing one Sunday still accrues one."""
    rule = MonthAccrualRule(min_days=None, comparison=AccrualComparison.WORKING_DAYS_26)
    # Hired Monday 2 March 2026: 2-31 March holds 26 working days.
    accrual = ExtraMonthAccrual.of(
        _TREDICESIMA, 2026, EmploymentPeriod(date(2026, 3, 2)), rule=rule
    )

    assert (accrual.months, accrual.day_units) == (9, Decimal(1))


def test_stored_day_rule_takes_no_threshold() -> None:
    """A day-based clause leaves ``min_days`` out; a threshold one needs it."""
    source = RuleProvenance(status=ProvenanceStatus.ASSUMED, note="test")
    stored = ExtraMonthAccrualRule(
        comparison=AccrualComparison.DAYS_365, provenance=source
    )
    assert stored.min_days is None
    with pytest.raises(ValueError, match="no threshold"):
        ExtraMonthAccrualRule(
            min_days=15, comparison=AccrualComparison.DAYS_360, provenance=source
        )
    with pytest.raises(ValueError, match="min_days must be between"):
        ExtraMonthAccrualRule(comparison=AccrualComparison.AT_LEAST, provenance=source)
    with pytest.raises(ValueError, match="min_days must be between"):
        MonthAccrualRule(min_days=None, comparison=AccrualComparison.AT_LEAST)
