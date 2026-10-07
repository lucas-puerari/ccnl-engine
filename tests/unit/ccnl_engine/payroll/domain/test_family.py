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


def _dep(relationship: DependentRelationship, **fields: object) -> Dependent:
    """Return a dependant over an open interval, other fields as given.

    Returns:
        The dependant.
    """
    interval: dict[str, object] = {"dependent_from": None, "dependent_until": None}
    return Dependent(relationship, **{**interval, **fields})  # type: ignore[arg-type]


class TestDependentDefaults:
    """Dependent — default field values."""

    def test_conditions_default_to_unknown(self) -> None:
        """Every condition of art. 12 defaults to None: unknown, not met."""
        dep = _dep(_SPOUSE)
        assert dep.birth_date is None
        assert dep.disabled is False
        assert dep.own_income is None
        assert dep.allocation_pct is None
        assert dep.cohabiting is None
        assert dep.residency_eligibility is None

    def test_interval_is_required(self) -> None:
        """The dependency interval has no default: None is an open end."""
        with pytest.raises(TypeError, match="dependent_until"):
            Dependent(_SPOUSE, dependent_from=None)  # type: ignore[call-arg]

    def test_string_relationship_coerced(self) -> None:
        """The string value of a relationship is normalized to the member."""
        dep = _dep("child", birth_date=_BORN)  # type: ignore[arg-type]
        assert dep.relationship == _CHILD

    def test_birth_date_accepted(self) -> None:
        """birth_date is stored as-is when supplied."""
        d = date(2000, 6, 15)
        dep = _dep(_CHILD, birth_date=d)
        assert dep.birth_date == d


class TestMissingFacts:
    """Dependent.missing_facts: the unknown conditions art. 12 reads."""

    @pytest.mark.parametrize(
        ("relationship", "facts"),
        [
            (_SPOUSE, ("own_income", "residency_eligibility")),
            (_CHILD, ("own_income", "allocation_pct", "residency_eligibility")),
            (
                _ASCENDANT,
                ("own_income", "allocation_pct", "cohabiting", "residency_eligibility"),
            ),
        ],
    )
    def test_unknown_conditions_by_relationship(
        self, relationship: DependentRelationship, facts: tuple[str, ...]
    ) -> None:
        """C. 2 and c. 2-bis for all; the share for lett. c and d; lett. d cohabits."""
        assert _dep(relationship, birth_date=_BORN).missing_facts == facts

    def test_stated_conditions_leave_nothing_missing(self) -> None:
        """A stated False is a fact, not a missing one."""
        dep = _dep(
            _ASCENDANT,
            own_income=Decimal(0),
            allocation_pct=Decimal(0),
            cohabiting=False,
            residency_eligibility=False,
        )
        assert dep.missing_facts == ()


class TestMayQualify:
    """Dependent.may_qualify: no stated condition excludes the deduction."""

    _LIMIT = Decimal("2840.51")

    def test_unknown_conditions_do_not_exclude(self) -> None:
        """Unknown is not a stated failure."""
        assert _dep(_ASCENDANT).may_qualify(self._LIMIT)

    @pytest.mark.parametrize(
        "fields",
        [
            {"residency_eligibility": False},
            {"cohabiting": False},
            {"own_income": Decimal("2840.52")},
        ],
        ids=["not-resident", "not-cohabiting", "above-limit"],
    )
    def test_stated_failure_excludes(self, fields: dict[str, object]) -> None:
        """Each stated failure excludes an ascendant."""
        assert not _dep(_ASCENDANT, **fields).may_qualify(self._LIMIT)

    def test_cohabitation_not_read_for_a_spouse(self) -> None:
        """A spouse stated not cohabiting is not excluded by lett. d."""
        spouse = _dep(_SPOUSE, cohabiting=False, own_income=self._LIMIT)
        assert spouse.may_qualify(self._LIMIT)


class TestShare:
    """Dependent.share and the spouse deduction, which is not shared."""

    def test_unknown_share_reads_as_whole(self) -> None:
        """The whole deduction when no share is stated (a spouse's case)."""
        assert _dep(_SPOUSE).share == Decimal(100)

    def test_stated_share(self) -> None:
        """A stated share is used as is."""
        child = _dep(_CHILD, birth_date=_BORN, allocation_pct=Decimal(50))
        assert child.share == Decimal(50)

    def test_spouse_whole_share_accepted(self) -> None:
        """100 for a spouse states the only possible share."""
        assert _dep(_SPOUSE, allocation_pct=Decimal(100)).share == Decimal(100)

    def test_spouse_partial_share_raises(self) -> None:
        """Lett. a has no split between spouses."""
        with pytest.raises(InvalidInputError, match="not shared") as caught:
            _dep(_SPOUSE, allocation_pct=Decimal(50))
        assert caught.value.field == "Dependent.allocation_pct"


class TestDependentValidation:
    """Dependent — field constraints."""

    def test_negative_own_income_raises(self) -> None:
        """own_income must be >= 0."""
        with pytest.raises(InvalidInputError):
            _dep(_SPOUSE, own_income=Decimal(-1))

    def test_child_without_birth_date_raises(self) -> None:
        """A child's age band is checked every month: the birth date is needed."""
        with pytest.raises(InvalidInputError, match="birth_date") as caught:
            _dep(_CHILD)
        assert caught.value.field == "Dependent.birth_date"

    def test_interval_ending_before_it_starts_raises(self) -> None:
        """dependent_until must not precede dependent_from."""
        with pytest.raises(InvalidInputError) as caught:
            _dep(
                relationship=_SPOUSE,
                dependent_from=date(2026, 5, 2),
                dependent_until=date(2026, 5, 1),
            )
        assert caught.value.field == "Dependent.dependent_until"

    def test_one_day_interval_accepted(self) -> None:
        """An interval of one day is valid."""
        day = date(2026, 5, 1)
        dep = _dep(_SPOUSE, dependent_from=day, dependent_until=day)
        assert dep.dependency_months(2026) == frozenset({5})

    def test_datetime_bound_raises(self) -> None:
        """A datetime is not a date."""
        with pytest.raises(InvalidInputError, match="dependent_from"):
            _dep(
                relationship=_SPOUSE,
                dependent_from=datetime(2026, 1, 1),  # noqa: DTZ001
            )

    def test_allocation_below_zero_raises(self) -> None:
        """allocation_pct must be >= 0."""
        with pytest.raises(InvalidInputError):
            _dep(_CHILD, allocation_pct=Decimal(-1))

    def test_allocation_above_hundred_raises(self) -> None:
        """allocation_pct must be <= 100."""
        with pytest.raises(InvalidInputError):
            _dep(_CHILD, allocation_pct=Decimal(101))

    @pytest.mark.parametrize("name", ["cohabiting", "residency_eligibility"])
    def test_non_bool_condition_raises(self, name: str) -> None:
        """A condition is True, False or None (unknown)."""
        with pytest.raises(InvalidInputError) as caught:
            _dep(_ASCENDANT, **{name: 1})
        assert caught.value.field == f"Dependent.{name}"

    def test_frozen(self) -> None:
        """Dependent is frozen and cannot be mutated."""
        dep = _dep(_SPOUSE)
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
        fc = FamilyComposition(dependents=(_dep(_SPOUSE),))
        assert fc.has_any_dependent is True

    def test_child_sets_flag(self) -> None:
        """One child dependent → has_any_dependent True."""
        child = _dep(_CHILD, birth_date=_BORN)
        fc = FamilyComposition(dependents=(child,))
        assert fc.has_any_dependent is True

    def test_ascendant_sets_flag(self) -> None:
        """One ascendant dependent → has_any_dependent True."""
        fc = FamilyComposition(dependents=(_dep(_ASCENDANT),))
        assert fc.has_any_dependent is True

    def test_empty_dependents_false(self) -> None:
        """Empty tuple → has_any_dependent False."""
        assert FamilyComposition(dependents=()).has_any_dependent is False

    def test_frozen(self) -> None:
        """FamilyComposition is frozen and cannot be mutated."""
        fc = FamilyComposition(dependents=(_dep(_SPOUSE),))
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
        dep = _dep(_SPOUSE, dependent_from=start, dependent_until=end)
        assert dep.dependency_months(2026) == frozenset(months)


def test_two_spouses_raise() -> None:
    """A worker has at most one spouse."""
    spouse = _dep(_SPOUSE)
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
            FamilyComposition(dependents=(_dep(_SPOUSE),), sole_parent=True)
        assert caught.value.field == "FamilyComposition.sole_parent"

    def test_sole_parent_must_be_bool(self) -> None:
        """A non-bool flag is rejected."""
        with pytest.raises(InvalidInputError, match="sole_parent"):
            FamilyComposition(sole_parent=1)  # type: ignore[arg-type]
