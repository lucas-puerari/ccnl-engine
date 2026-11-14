"""The meal owed to a domestic worker and not given, paid in cash.

CCNL lavoro domestico of 28 October 2025 (Assindatcolf PDF, sha256
122ca6a72196a835976abac7fb988dc1502973941d52891a546512347fdc9dcf), Art. 14
c. 8, p. 26: on 6 or more hours a day with continuous presence the worker is
owed the meal "ovvero, in difetto di erogazione, un'indennità pari al suo
valore convenzionale"; Tabella F 2026, p. 59: pranzo e/o colazione 2.33.
Twelve days: 2.33 x 12 = 27.96.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import MealIndennityEvent
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_ENGINE = PayrollEngine.bundled()


def _run(ccnl_id: str, year: int, *events: MealIndennityEvent) -> PeriodResult:
    hours = WeeklyHours(Decimal(40))
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=3),
            payment_date=date(year, 3, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code="B",
                seniority=SeniorityFact(36, date(year, 1, 1), SenioritySource.PAYSLIP),
                weekly_hours=hours,
                full_time_weekly_hours=hours,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(173)), events=events
            ),
        )
    )


def test_twelve_meals_not_given_pay_27_96() -> None:
    """Paid in cash on top of the month, taxable."""
    plain = _run("lavoro-domestico-non-convivente", 2026)
    owed = _run(
        "lavoro-domestico-non-convivente",
        2026,
        MealIndennityEvent(date(2026, 3, 9), 12),
    )
    (decision,) = (d for d in owed.decisions if d.capability == "meal_indennity")

    assert decision.amount == Decimal("27.96")
    assert decision.reason_code == "meal_indennity_paid"
    assert decision.rule == "ccnl/lavoro-domestico-non-convivente:meal_indennity"
    assert dict(decision.inputs) == {
        "days": Decimal(12),
        "daily_value": Decimal("2.33"),
    }
    assert owed.period_gross - plain.period_gross == Decimal("27.96")
    (item,) = (i for i in owed.pay_items if "_evt" in i.item_id)
    assert (item.kind, item.quantity, item.amount) == (
        "fixed_allowance_earning",
        Decimal(12),
        Decimal("27.96"),
    )
    (entry,) = (e for e in owed.ledger_entries if e.source_item_id == item.item_id)
    assert entry.policy_decision_id == "it/earning/ordinary"
    assert entry.entry_id == f"cash_{item.item_id}"
    before, after = plain.closing_state, owed.closing_state
    assert after.cash.earnings.taxable - before.cash.earnings.taxable == Decimal(
        "27.96"
    )


def test_a_ccnl_without_the_value_is_rejected() -> None:
    """The convivente takes its meals in kind: no valore to pay."""
    with pytest.raises(
        InvalidInputError,
        match=(
            r"^MealIndennityEvent: the CCNL states no valore convenzionale of "
            r"the meal on 2026-03-09$"
        ),
    ) as error:
        _run(
            "lavoro-domestico-convivente",
            2026,
            MealIndennityEvent(date(2026, 3, 9), 2),
        )
    assert (error.value.field, error.value.feature) == (
        "MealIndennityEvent",
        "meal_indennity",
    )


@pytest.mark.parametrize("days", [0, 32])
def test_the_days_fall_in_the_month(days: int) -> None:
    """From 1 to the days of the month."""
    with pytest.raises(InvalidInputError, match=r"MealIndennityEvent\.days"):
        MealIndennityEvent(date(2026, 3, 9), days)


def test_february_has_28_days() -> None:
    """29 days do not fit February 2026."""
    with pytest.raises(
        InvalidInputError,
        match=r"^MealIndennityEvent\.days must be at most 28, the days of its month$",
    ) as error:
        MealIndennityEvent(date(2026, 2, 9), 29)
    assert error.value.feature == "meal_indennity"
