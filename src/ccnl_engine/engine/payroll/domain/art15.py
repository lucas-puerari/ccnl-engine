"""Art15Deductions — caller-supplied oneri detraibili (Art. 15 TUIR)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_ZERO = Decimal(0)


@dataclass(frozen=True)
class Art15Deductions:
    """Oneri detraibili declared by the worker (Art. 15 TUIR).

    The employer (*sostituto d'imposta*) applies these deductions against
    the IRPEF withheld when the worker provides supporting documentation.
    The resulting credit reduces ``irpef_net`` and therefore ``net_annual``.

    Unlike Art. 12 family deductions (which taper with income), Art. 15
    deductions are fixed-rate (19 %) credits on eligible expenditure up to
    statutory ceilings.

    Art. 1 c. 3-4 L. 199/2025 sterilizzazione does NOT apply to Art. 15:
    the EUR 440 clawback targets only Art. 12 + Art. 13 TUIR (it is the
    exact compensation for the 35 % → 33 % bracket rate change, unrelated
    to Art. 15 oneri).

    Attributes:
        mortgage_interest: Interessi passivi su mutuo per l'acquisto
            dell'abitazione principale (Art. 15 c. 1 lett. b TUIR).
            Annual interest actually paid.  Capped at EUR 4 000 per
            household; deduction rate 19 % (max credit EUR 760).
            Must be >= 0.
    """

    mortgage_interest: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that mortgage_interest is non-negative.

        Raises:
            ValueError: If mortgage_interest is negative.
        """
        if self.mortgage_interest < _ZERO:
            msg = f"mortgage_interest must be >= 0, got {self.mortgage_interest}"
            raise ValueError(msg)

    @property
    def has_any_onere(self) -> bool:
        """True when at least one Art. 15 item is non-zero."""
        return self.mortgage_interest > _ZERO
