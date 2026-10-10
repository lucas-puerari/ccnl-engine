"""Art. 12 TUIR deductions of a whole family on the 2026 bundle."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.family.inputs import (
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.family.rules_deduction import compute_family_deductions
from ccnl_engine.tax.annual.loaders_optional import load_family_deduction_rules
from tests.fixtures.dependents import declared_dependent

_D = Decimal
_RULES = load_family_deduction_rules(2026)
_SPOUSE = DependentRelationship.SPOUSE
_CHILD = DependentRelationship.CHILD
_ASCENDANT = DependentRelationship.ASCENDANT


def test_family_sums_each_dependent() -> None:
    """R 30,000: spouse 710, child 649.99, ascendant 750 x 0.625 = 468.75.

    Child: (95,000 - 30,000) / 95,000 = 0.684210... -> 0.6842, 649.99.
    Ascendant: (80,000 - 30,000) / 80,000 = 0.625.
    """
    family = FamilyComposition(
        dependents=(
            declared_dependent(relationship=_ASCENDANT),
            declared_dependent(relationship=_CHILD, birth_date=date(2001, 3, 1)),
            declared_dependent(relationship=_SPOUSE),
        )
    )
    deductions = compute_family_deductions(family, _D(30000), _RULES)
    assert deductions.of(_SPOUSE) == _D(710)
    assert deductions.of(_CHILD) == _D("649.99")
    assert deductions.of(_ASCENDANT) == _D("468.75")
    assert deductions.total == _D("1828.74")
    assert [d.dependent.relationship for d in deductions.dependents] == [
        _SPOUSE,
        _CHILD,
        _ASCENDANT,
    ]
    assert deductions.entitled


def test_negative_income_counts_as_zero() -> None:
    """No income: the spouse ratio of number 1) is zero, not due (c. 4)."""
    family = FamilyComposition(dependents=(declared_dependent(relationship=_SPOUSE),))
    assert compute_family_deductions(family, _D(-100), _RULES).total == _D(0)


def test_entitled_is_about_months_not_amounts() -> None:
    """Above every ceiling the amount is zero but the spouse is entitled."""
    spouse = FamilyComposition(dependents=(declared_dependent(relationship=_SPOUSE),))
    assert compute_family_deductions(spouse, _D(200000), _RULES).entitled
    child = FamilyComposition(
        dependents=(
            declared_dependent(relationship=_CHILD, birth_date=date(2015, 1, 1)),
        )
    )
    deductions = compute_family_deductions(child, _D(20000), _RULES)
    assert not deductions.entitled
    assert deductions.total == _D(0)
