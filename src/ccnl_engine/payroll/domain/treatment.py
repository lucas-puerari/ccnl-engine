"""Treatment decisions: typed accounting policy for variable work events."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["EventTreatment"]


@dataclass(frozen=True)
class EventTreatment:
    """Typed accounting policy for a variable work event.

    Each flag answers: does this event's gross amount contribute to the
    corresponding payroll axis?  The policy is evaluated once per event
    and the decision is applied uniformly, making the axis assignment
    explicit and auditable.

    ``inps`` covers both employee and employer contribution bases.
    ``tfr`` controls whether the amount enters the TFR accrual base
    (*retribuzione utile TFR* per art. 2120 c.c.).
    ``irpef`` controls whether the amount enters the IRPEF taxable base.

    Attributes:
        inps: Amount enters the INPS (employee + employer) contribution base.
        tfr: Amount enters the TFR accrual base.
        irpef: Amount enters the IRPEF taxable base.
    """

    inps: bool
    tfr: bool
    irpef: bool
