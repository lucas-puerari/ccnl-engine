"""Monetary rounding policy for payroll computations.

The canonical policy is :data:`MONETARY`: two decimal places, ROUND_HALF_UP,
applied at the monetary stage (rate multiplications, bracket calculations).
Pure additions and subtractions of already-rounded amounts do not re-round.

``money()`` is retained as a thin alias so every call site stays untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class RoundingPolicy:
    """Encapsulates a decimal rounding policy: precision, mode, and stage.

    Attributes:
        precision: Smallest unit to round to (e.g. ``Decimal("0.01")``).
        mode: Python decimal rounding mode string (e.g. ``ROUND_HALF_UP``).
        stage: Computation stage where this policy applies (e.g.
            ``"monetary"``).
    """

    precision: Decimal
    mode: str
    stage: str

    def apply(self, x: Decimal) -> Decimal:
        """Round *x* to :attr:`precision` using :attr:`mode`.

        Returns:
            *x* rounded according to this policy.
        """
        return x.quantize(self.precision, rounding=self.mode)

    def __str__(self) -> str:
        """Return a human-readable descriptor, e.g. ``"ROUND_HALF_UP 0.01"``.

        Returns:
            The string ``"{mode} {precision}"``.
        """
        return f"{self.mode} {self.precision}"


#: Canonical monetary rounding: two decimal places, ROUND_HALF_UP.
#: Applied whenever a rate multiplication or bracket calculation produces a
#: sub-cent value that must be settled before the next derivation step.
MONETARY = RoundingPolicy(
    precision=Decimal("0.01"),
    mode=ROUND_HALF_UP,
    stage="monetary",
)


def money(x: Decimal) -> Decimal:
    """Round *x* to two decimal places using ROUND_HALF_UP.

    Delegates to :data:`MONETARY` — the canonical monetary rounding policy.

    Returns:
        *x* rounded to two decimal places.
    """
    return MONETARY.apply(x)
