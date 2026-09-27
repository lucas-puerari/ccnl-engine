"""Dated rules the diff tool walks for the employer funds of a CCNL."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.diff.service.rule_walk import dated_rules


def test_fund_rate_and_employee_minimum_are_walked() -> None:
    """ALIFOND yields its employer rate and its employee minimum."""
    rules = {
        rule.path: rule
        for rule in dated_rules(load_ccnl("tabacco-apti.json"))
        if "employer_funds" in rule.path
    }
    assert set(rules) == {
        "parameters.employer_funds[ALIFOND].rate",
        "parameters.employer_funds[ALIFOND].employee_min_rate",
    }
    minimum = rules["parameters.employer_funds[ALIFOND].employee_min_rate"]
    assert minimum.unit == "%"
    assert minimum.series.value_at(date(2026, 1, 1)) == Decimal("0.0100")
