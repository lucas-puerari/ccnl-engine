"""A parental leave by the hour, Metalmeccanico Federmeccanica C3.

C3, 2158.26 EUR a month, hourly divisor 173, an average day of 8 hours:
4 hours of leave on 2 to 5 March 2026, two days of leave of a child born
on 1 June 2025, its maternity ended on 1 September 2025: the 2025 cohort
pays three months at 80% while the child is under six.

- Deduction: 16 hours at 2158.26 / 173: 199.61, out of the INPS and TFR
  bases.
- Indemnity: the daily base on the pay of the run, 2158.26 / 30 plus the
  rateo of the 13th, 2158.26 / 360: 77.937; four half days at 80%: 77.937
  * 0.80 * 4 / 2 = 124.70.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    HourlyParentalLeaveEvent,
    InpsSicknessBase,
    LeaveHours,
    ParentalLeaveTaken,
)
from tests.integration.ccnl_engine.absence.insured.parental.test_handlers import (
    _amounts,
    _run,
)
from tests.integration.ccnl_engine.absence.insured.permit.test_handlers import (
    _run as _permit_run,
)

_BORN = date(2025, 6, 1)


def _leave(
    *days: int, average: Decimal = Decimal(8), born: date = _BORN
) -> HourlyParentalLeaveEvent:
    return HourlyParentalLeaveEvent(
        tuple(LeaveHours(date(2026, 3, d), average / 2) for d in days),
        born,
        ParentalLeaveTaken(0, 0, 0),
        average,
        protection_ended_on=date(2025, 9, 1),
    )


def test_four_half_days_are_two_days_of_leave_at_80_percent() -> None:
    """The hours at the hourly base, half the daily indemnity a day."""
    result = _run(_leave(2, 3, 4, 5))

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("199.61")),
        "maternity_item": ("inps", Decimal("124.70")),
    }
    (decision,) = (d for d in result.decisions if d.capability == "parental_leave")
    assert (decision.reason_code, decision.amount, decision.inputs["deduction"]) == (
        "statutory_only",
        Decimal("124.70"),
        Decimal("199.61"),
    )
    (item,) = (i for i in result.pay_items if i.kind == "maternity_item")
    assert item.absence_days == Decimal(2)
    ids = {lim.id for lim in result.limitations}
    assert {"parental_hourly_ccnl_rule", "parental_extra_month_share"} <= ids


def test_without_an_hourly_base_the_hours_post_nothing() -> None:
    """Chimica PMI: the indemnity is paid, the hours are not deducted."""
    result = _permit_run(_leave(2, 3), ccnl=("chimica-affini-pmi-unionchimica", "D"))

    codes = {i.code for i in result.issues if i.capability == "parental_leave"}
    assert "parental_hours_underived" in codes
    (decision,) = (d for d in result.decisions if d.capability == "parental_leave")
    assert (decision.status, decision.reason_code) == (
        "incomplete",
        "parental_hours_underived",
    )


def test_the_leave_ends_before_the_fourteenth_birthday() -> None:
    """The last day falls on the fourteenth birthday: no longer leave."""
    with pytest.raises(InvalidInputError) as error:
        _run(_leave(2, 3, 4, 5, born=date(2012, 3, 5)))

    assert (str(error.value), error.value.field, error.value.feature) == (
        "HourlyParentalLeaveEvent.hours must precede the child's 14th birthday",
        "HourlyParentalLeaveEvent.hours",
        "parental_leave",
    )


def test_the_pay_of_the_month_before_gives_the_daily_base() -> None:
    """February 2400.00 with the rateo of the 13th: 86.667 a day; 138.67.

    2400 / 30 + 2400 / 360 = 86.667; four half days at 80%: 138.67.
    """
    leave = HourlyParentalLeaveEvent(
        tuple(LeaveHours(date(2026, 3, d), Decimal(4)) for d in (2, 3, 4, 5)),
        _BORN,
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        protection_ended_on=date(2025, 9, 1),
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
    )

    assert _amounts(_run(leave))["maternity_item"] == ("inps", Decimal("138.67"))


def test_beyond_the_indemnified_months_the_days_are_unpaid() -> None:
    """Every month taken: 8 hours deducted (99.80), the days paid nothing."""
    leave = HourlyParentalLeaveEvent(
        (
            LeaveHours(date(2026, 3, 2), Decimal(4)),
            LeaveHours(date(2026, 3, 3), Decimal(4)),
        ),
        _BORN,
        ParentalLeaveTaken(90, 90, 90),
        Decimal(8),
    )
    result = _run(leave)

    assert _amounts(result) == {"absence_deduction": ("abs", Decimal("99.80"))}
    ids = {lim.id for lim in result.limitations}
    assert "parental_income_condition" in ids


def test_an_unstated_end_matters_for_a_child_born_in_2024() -> None:
    """The birth gives two months at 80%; a 2025 end would give three."""
    leave = HourlyParentalLeaveEvent(
        tuple(LeaveHours(date(2026, 3, d), Decimal(4)) for d in (2, 3)),
        date(2024, 6, 1),
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
    )

    assert "parental_protection_end_unknown" in {i.code for i in _run(leave).issues}
