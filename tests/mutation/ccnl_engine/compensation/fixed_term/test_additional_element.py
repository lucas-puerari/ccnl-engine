"""The elemento aggiuntivo of the OTD, art. 54-bis (verbale 28/05/2026, p. 34).

From 1 January 2027 an OTD with three consecutive years of 150 days with the
employer is paid 0.4% of the salario contrattuale on the hours.  Area2,
100 hours: before 2027 or with two years nothing; with three, 0.4% of the
same base the terzo elemento is paid on.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.hourly.base import percentage_due
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    WeeklyHours,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.compensation.hourly.models import HourlyPercentage


def _run(year: int, years: int | None) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=3),
            payment_date=date(year, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area2",
                seniority=new_hire(2022),
                roles=frozenset(),
                contract_type=FixedTerm(renewals=0, qualifying_years=years),
                employment_period=EmploymentPeriod(date(2022, 3, 1)),
                weekly_hours=WeeklyHours(Decimal(39)),
                full_time_weekly_hours=WeeklyHours(Decimal(39)),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="A005",
                ordinary_hours_worked=ContributableHours(Decimal(100)),
            ),
        )
    )


def _percentages(result: PeriodResult) -> list[str]:
    return [
        i.item_id.split("_")[0]
        for i in result.pay_items
        if i.kind == "hourly_percentage_earning"
    ]


def test_2026_pays_the_terzo_elemento_alone() -> None:
    """Before 2027 the element is not in force, whatever the years."""
    assert _percentages(_run(2026, None)) == ["terzo"]


def _element() -> HourlyPercentage:
    rule = load_ccnl("operai-agricoli-florovivaisti").parameters.fixed_term_pay
    assert rule is not None
    (element,) = (p for p in rule.hourly_pay.percentages if p.fixed_term_years)
    return element


@pytest.mark.parametrize(
    ("contract", "due"),
    [
        (FixedTerm(qualifying_years=3), True),
        (FixedTerm(qualifying_years=2), False),
        (Permanent(), False),
    ],
    ids=["three-years", "two-years", "permanent"],
)
def test_the_element_needs_three_years(
    contract: FixedTerm | Permanent, due: bool
) -> None:
    """Three consecutive years of 150 days, from 1 January 2027."""
    element = _element()
    assert percentage_due(element, contract, date(2027, 3, 1)) is due
    assert not percentage_due(element, contract, date(2026, 12, 31))


def test_unknown_years_are_a_missing_fact() -> None:
    """In force and not stated: the run cannot tell whether it is due."""
    with pytest.raises(MissingRequiredFactError, match="qualifying_years"):
        percentage_due(_element(), FixedTerm(), date(2027, 3, 1))
