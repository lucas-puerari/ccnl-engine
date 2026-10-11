"""Benefit breakdown: per-axis audit trace for fringe and welfare benefits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

__all__ = ["BenefitBreakdown"]


@dataclass(frozen=True)
class BenefitBreakdown:
    """Per-axis breakdown of benefit amounts for one payroll period.

    Captures the economic value, cash payout and tax/contribution bases
    separately so that reconciliation, audit and cost-centre reporting can
    each use the appropriate figure.

    Attributes:
        value: Total economic value of the benefits (fringe + welfare).
        cash: Cash amount paid out (zero for purely non-cash benefits).
        irpef_base: IRPEF-liable portion of the benefit value.
        inps_base: INPS-liable portion of the benefit value.
        employer_cost: Total cost to the employer (equals ``value``).
    """

    value: Decimal
    cash: Decimal
    irpef_base: Decimal
    inps_base: Decimal
    employer_cost: Decimal
