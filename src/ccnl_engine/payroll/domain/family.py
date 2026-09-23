"""Family domain models for Art. 12 TUIR deductions."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DependentRelationship(StrEnum):
    """Relationship category of a fiscally dependent family member."""

    SPOUSE = "spouse"
    CHILD = "child"
    ASCENDANT = "ascendant"


class Dependent(BaseModel):
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
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    relationship: DependentRelationship
    birth_date: date | None = None
    disabled: bool = False
    own_income: Decimal = Field(default=Decimal(0), ge=Decimal(0))
    months_dependent: int = Field(default=12, ge=1, le=12)
    allocation_pct: Decimal = Field(
        default=Decimal(100), ge=Decimal(0), le=Decimal(100)
    )
    cohabiting: bool = True
    residency_eligibility: bool = True


class FamilyComposition(BaseModel):
    """Caller-supplied family unit for Art. 12 TUIR deductions.

    Used to compute family deductions applied by the employer as
    *sostituto d'imposta*.  The engine uses ``taxable_income`` (gross minus
    INPS employee contributions) as a proxy for *reddito complessivo*.

    Computed deductions reduce ``irpef_net`` and therefore increase
    ``net_annual`` (unlike all other L3 features, which are informational
    only).  The scope status is ``"caller_declared"`` because eligibility
    conditions (residency, disability certification, dependent's full income)
    are declared by the caller and not engine-verified.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dependents: tuple[Dependent, ...] = ()

    @model_validator(mode="after")
    def _check_one_spouse(self) -> Self:
        spouses = [
            d for d in self.dependents if d.relationship == DependentRelationship.SPOUSE
        ]
        if len(spouses) > 1:
            msg = f"FamilyComposition accepts at most one spouse; got {len(spouses)}"
            raise ValueError(msg)
        return self

    @property
    def has_any_dependent(self) -> bool:
        """True when at least one dependent is declared."""
        return bool(self.dependents)
