"""The pay above the CCNL of the year before, stated by the request.

Federmeccanica art. 13 and Confapi art. 48: the 485 EUR of the elemento
perequativo are reduced "fino a concorrenza" by the pay above the CCNL the
worker received in the year before.  Stated, the run deducts it; not
stated, it reads the individual elements and names the missing fact.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.compensation.equalisation.rules import equalisation_outcome
from ccnl_engine.employer.headcount import Headcount
from ccnl_engine.employer.inputs import EmployerProfile
from ccnl_engine.inputs import EmploymentPeriod, Permanent, PriorYearTaxFacts
from ccnl_engine.run.models import RunKind
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period
from tests.unit.ccnl_engine.compensation.equalisation.test_rules import (
    _CONFAPI,
    _request,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.period.requests import PeriodCalculationRequest


def _stated(above: Decimal) -> PeriodCalculationRequest:
    request = _request()
    vars(request)["prior_year"] = PriorYearTaxFacts(pay_above_ccnl=above)
    return request


@pytest.mark.parametrize(
    ("above", "paid"),
    [
        (Decimal(0), Decimal("485.00")),
        (Decimal(100), Decimal("385.00")),
        (Decimal(600), None),
    ],
)
def test_the_stated_pay_reduces_the_element(
    above: Decimal, paid: Decimal | None
) -> None:
    """485 less the pay above the CCNL, never below zero."""
    request = _stated(above)
    events = equalisation_outcome(request, _CONFAPI, RunKind.REGULAR).events
    assert [e.amount for e in events] == ([] if paid is None else [paid])


def _june(prior: PriorYearTaxFacts, premium: bool | None) -> PeriodResult:
    employment = Employment(
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        seniority=new_hire(2020),
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        contract_type=Permanent(),
    )
    employer = EmployerProfile(
        provincial_pay_element=False,
        headcount=Headcount(50),
        second_level_premium=premium,
    )
    return regular_period(
        employment=employment,
        month=6,
        employer=employer,
        current_year=employment_only(),
        prior_year=prior,
    )


def _codes(result: PeriodResult) -> set[str]:
    return {i.code for i in result.issues}


def test_an_unstated_pay_is_a_missing_fact() -> None:
    """Federmeccanica in June: owed, no company bargaining, pay not stated."""
    unknown = _june(PriorYearTaxFacts(), premium=False)
    stated = _june(PriorYearTaxFacts(pay_above_ccnl=Decimal(100)), premium=False)
    company = _june(PriorYearTaxFacts(), premium=True)
    open_ = _june(PriorYearTaxFacts(), premium=None)
    assert "pay_above_ccnl_unknown" in _codes(unknown)
    (issue,) = (i for i in unknown.issues if i.code == "pay_above_ccnl_unknown")
    assert issue.fact == "pay_above_ccnl"
    assert "pay_above_ccnl_unknown" not in _codes(stated)
    assert "pay_above_ccnl_unknown" not in _codes(company)
    assert "pay_above_ccnl_unknown" not in _codes(open_)


def test_a_month_without_the_element_needs_no_pay() -> None:
    """March pays no elemento perequativo."""
    employment = Employment(
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        seniority=new_hire(2020),
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        contract_type=Permanent(),
    )
    employer = EmployerProfile(
        provincial_pay_element=False,
        headcount=Headcount(50),
        second_level_premium=False,
    )
    result = regular_period(
        employment=employment,
        month=3,
        employer=employer,
        current_year=employment_only(),
    )
    assert "pay_above_ccnl_unknown" not in _codes(result)


def test_an_element_excluded_by_any_pay_above() -> None:
    """An element no worker with pay above the CCNL takes: any amount stated."""
    element = _CONFAPI.parameters.equalisation_elements or (
        _CONFAPI.parameters.equalisation_element,
    )
    first = element[0]
    assert first is not None
    excluding = first.model_copy(update={"individual_excludes": True})
    params = _CONFAPI.parameters.model_copy(
        update={"equalisation_element": excluding, "equalisation_elements": ()}
    )
    ccnl = _CONFAPI.model_copy(update={"parameters": params})
    for above, paid in ((Decimal(0), [Decimal("485.00")]), (Decimal(1), [])):
        request = _stated(above)
        events = equalisation_outcome(request, ccnl, RunKind.REGULAR).events
        assert [e.amount for e in events] == paid
