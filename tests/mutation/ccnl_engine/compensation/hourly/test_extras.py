"""Caller-selected all-inclusive hourly pay of short-engagement workers.

Art. 155(3) replacement table, 2024 renewal p. 44: level 5 from May 2026
is 14.85 an hour. Five hours give 5 x 14.85 = 74.25; without the
caller-stated role the normal monthly minimum applies instead.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.hourly.models import HourlyPay
from ccnl_engine.compensation.proration.hourly_rules import (
    hourly_ratio,
    selected_hourly_rate,
)
from ccnl_engine.inputs import ContributableHours, FixedTerm, NoPensionFund, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

pytestmark = pytest.mark.legal_scenario


def test_five_hours_of_a_caller_selected_extra() -> None:
    """Level 5: 5 x 14.85 = 74.25, instead of monthly pay prorated by 172."""
    worker = Employment(
        ccnl_id="turismo-federalberghi-alberghi-minori",
        level_code="5",
        contract_type=FixedTerm(),
        seniority=new_hire(2026),
        pension_fund=NoPensionFund(),
        roles=frozenset({"extra"}),
    )
    hours = ContributableHours(Decimal(5))
    extra = regular_period(
        employment=worker,
        year=2026,
        month=5,
        ordinary_hours_worked=hours,
    )
    ordinary = regular_period(
        employment=replace(worker, roles=frozenset()),
        year=2026,
        month=5,
        ordinary_hours_worked=hours,
    )
    assert sum(
        (item.amount for item in extra.pay_items if item.kind == "base_salary_earning"),
        Decimal(0),
    ) == Decimal("74.25")
    assert extra.period_gross == Decimal("74.25")
    assert ordinary.period_gross != extra.period_gross


def test_hourly_rate_table_requires_a_selection_and_unique_rows() -> None:
    """A role table cannot omit all selectors or repeat a role/level pair."""
    spec = load_ccnl("turismo-federalberghi-alberghi-minori").parameters.hourly_pay
    assert spec is not None
    payload = spec.model_dump()
    with pytest.raises(ValueError, match="needs categories or rates"):
        HourlyPay.model_validate(payload | {"rates": (), "categories": ()})
    with pytest.raises(ValueError, match="repeat a role and level"):
        HourlyPay.model_validate(payload | {"rates": (spec.rates[0], spec.rates[0])})


def test_role_selection_and_hourly_divisor_share() -> None:
    """A role and matching level select the rate; 20/40 hours halve the divisor."""
    spec = load_ccnl("turismo-federalberghi-alberghi-minori").parameters.hourly_pay
    assert spec is not None
    assert selected_hourly_rate(spec, None, "5") is None
    assert selected_hourly_rate(spec, frozenset(), "5") is None
    assert selected_hourly_rate(spec, frozenset({"extra"}), "unknown") is None
    assert selected_hourly_rate(spec, frozenset({"other"}), "5") is None
    assert selected_hourly_rate(spec, frozenset({"extra"}), "5") == spec.rates[1]
    twenty, forty = WeeklyHours(Decimal(20)), WeeklyHours(Decimal(40))
    assert hourly_ratio(twenty, forty) == Decimal("0.5")
    assert hourly_ratio(forty, forty) == 1
    assert hourly_ratio(None, forty) == 1
    assert hourly_ratio(twenty, None) == 1
