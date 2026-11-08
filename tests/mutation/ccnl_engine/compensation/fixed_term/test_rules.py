"""Operai agricoli a tempo determinato (OTD), CCNL 23 May 2022 art. 50.

The OTD is paid the salario of the hours worked (monthly over 169) and a
terzo elemento of 30.44% on it "quale corrispettivo" of the festività, the
ferie, the tredicesima and the quattordicesima, outside the TFR base
(art. 58: "il TFR non si calcola sul terzo elemento").  Area 2,
January 2026: salario 1,330.25; 120 hours pay 1,330.25 / 169 x 120 =
944.556 -> 944.56, terzo elemento 944.56 x 0.3044 = 287.524 -> 287.52.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.fixed_term.rules import (
    overtime_hours,
    overtime_tfr,
    with_fixed_term_pay,
)
from ccnl_engine.errors import OutOfScopeError
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

_CCNL_ID = "operai-agricoli-florovivaisti"


def _employment(contract: object) -> Employment:
    return Employment(
        ccnl_id=_CCNL_ID,
        level_code="Area2",
        category=WorkerCategory.OPERAIO,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=contract,  # type: ignore[arg-type]
    )


def _pay(contract: object) -> dict[str, Decimal]:
    result = regular_period(
        employment=_employment(contract),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(120)),
    )
    return {i.item_id.removesuffix("-regular"): i.amount for i in result.pay_items}


def test_an_otd_is_paid_the_hours_and_the_terzo_elemento() -> None:
    """944.56 for the hours, 287.52 of terzo elemento, TFR 8.63% of the hours."""
    pay = _pay(FixedTerm())
    assert pay["base_salary_2026-01"] == Decimal("944.56")
    assert pay["terzo_elemento_2026-01"] == Decimal("287.52")
    assert pay["tfr_2026-01"] == Decimal("81.52")  # 944.56 x 8.63%


def test_an_oti_keeps_the_monthly_pay() -> None:
    """The permanent operaio is paid the month and no terzo elemento."""
    pay = _pay(Permanent())
    assert pay["base_salary_2026-01"] == Decimal("1330.25")
    assert "terzo_elemento_2026-01" not in pay


def test_the_otd_accrues_no_extra_month_and_no_leave() -> None:
    """Twelve monthly payments and no leave rules for the OTD."""
    ccnl = with_fixed_term_pay(load_ccnl(_CCNL_ID), WorkerCategory.OPERAIO, FixedTerm())
    assert ccnl.parameters.additional_months.value_at(date(2026, 1, 1)) == 12
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.leave_rules is None


def test_an_impiegato_or_a_permanent_operaio_is_unchanged() -> None:
    """The rule covers the fixed-term operai only."""
    ccnl = load_ccnl(_CCNL_ID)
    assert with_fixed_term_pay(ccnl, WorkerCategory.IMPIEGATO, FixedTerm()) is ccnl
    assert with_fixed_term_pay(ccnl, WorkerCategory.OPERAIO, Permanent()) is ccnl


def test_a_ccnl_without_the_rule_is_unchanged() -> None:
    """Commercio sets no fixed-term pay."""
    ccnl = load_ccnl("commercio-confcommercio")
    assert with_fixed_term_pay(ccnl, WorkerCategory.OPERAIO, FixedTerm()) is ccnl


def test_the_thirteenth_of_an_otd_is_refused() -> None:
    """The tredicesima is in the terzo elemento: no thirteenth run."""
    hired = date(2026, 1, 1)
    with pytest.raises(OutOfScopeError, match="thirteenth in a percentage"):
        PayrollEngine.bundled().calculate_period(
            PeriodInput(
                run=PayrollRun.thirteenth(2026, 12),
                payment_date=date(2026, 12, 15),
                employment=Employment(
                    ccnl_id=_CCNL_ID,
                    level_code="Area2",
                    category=WorkerCategory.OPERAIO,
                    contract_type=FixedTerm(),
                    employment_period=EmploymentPeriod(hired, None),
                    seniority=SeniorityFact.since(
                        hired, SenioritySource.EMPLOYER_RECORDS
                    ),
                    pension_fund=NoPensionFund(),
                ),
                employer=EmployerProfile(headcount=Headcount(10)),
            )
        )


def test_a_ccnl_without_work_rules_keeps_none() -> None:
    """The pay applies; there are no leave rules to drop."""
    bare = load_ccnl(_CCNL_ID).model_copy(update={"work_rules": None})
    ccnl = with_fixed_term_pay(bare, WorkerCategory.OPERAIO, FixedTerm())
    assert ccnl.work_rules is None
    assert ccnl.parameters.hourly_pay is not None


def test_a_cooperative_otd_is_paid_the_hours_and_the_terzo_elemento() -> None:
    """Cooperative e consorzi agricoli, art. 60 (verbale 2024, p. 14)."""
    ccnl = load_ccnl("cooperative-consorzi-agricoli")
    level = ccnl.level_by_code("5")
    hourly = level.base_salary.value_at(date(2026, 1, 1)) / Decimal(169)
    result = regular_period(
        employment=Employment(
            ccnl_id="cooperative-consorzi-agricoli",
            level_code="5",
            category=WorkerCategory.OPERAIO,
            seniority=new_hire(),
            pension_fund=NoPensionFund(),
            contract_type=FixedTerm(),
        ),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(100)),
    )
    pay = {i.item_id.removesuffix("-regular"): i.amount for i in result.pay_items}
    paid = (hourly * 100).quantize(Decimal("0.01"))
    assert pay["base_salary_2026-01"] == paid
    assert pay["terzo_elemento_2026-01"] == (paid * Decimal("0.3044")).quantize(
        Decimal("0.01")
    )
    # Art. 66: 8.63% of the minimo of the hours, without the terzo elemento.
    assert pay["tfr_2026-01"] == (paid * Decimal("0.0863")).quantize(Decimal("0.01"))


def test_the_terzo_elemento_is_paid_on_the_overtime_hours() -> None:
    """Art. 44: also on the overtime hours, at the ordinary measure.

    120 hours worked and 10 of overtime: the base of the terzo elemento is
    944.56 x 130 / 120 = 1,023.273 -> 1,023.27, times 30.44% = 311.48.
    """
    result = regular_period(
        employment=_employment(FixedTerm()),
        current_year=employment_only(),
        events=(
            OvertimeEvent(date(2026, 1, 15), Decimal(10), hourly_rate=Decimal("7.87")),
        ),
        ordinary_hours_worked=ContributableHours(Decimal(120)),
    )
    pay = {i.item_id.removesuffix("-regular"): i.amount for i in result.pay_items}
    assert pay["terzo_elemento_2026-01"] == Decimal("311.48")


def test_overtime_hours_count_only_for_the_fixed_term_pay() -> None:
    """A permanent operaio, or a CCNL without the rule, adds no hours."""
    events = (OvertimeEvent(date(2026, 1, 15), Decimal(10)),)
    ccnl = load_ccnl(_CCNL_ID)
    assert overtime_hours(ccnl, events) == 0
    otd = with_fixed_term_pay(ccnl, WorkerCategory.OPERAIO, FixedTerm())
    assert overtime_hours(otd, events) == 10
    assert overtime_hours(load_ccnl("commercio-confcommercio"), events) == 0


def _tfr(*, non_occasional: bool) -> Decimal:
    event = OvertimeEvent(
        date(2026, 1, 15),
        Decimal(10),
        hourly_rate=Decimal("7.87"),
        non_occasional=non_occasional,
    )
    result = regular_period(
        employment=_employment(FixedTerm()),
        current_year=employment_only(),
        events=(event,),
        ordinary_hours_worked=ContributableHours(Decimal(120)),
    )
    return next(i.amount for i in result.pay_items if i.item_id.startswith("tfr_"))


def test_non_occasional_overtime_accrues_ten_percent_tfr() -> None:
    """Art. 58: 10% of the salario of the non-occasional overtime hours.

    1,330.25 / 169 x 10 hours x 10% = 7.871 -> 7.87 on top of the 8.63%.
    """
    assert _tfr(non_occasional=True) - _tfr(non_occasional=False) == Decimal("7.87")


def test_overtime_tfr_counts_only_non_occasional_otd_hours() -> None:
    """Occasional hours, a permanent operaio and other CCNLs accrue none."""
    day = date(2026, 1, 15)
    hours = OvertimeEvent(day, Decimal(10), non_occasional=True)
    occasional = OvertimeEvent(day, Decimal(10))
    ccnl = load_ccnl(_CCNL_ID)
    otd = with_fixed_term_pay(ccnl, WorkerCategory.OPERAIO, FixedTerm())
    level = otd.level_by_code("Area2")
    assert overtime_tfr(otd, level, (hours, occasional, object()), day) == Decimal(
        "7.87"
    )
    assert overtime_tfr(otd, level, (occasional,), day) == 0
    assert overtime_tfr(ccnl, level, (hours,), day) == 0
    commercio = load_ccnl("commercio-confcommercio")
    assert overtime_tfr(commercio, commercio.levels[0], (hours,), day) == 0
