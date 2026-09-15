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
    The resulting credit reduces ``irpef_net`` and therefore increases
    ``net_annual``.

    Unlike Art. 12 family deductions (which taper with income), Art. 15
    deductions are fixed-rate (19 %) credits on eligible expenditure up to
    statutory ceilings.

    Art. 1 c. 3-4 L. 199/2025 applies a EUR 440 reduction to the tax credit
    for oneri detraibili al 19% (Art. 1 c. 4 lett. a, which includes Art. 15
    c. 1 lett. b TUIR interessi su mutuo; spese sanitarie lett. c are
    explicitly excluded) when reddito complessivo exceeds EUR 200 000.

    Attributes:
        mortgage_interest: Interessi passivi su mutuo per l'acquisto
            dell'abitazione principale (Art. 15 c. 1 lett. b TUIR).
            Annual interest actually paid.  Capped at EUR 4 000 per
            household; deduction rate 19 % (max credit EUR 760).
            Must be >= 0.
        mortgage_pre_2022: True when the mortgage was stipulated on or
            before 31 December 2021.  Only mortgages contracted by that
            date count as qualifying Art. 15 deductions for the Trattamento
            integrativo (Art. 1 D.L. 3/2020); later mortgages reduce IRPEF
            but do not affect the TI relevant-deductions sum.
            Defaults to False (post-2021 / origin unknown).
    """

    mortgage_interest: Decimal = _ZERO
    mortgage_pre_2022: bool = False

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
