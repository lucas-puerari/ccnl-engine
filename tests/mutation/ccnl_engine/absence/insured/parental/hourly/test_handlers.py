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

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.absence.insured.handlers import NOT_MODELLED
from ccnl_engine.absence.insured.parental.hourly.rules import hourly_top_up
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    HourlyParentalLeaveEvent,
    InpsSicknessBase,
    LeaveHours,
    ParentalLeaveTaken,
)
from tests.mutation.ccnl_engine.absence.insured.parental.test_handlers import (
    _amounts,
    _run,
)
from tests.mutation.ccnl_engine.absence.insured.permit.test_handlers import (
    _run as _permit_run,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

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


def test_collective_hourly_supplement_and_statutory_only() -> None:
    """Two four-hour days are one day: 2400/30 + 2*2400/360 = 93.3333.

    With 14 monthly payments, INPS pays 28.00 at 30% and an 80% rule
    adds 46.67. Without a top-up, 13 payments give INPS 26.00 only.
    """
    leave = HourlyParentalLeaveEvent(
        (
            LeaveHours(date(2026, 3, 2), Decimal(4)),
            LeaveHours(date(2026, 3, 3), Decimal(4)),
        ),
        date(2022, 6, 1),
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
        topped_up_days_before=Decimal(0),
    )
    topped = _amounts(_run(leave, ccnl_id="autorimesse-ic35", level_code="C4"))
    plain = _amounts(_run(leave))
    assert topped["maternity_item"] == ("inps", Decimal("28.00"))
    assert plain["maternity_item"] == ("inps", Decimal("26.00"))
    assert topped["absence_integration_item"] == ("intg", Decimal("46.67"))
    assert "absence_integration_item" not in plain


def test_half_day_remaining_under_collective_cap() -> None:
    """With 89.5 of 90 days used, two four-hour days yield one half-day.

    At 2400/30 + 2400/360 = 86.6667 per day, the 50%-less-30%
    supplement for a single half-day is 86.6667 * 0.20 / 2 = 8.67.
    """
    leave = HourlyParentalLeaveEvent(
        (
            LeaveHours(date(2026, 3, 2), Decimal(4)),
            LeaveHours(date(2026, 3, 3), Decimal(4)),
        ),
        date(2022, 6, 1),
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
        topped_up_days_before=Decimal("89.5"),
    )
    work_rules = load_ccnl("materiali-costruzione-lapidei-confapi").work_rules
    assert work_rules is not None
    assert work_rules.insured_absence is not None
    rule = work_rules.insured_absence.parental
    assert hourly_top_up(
        leave,
        {date(2026, 3, 2): Decimal("0.3"), date(2026, 3, 3): Decimal("0.3")},
        (date(2026, 3, 1), date(2026, 3, 31)),
        Decimal(2400) / 30 + Decimal(2400) / 360,
        rule,
        Decimal("0.3"),
    ) == (Decimal("8.67"), Decimal("0.5"))


def test_missing_collective_history_does_not_post_a_supplement() -> None:
    """Without the prior supplemented-day count, no 80% top-up is posted."""
    result = _run(_leave(2, 3), ccnl_id="autorimesse-ic35", level_code="C4")
    assert "absence_integration_item" not in _amounts(result)
    assert "parental_top_up_history_unknown" in {issue.code for issue in result.issues}


def test_standard_only_supplement_excludes_single_parent() -> None:
    """The 50% rule excludes enhanced statutory months of a sole parent."""
    leave = replace(_leave(2, 3), single_parent=True, topped_up_days_before=Decimal(0))
    work_rules = load_ccnl("materiali-costruzione-lapidei-confapi").work_rules
    assert work_rules is not None
    assert work_rules.insured_absence is not None
    assert hourly_top_up(
        leave,
        {date(2026, 3, 2): Decimal("0.3"), date(2026, 3, 3): Decimal("0.3")},
        (date(2026, 3, 1), date(2026, 3, 31)),
        Decimal(100),
        work_rules.insured_absence.parental,
        Decimal("0.3"),
    ) == (Decimal(0), Decimal(0))


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


def _parental_decision(result: PeriodResult) -> CalculationDecision:
    return next(d for d in result.decisions if d.capability == "parental_leave")


def test_the_collective_top_up_closes_the_rule_gap() -> None:
    """Autorimesse: INPS 28.00 plus the 46.67 top-up; no CCNL rule gap."""
    leave = HourlyParentalLeaveEvent(
        (
            LeaveHours(date(2026, 3, 2), Decimal(4)),
            LeaveHours(date(2026, 3, 3), Decimal(4)),
        ),
        date(2022, 6, 1),
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
        topped_up_days_before=Decimal(0),
    )
    topped = _run(leave, ccnl_id="autorimesse-ic35", level_code="C4")
    plain = _run(leave)

    decision = _parental_decision(topped)
    assert decision.inputs["integration"] == Decimal("46.67")
    assert decision.amount == Decimal("74.67")
    assert NOT_MODELLED not in {i.code for i in topped.issues}

    statutory = _parental_decision(plain)
    assert statutory.status is CalculationStatus.PROVISIONAL
    assert statutory.reason_code == "statutory_only"
    gap = next(i for i in plain.issues if i.code == NOT_MODELLED)
    assert gap.capability == "parental_leave"


def test_unknown_history_is_an_incomplete_fact_issue() -> None:
    """The missing count names its field; the CCNL treatment is not applied."""
    result = _run(_leave(2, 3), ccnl_id="autorimesse-ic35", level_code="C4")

    issue = next(
        i for i in result.issues if i.code == "parental_top_up_history_unknown"
    )
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.capability == "parental_leave"
    assert issue.cause is IssueCause.FACT
    assert issue.fact == "topped_up_days_before"
    assert issue.message.startswith(
        "HourlyParentalLeaveEvent.topped_up_days_before is required"
    )
    assert _parental_decision(result).inputs["integration"] == Decimal(0)
    assert NOT_MODELLED not in {i.code for i in result.issues}
