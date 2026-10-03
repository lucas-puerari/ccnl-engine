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
    require_int,
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

    The caller declares the dependent; the engine uses the fields to determine
    eligibility and pro-rate the deduction.  Fields the engine cannot verify
    (residency, disability certification) are taken as declared.

    Attributes:
        relationship: Relationship to the worker.
        birth_date: Date of birth, used to determine age-based eligibility for
            children.  ``None`` means the caller has not supplied it; the engine
            treats the dependent as eligible (caller_declared).
        disabled: ``True`` when disability is certified under Legge 104/92.
        own_income: Dependent's own annual income (EUR).  Used to check the
            2840.51 EUR threshold for spouses and ascendants.
        months_dependent: Months of the tax year the dependent was fiscally
            dependent (1-12).  Used for pro-rata deduction.
        allocation_pct: Percentage of the deduction allocated to this worker
            (0-100).  Use 50 for shared-custody children; 100 otherwise.
        cohabiting: ``True`` when the ascendant lives with the worker.  Only
            relevant for ascendants (Art. 12 c. 1 lett. d post L. 207/2024).
        residency_eligibility: ``True`` when citizenship/residency conditions
            are met (Art. 12 c. 2-bis).  Caller-declared; not engine-verified.

    Raises:
        InvalidInputError: When a field is not of its type or is outside its
            range.
    """

    relationship: DependentRelationship
    birth_date: date | None = None
    disabled: bool = False
    own_income: Decimal = _ZERO
    months_dependent: int = 12
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
        require_date(
            self.birth_date, "Dependent.birth_date", feature=_FEATURE, optional=True
        )
        for name in ("disabled", "cohabiting", "residency_eligibility"):
            require_bool(getattr(self, name), f"Dependent.{name}", feature=_FEATURE)
        require_decimal(
            self.own_income, "Dependent.own_income", feature=_FEATURE, minimum=_ZERO
        )
        require_int(
            self.months_dependent,
            "Dependent.months_dependent",
            feature=_FEATURE,
            minimum=1,
            maximum=12,
        )
        require_decimal(
            self.allocation_pct,
            "Dependent.allocation_pct",
            feature=_FEATURE,
            minimum=_ZERO,
            maximum=_HUNDRED,
        )


@dataclass(frozen=True, slots=True)
class FamilyComposition:
    """Caller-supplied family unit for Art. 12 TUIR deductions.

    Used to compute family deductions applied by the employer as
    *sostituto d'imposta*.  The engine uses ``taxable_income`` (gross minus
    INPS employee contributions) as a proxy for *reddito complessivo*.

    Computed deductions reduce ``irpef_net`` and therefore increase
    ``net_annual`` (unlike all other L3 features, which are informational
    only).  A list of dependents is accepted and stored as a tuple.  The
    scope status is ``"caller_declared"`` because eligibility
    conditions (residency, disability certification, dependent's full income)
    are declared by the caller and not engine-verified.
    """

    dependents: tuple[Dependent, ...] = ()

    def __post_init__(self) -> None:
        """Validate every dependent and accept at most one spouse.

        Raises:
            InvalidInputError: When a dependent is not a :class:`Dependent`
                or more than one is a spouse.
        """
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

    @property
    def has_any_dependent(self) -> bool:
        """True when at least one dependent is declared."""
        return bool(self.dependents)
