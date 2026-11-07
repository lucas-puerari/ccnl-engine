"""The bundled CCNLs that accrue the extra months by days, not by a threshold.

- Turismo Federalberghi, ipotesi 5 July 2024, art. 160 c. 2: the days worked
  in a month not worked in full accrue in twenty-sixths of a rateo;
- Sanità 2022-2024 art. 60 c. 4: a twelfth per whole month and a 365th of
  the year per day of a month served in part;
- Funzioni Locali 16 November 2022 art. 75 c. 3: a 365th of the year for
  every day served.

Hired on Tuesday 17 November 2026: 17-30 November is 14 days, 12 of them
from Monday to Saturday; December is whole.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule

_TREDICESIMA = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="tredicesima",
    payment_month=12,
    accrual_window_start_month=1,
)
_HIRED = EmploymentPeriod(date(2026, 11, 17))


@pytest.mark.parametrize(
    ("slug", "accrued"),
    [
        ("turismo-federalberghi", 1 + Decimal(12) / 26),
        ("sanita-aran", 1 + Decimal(14 * 12) / 365),
        ("funzioni-locali-aran", Decimal(45 * 12) / 365),
    ],
)
def test_hire_in_november_accrues_by_days(slug: str, accrued: Decimal) -> None:
    """The months of the tredicesima paid in December 2026."""
    rule = month_accrual_rule(load_ccnl(slug))

    accrual = ExtraMonthAccrual.of(_TREDICESIMA, 2026, _HIRED, rule=rule)

    assert rule.min_days is None
    assert accrual.accrued == accrued
