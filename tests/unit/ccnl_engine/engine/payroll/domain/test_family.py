"""Unit tests for FamilyComposition domain model."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.payroll.domain.family import FamilyComposition


class TestFamilyCompositionDefaults:
    """FamilyComposition — default values and zero-state."""

    def test_default_all_zero(self) -> None:
        """All numeric fields default to zero; spouse defaults to False."""
        fc = FamilyComposition()
        assert fc.spouse_dependent is False
        assert fc.children_21_or_older == 0
        assert fc.children_21_or_older_disabled == 0
        assert fc.ascendenti_conviventi == 0

    def test_has_any_dependent_false_by_default(self) -> None:
        """has_any_dependent is False when all fields are at their defaults."""
        assert FamilyComposition().has_any_dependent is False

    def test_total_eligible_children_zero_by_default(self) -> None:
        """total_eligible_children is zero when no children are set."""
        assert FamilyComposition().total_eligible_children == 0


class TestFamilyCompositionValidation:
    """FamilyComposition — validation at construction time."""

    def test_children_negative_raises(self) -> None:
        """Negative children_21_or_older raises ValueError."""
        with pytest.raises(ValueError, match="children_21_or_older must be >= 0"):
            FamilyComposition(children_21_or_older=-1)

    def test_disabled_negative_raises(self) -> None:
        """Negative children_21_or_older_disabled raises ValueError."""
        with pytest.raises(
            ValueError, match="children_21_or_older_disabled must be >= 0"
        ):
            FamilyComposition(children_21_or_older_disabled=-1)

    def test_ascendenti_negative_raises(self) -> None:
        """Negative ascendenti_conviventi raises ValueError."""
        with pytest.raises(ValueError, match="ascendenti_conviventi must be >= 0"):
            FamilyComposition(ascendenti_conviventi=-1)

    def test_all_positive_accepted(self) -> None:
        """All positive values construct without error."""
        fc = FamilyComposition(
            spouse_dependent=True,
            children_21_or_older=2,
            children_21_or_older_disabled=1,
            ascendenti_conviventi=1,
        )
        assert fc.spouse_dependent is True
        assert fc.children_21_or_older == 2


class TestFamilyCompositionProperties:
    """FamilyComposition — derived properties."""

    def test_total_eligible_children_sum(self) -> None:
        """total_eligible_children sums standard and disabled children."""
        fc = FamilyComposition(children_21_or_older=2, children_21_or_older_disabled=1)
        assert fc.total_eligible_children == 3

    def test_has_any_dependent_spouse(self) -> None:
        """has_any_dependent is True when spouse_dependent is True."""
        assert FamilyComposition(spouse_dependent=True).has_any_dependent is True

    def test_has_any_dependent_children(self) -> None:
        """has_any_dependent is True when children_21_or_older > 0."""
        assert FamilyComposition(children_21_or_older=1).has_any_dependent is True

    def test_has_any_dependent_disabled(self) -> None:
        """has_any_dependent is True when children_21_or_older_disabled > 0."""
        assert (
            FamilyComposition(children_21_or_older_disabled=1).has_any_dependent is True
        )

    def test_has_any_dependent_ascendenti(self) -> None:
        """has_any_dependent is True when ascendenti_conviventi > 0."""
        assert FamilyComposition(ascendenti_conviventi=1).has_any_dependent is True

    def test_has_any_dependent_all_zero(self) -> None:
        """has_any_dependent is False when all fields are explicitly zero."""
        fc = FamilyComposition(
            spouse_dependent=False,
            children_21_or_older=0,
            children_21_or_older_disabled=0,
            ascendenti_conviventi=0,
        )
        assert fc.has_any_dependent is False

    def test_frozen_cannot_mutate(self) -> None:
        """FamilyComposition is frozen and cannot be mutated after creation."""
        fc = FamilyComposition(children_21_or_older=1)
        with pytest.raises((AttributeError, TypeError)):
            fc.children_21_or_older = 2  # type: ignore[misc]
