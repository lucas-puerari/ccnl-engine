"""Family domain models for Art. 12 TUIR deductions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    parse_enum,
    require_bool,
    require_date,
    require_decimal,
)

_FEATURE = "family_deductions"
_ZERO = Decimal(0)
_HUNDRED = Decimal(100)


class DependentRelationship(StrEnum):
    """Relationship category of a fiscally dependent family member."""

    SPOUSE = "spouse"
    CHILD = "child"
    ASCENDANT = "ascendant"


@dataclass(frozen=True, slots=True)
class Dependent:
    """One fiscally dependent family member for Art. 12 TUIR purposes.

    The caller declares the dependent and the dated interval in which the
    conditions it cannot verify hold (marriage, cohabitation, residency,
    custody); the engine derives from it, month by month, the months the
    deduction is due (art. 12 c. 3: "rapportate a mese e competono dal mese
    in cui si sono verificate a quello in cui sono cessate le condizioni
    richieste") and, for a child, the months of the age band.

    Attributes:
        relationship: Relationship to the worker.
        birth_date: Date of birth.  Required for a child: the age band of
            lett. c is evaluated in every month.  Ignored for a spouse or an
            ascendant.
        disabled: ``True`` when a disability is certified under art. 3
            L. 104/1992; a child keeps the deduction from the age of 30.
        own_income: Dependent's own reddito complessivo of the year (EUR),
            checked against the limit of art. 12 c. 2.
        dependent_from: First day the conditions hold; ``None`` for since
            before the tax year.
        dependent_until: Last day the conditions hold; ``None`` for
            beyond the tax year.
        allocation_pct: Percentage of the deduction allocated to this worker
            (0-100).  Use 50 for a child shared between the parents.
        cohabiting: ``True`` when the ascendant lives with the worker.  Only
            relevant for ascendants (Art. 12 c. 1 lett. d post L. 207/2024).
        residency_eligibility: ``True`` when citizenship/residency conditions
            are met (Art. 12 c. 2-bis).  Caller-declared; not engine-verified.

    Raises:
        InvalidInputError: When a field is not of its type or is outside its
            range, a child has no birth date, or the interval ends before
            it starts.
    """

    relationship: DependentRelationship
    birth_date: date | None = None
    disabled: bool = False
    own_income: Decimal = _ZERO
    dependent_from: date | None = None
    dependent_until: date | None = None
    allocation_pct: Decimal = _HUNDRED
    cohabiting: bool = True
    residency_eligibility: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        relationship = parse_enum(
            self.relationship,
            DependentRelationship,
            "Dependent.relationship",
            feature=_FEATURE,
        )
        object.__setattr__(self, "relationship", relationship)
        for name in ("birth_date", "dependent_from", "dependent_until"):
            require_date(
                getattr(self, name),
                f"Dependent.{name}",
                feature=_FEATURE,
                optional=True,
            )
        for name in ("disabled", "cohabiting", "residency_eligibility"):
            require_bool(getattr(self, name), f"Dependent.{name}", feature=_FEATURE)
        require_decimal(
            self.own_income, "Dependent.own_income", feature=_FEATURE, minimum=_ZERO
        )
        require_decimal(
            self.allocation_pct,
            "Dependent.allocation_pct",
            feature=_FEATURE,
            minimum=_ZERO,
            maximum=_HUNDRED,
        )
        self._check_dates()

    def _check_dates(self) -> None:
        child = self.relationship is DependentRelationship.CHILD
        if child and self.birth_date is None:
            msg = "a child needs its birth_date: the age band is checked every month"
            raise InvalidInputError(msg, field="Dependent.birth_date", feature=_FEATURE)
        start, end = self.dependent_from, self.dependent_until
        if start is not None and end is not None and end < start:
            msg = f"dependent_until {end} is before dependent_from {start}"
            raise InvalidInputError(
                msg, field="Dependent.dependent_until", feature=_FEATURE
            )

    def dependency_months(self, year: int) -> frozenset[int]:
        """Return the months of ``year`` the conditions hold on some day.

        Returns:
            Months 1-12 the interval touches, both ends included (c. 3).
        """
        start, end = self.dependent_from, self.dependent_until
        first = 1 if start is None else _month_index(start, year)
        last = 12 if end is None else _month_index(end, year)
        return frozenset(range(max(first, 1), min(last, 12) + 1))


def _month_index(day: date, year: int) -> int:
    """Return the month of ``day`` counted from January of ``year`` as 1.

    Returns:
        ``0`` or less before ``year``, ``13`` or more after it.
    """
    return (day.year - year) * 12 + day.month


@dataclass(frozen=True, slots=True)
class FamilyComposition:
    """Caller-supplied family unit for Art. 12 TUIR deductions.

    Used to compute the family deductions the employer applies as
    *sostituto d'imposta*, on the reddito complessivo of
    :class:`~ccnl_engine.payroll.domain.current_year.CurrentYearTaxFacts`.
    Eligibility conditions the engine cannot verify (residency, disability
    certification, the dependents' own income) are taken as declared.

    Attributes:
        dependents: The dependents; a list is accepted and stored as a
            tuple.
        sole_parent: ``True`` when the other parent is missing or has not
            recognized the children, or the children are the worker's
            alone, and the worker is not married or is legally separated:
            for the first child the spouse deduction of lett. a applies
            when more favourable (art. 12 c. 1 lett. c, last period).
    """

    dependents: tuple[Dependent, ...] = ()
    sole_parent: bool = False

    def __post_init__(self) -> None:
        """Validate every dependent and accept at most one spouse.

        Raises:
            InvalidInputError: When a dependent is not a :class:`Dependent`,
                more than one is a spouse, or a sole parent declares a
                spouse.
        """
        require_bool(
            self.sole_parent, "FamilyComposition.sole_parent", feature=_FEATURE
        )
        dependents = tuple_of(
            self.dependents,
            "FamilyComposition.dependents",
            items_of_type(Dependent, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "dependents", dependents)
        spouses = [
            d for d in dependents if d.relationship == DependentRelationship.SPOUSE
        ]
        if len(spouses) > 1:
            msg = f"FamilyComposition accepts at most one spouse; got {len(spouses)}"
            raise InvalidInputError(
                msg, field="FamilyComposition.dependents", feature=_FEATURE
            )
        if spouses and self.sole_parent:
            msg = "a sole parent declares no spouse (art. 12 c. 1 lett. c)"
            raise InvalidInputError(
                msg, field="FamilyComposition.sole_parent", feature=_FEATURE
            )

    @property
    def has_any_dependent(self) -> bool:
        """True when at least one dependent is declared."""
        return bool(self.dependents)
