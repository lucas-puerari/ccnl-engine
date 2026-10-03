"""Ascendant deduction of art. 12 c. 1 lett. d TUIR on the 2026 bundle.

Expected values computed by hand from the text quoted in
:mod:`tests.fixtures.legal_examples.family_2026`: 750 x (80,000 - R) /
80,000, the ratio truncated to four decimals (c. 4).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.family import Dependent, DependentRelationship
from ccnl_engine.payroll.service.family.ascendants import ascendant_deductions
from ccnl_engine.tax.service.tax_optional_loaders import load_family_deduction_rules
from tests.fixtures.legal_examples import family_2026

_D = Decimal
_RULES = load_family_deduction_rules(2026)


def _parent(**kwargs: object) -> Dependent:
    return Dependent(relationship=DependentRelationship.ASCENDANT, **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("income", "expected"),
    [
        ("0", "0.00"),  # ratio 1: not due (c. 4)
        ("30001", "468.68"),  # 0.6249875 -> 0.6249; 468.675
        ("40000", "375.00"),  # 0.5
        ("79999.99", "0.00"),  # 0.01 / 80,000 -> 0.0000
        ("80000", "0.00"),  # ratio 0
        ("80000.01", "0.00"),  # ratio below 0
    ],
)
def test_frontiers(income: str, expected: str) -> None:
    """Full year, full share."""
    (deduction,) = ascendant_deductions([_parent()], _D(income), _RULES)
    assert deduction.amount == _D(expected)
    assert family_2026.ascendant_deduction(_D(income)) == _D(expected)


def test_cohabiting_from_the_end_of_november() -> None:
    """From 30 November: November and December, 375 x 2 / 12 = 62.50."""
    parent = _parent(dependent_from=date(2026, 11, 30))
    (deduction,) = ascendant_deductions([parent], _D(40000), _RULES)
    assert deduction.months == 2
    assert deduction.amount == _D("62.50")


@pytest.mark.parametrize(
    "parent",
    [
        _parent(cohabiting=False),
        _parent(residency_eligibility=False),
        _parent(own_income=_D("2840.52")),
    ],
    ids=["not-cohabiting", "not-resident", "own-income-above-limit"],
)
def test_parent_not_qualifying(parent: Dependent) -> None:
    """Only cohabiting, resident ascendants within the c. 2 limit qualify."""
    (deduction,) = ascendant_deductions([parent], _D(40000), _RULES)
    assert deduction.months == 0
    assert deduction.amount == _D(0)


def test_shared_between_siblings() -> None:
    """Pro quota among those entitled: 375 x 50% = 187.50."""
    (deduction,) = ascendant_deductions(
        [_parent(allocation_pct=_D(50))], _D(40000), _RULES
    )
    assert deduction.amount == _D("187.50")
