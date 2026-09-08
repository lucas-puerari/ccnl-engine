"""FamilyComposition — caller-supplied family unit for Art. 12 TUIR deductions."""

from __future__ import annotations

from dataclasses import dataclass

_ZERO = 0


@dataclass(frozen=True)
class FamilyComposition:
    """Composition of the worker's fiscally dependent family unit.

    Used to compute Art. 12 TUIR deductions applied by the employer as
    *sostituto d'imposta*.  The engine uses ``gross_annual`` from the payroll
    chain as a proxy for *reddito complessivo* (other income sources are not
    modelled — this is a documented simplification).

    Computed deductions reduce ``irpef_net`` and therefore ``net_annual``
    (unlike all other L3 features, which are informational only).

    Attributes:
        spouse_dependent: ``True`` when the worker's spouse (or civil partner)
            is fiscally dependent (own income <= EUR 2840.51).  Triggers the
            Art. 12 c. 1 lett. a deduction.
        children_21_or_older: Number of eligible children aged 21 or older.
            Children under 21 are covered by Assegno Unico Universale
            (D.Lgs. 230/2021 from 2022-03-01) and are NOT eligible.
        children_21_or_older_disabled: Number of eligible children aged 21
            or older with certified disability (Legge 104/92).  These receive
            a higher deduction (``disabled_amount`` from the rules file).
        ascendenti_conviventi: Number of fiscally dependent ascendants
            (parents, grandparents) living with the taxpayer.  Post L. 207/2024
            only ascendants qualify; other relatives no longer do.

    Note:
        All counts default to zero.  Pass at least one non-default value to
        trigger a deduction computation.
    """

    spouse_dependent: bool = False
    children_21_or_older: int = 0
    children_21_or_older_disabled: int = 0
    ascendenti_conviventi: int = 0

    def __post_init__(self) -> None:
        """Validate that all counts are non-negative.

        Raises:
            ValueError: If any count field is negative.
        """
        for name in (
            "children_21_or_older",
            "children_21_or_older_disabled",
            "ascendenti_conviventi",
        ):
            if getattr(self, name) < _ZERO:
                msg = f"{name} must be >= 0, got {getattr(self, name)}"
                raise ValueError(msg)

    @property
    def total_eligible_children(self) -> int:
        """Total number of eligible children (standard + disabled)."""
        return self.children_21_or_older + self.children_21_or_older_disabled

    @property
    def has_any_dependent(self) -> bool:
        """True when at least one dependent triggers a deduction."""
        return (
            self.spouse_dependent
            or self.total_eligible_children > 0
            or self.ascendenti_conviventi > 0
        )
