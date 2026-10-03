"""Unit tests for Dependent and FamilyComposition domain models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_SPOUSE = DependentRelationship.SPOUSE
_CHILD = DependentRelationship.CHILD
_ASCENDANT = DependentRelationship.ASCENDANT
_BORN = date(2000, 6, 15)


class TestDependentDefaults:
    """Dependent — default field values."""

    def test_defaults(self) -> None:
        """Defaults: own_income=0, open interval, alloc=100, cohabiting, eligible."""
        dep = Dependent(relationship=_SPOUSE)
        assert dep.birth_date is None
        assert dep.disabled is False
        assert dep.own_income == Decimal(0)
        assert dep.dependent_from is None
        assert dep.dependent_until is None
        assert dep.allocation_pct == Decimal(100)
        assert dep.cohabiting is True
        assert dep.residency_eligibility is True

    def test_string_relationship_coerced(self) -> None:
        """The string value of a relationship is normalized to the member."""
        dep = Dependent(relationship="child", birth_date=_BORN)  # type: ignore[arg-type]
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
        with pytest.raises(InvalidInputError):
            Dependent(relationship=_SPOUSE, own_income=Decimal(-1))

    def test_child_without_birth_date_raises(self) -> None:
        """A child's age band is checked every month: the birth date is needed."""
        with pytest.raises(InvalidInputError, match="birth_date") as caught:
            Dependent(relationship=_CHILD)
        assert caught.value.field == "Dependent.birth_date"

    def test_interval_ending_before_it_starts_raises(self) -> None:
        """dependent_until must not precede dependent_from."""
        with pytest.raises(InvalidInputError) as caught:
            Dependent(
                relationship=_SPOUSE,
                dependent_from=date(2026, 5, 2),
                dependent_until=date(2026, 5, 1),
            )
        assert caught.value.field == "Dependent.dependent_until"

    def test_one_day_interval_accepted(self) -> None:
        """An interval of one day is valid."""
        day = date(2026, 5, 1)
        dep = Dependent(relationship=_SPOUSE, dependent_from=day, dependent_until=day)
        assert dep.dependency_months(2026) == frozenset({5})

    def test_datetime_bound_raises(self) -> None:
        """A datetime is not a date."""
        with pytest.raises(InvalidInputError, match="dependent_from"):
            Dependent(
                relationship=_SPOUSE,
                dependent_from=datetime(2026, 1, 1),  # noqa: DTZ001
            )

    def test_allocation_below_zero_raises(self) -> None:
        """allocation_pct must be >= 0."""
        with pytest.raises(InvalidInputError):
            Dependent(relationship=_CHILD, allocation_pct=Decimal(-1))

    def test_allocation_above_hundred_raises(self) -> None:
        """allocation_pct must be <= 100."""
        with pytest.raises(InvalidInputError):
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
        child = Dependent(relationship=_CHILD, birth_date=_BORN)
        fc = FamilyComposition(dependents=(child,))
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


class TestDependencyMonths:
    """Dependent.dependency_months: months the interval touches (c. 3)."""

    @pytest.mark.parametrize(
        ("start", "end", "months"),
        [
            (None, None, range(1, 13)),
            (date(2026, 6, 15), None, range(6, 13)),
            (None, date(2026, 3, 10), range(1, 4)),
            (date(2026, 6, 30), date(2026, 7, 1), range(6, 8)),
            (date(2025, 3, 1), date(2027, 2, 1), range(1, 13)),
            (date(2025, 3, 1), date(2025, 12, 31), range(0)),
            (date(2027, 1, 1), None, range(0)),
        ],
        ids=[
            "open",
            "from-mid-june",
            "until-mid-march",
            "two-days-across-months",
            "beyond-the-year",
            "before-the-year",
            "after-the-year",
        ],
    )
    def test_months_of_2026(
        self, start: date | None, end: date | None, months: range
    ) -> None:
        """Both the start and the end month count."""
        dep = Dependent(relationship=_SPOUSE, dependent_from=start, dependent_until=end)
        assert dep.dependency_months(2026) == frozenset(months)


def test_two_spouses_raise() -> None:
    """A worker has at most one spouse."""
    spouse = Dependent(relationship=_SPOUSE)
    with pytest.raises(InvalidInputError, match="at most one spouse"):
        FamilyComposition(dependents=(spouse, spouse))


class TestSoleParent:
    """FamilyComposition.sole_parent."""

    def test_defaults_to_false(self) -> None:
        """A family is not a sole-parent one unless declared."""
        assert FamilyComposition().sole_parent is False

    def test_sole_parent_with_spouse_raises(self) -> None:
        """A sole parent declares no spouse."""
        with pytest.raises(InvalidInputError) as caught:
            FamilyComposition(
                dependents=(Dependent(relationship=_SPOUSE),), sole_parent=True
            )
        assert caught.value.field == "FamilyComposition.sole_parent"

    def test_sole_parent_must_be_bool(self) -> None:
        """A non-bool flag is rejected."""
        with pytest.raises(InvalidInputError, match="sole_parent"):
            FamilyComposition(sole_parent=1)  # type: ignore[arg-type]
