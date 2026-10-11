"""Contribution breakdown: per-component INPS audit trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

__all__ = ["ContributionBreakdown", "ContributionComponent"]


@dataclass(frozen=True)
class ContributionComponent:
    """One named component of the INPS contribution for a period.

    Attributes:
        name: Short identifier, e.g. ``"ivs_employee"``, ``"naspi_employer"``.
        base: The contribution base this rate was applied to (may be
            ceiling-capped for IVS components).
        rate: The rate applied to ``base``.
        amount: ``money(base * rate)`` — the contribution amount.
    """

    name: str
    base: Decimal
    rate: Decimal
    amount: Decimal


@dataclass(frozen=True)
class ContributionBreakdown:
    """Per-component INPS breakdown for one payroll period.

    ``employee`` and ``employer`` are the totals posted to the ledger
    (``EMPLOYEE_CONTRIBUTIONS`` and ``EMPLOYER_CONTRIBUTIONS`` respectively).
    ``components`` carries the per-rate detail for audit and compliance.

    Attributes:
        employee: Total employee INPS contribution for the period.
        employer: Total employer INPS contribution for the period.
        components: Per-component trace, ordered employee then employer.
    """

    employee: Decimal
    employer: Decimal
    components: tuple[ContributionComponent, ...]
