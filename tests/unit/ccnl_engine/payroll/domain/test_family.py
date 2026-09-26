"""Unit tests for Dependent and FamilyComposition domain models."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)

_SPOUSE = DependentRelationship.SPOUSE
_CHILD = DependentRelationship.CHILD
_ASCENDANT = DependentRelationship.ASCENDANT


class TestDependentDefaults:
    """Dependent — default field values."""

    def test_defaults(self) -> None:
        """Defaults: own_income=0, months=12, alloc=100, cohabiting, eligible."""
        dep = Dependent(relationship=_SPOUSE)
        assert dep.birth_date is None
        assert dep.disabled is False
        assert dep.own_income == Decimal(0)
        assert dep.months_dependent == 12
        assert dep.allocation_pct == Decimal(100)
        assert dep.cohabiting is True
        assert dep.residency_eligibility is True

    def test_string_relationship_coerced(self) -> None:
        """StrEnum coerces plain string to DependentRelationship via pydantic."""
        dep = Dependent.model_validate({"relationship": "child"})
        assert dep.relationship == _CHILD

    def test_birth_date_accepted(self) -> None:
        """birth_date is stored as-is when supplied."""
        d = date(2000, 6, 15)
        dep = Dependent(relationship=_CHILD, birth_date=d)
        assert dep.birth_date == d


class TestDependentValidation:
    """Dependent — field constraints."""

    def test_negative_own_income_raises(self) -> None:
        """own_income must be >= 0."""
        with pytest.raises(ValidationError):
            Dependent(relationship=_SPOUSE, own_income=Decimal(-1))

    def test_months_below_one_raises(self) -> None:
        """months_dependent must be >= 1."""
        with pytest.raises(ValidationError):
            Dependent(relationship=_CHILD, months_dependent=0)

    def test_months_above_twelve_raises(self) -> None:
        """months_dependent must be <= 12."""
        with pytest.raises(ValidationError):
            Dependent(relationship=_CHILD, months_dependent=13)

    def test_allocation_below_zero_raises(self) -> None:
        """allocation_pct must be >= 0."""
        with pytest.raises(ValidationError):
            Dependent(relationship=_CHILD, allocation_pct=Decimal(-1))

    def test_allocation_above_hundred_raises(self) -> None:
        """allocation_pct must be <= 100."""
        with pytest.raises(ValidationError):
            Dependent(relationship=_CHILD, allocation_pct=Decimal(101))

    def test_frozen(self) -> None:
        """Dependent is frozen and cannot be mutated."""
        dep = Dependent(relationship=_SPOUSE)
        with pytest.raises((AttributeError, TypeError, ValidationError)):
            dep.disabled = True  # type: ignore[misc]


class TestFamilyCompositionDefaults:
    """FamilyComposition — default empty state."""

    def test_default_empty(self) -> None:
        """Default: no dependents."""
        assert FamilyComposition().dependents == ()

    def test_has_any_dependent_false_by_default(self) -> None:
        """has_any_dependent is False when no dependents are declared."""
        assert FamilyComposition().has_any_dependent is False


class TestFamilyCompositionHasAnyDependent:
    """FamilyComposition.has_any_dependent — truth table."""

    def test_spouse_sets_flag(self) -> None:
        """One spouse dependent → has_any_dependent True."""
        fc = FamilyComposition(dependents=(Dependent(relationship=_SPOUSE),))
        assert fc.has_any_dependent is True

    def test_child_sets_flag(self) -> None:
        """One child dependent → has_any_dependent True."""
        fc = FamilyComposition(dependents=(Dependent(relationship=_CHILD),))
        assert fc.has_any_dependent is True

    def test_ascendant_sets_flag(self) -> None:
        """One ascendant dependent → has_any_dependent True."""
        fc = FamilyComposition(dependents=(Dependent(relationship=_ASCENDANT),))
        assert fc.has_any_dependent is True

    def test_empty_dependents_false(self) -> None:
        """Empty tuple → has_any_dependent False."""
        assert FamilyComposition(dependents=()).has_any_dependent is False

    def test_frozen(self) -> None:
        """FamilyComposition is frozen and cannot be mutated."""
        fc = FamilyComposition(dependents=(Dependent(relationship=_SPOUSE),))
        with pytest.raises((AttributeError, TypeError, ValidationError)):
            fc.dependents = ()  # type: ignore[misc]
