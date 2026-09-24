"""Eligibility facts and contribution ceiling status for payroll calculations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

__all__ = ["ContributionCeilingStatus", "PriorYearFacts"]


class ContributionCeilingStatus(StrEnum):
    """Whether the IVS massimale ceiling applies to this worker.

    Determines whether the annual contribution ceiling (massimale retributivo
    IVS, Art. 2 D. Lgs. 181/1997) is applied when resolving INPS contributions.

    Pass ``POST_1995`` or ``OPTED_IN`` to cap contributions at the annual
    massimale.  ``NOT_APPLICABLE`` skips the cap (pre-1996 enrollment).
    ``UNKNOWN`` is the safe default: the ceiling is not applied to avoid
    over-deducting when the caller has not provided the worker's enrollment
    status.
    """

    NOT_APPLICABLE = "not_applicable"
    POST_1995 = "post_1995"
    OPTED_IN = "opted_in"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PriorYearFacts:
    """Prior-year income facts required for income-tested eligibility checks.

    Used to determine eligibility for substitute-tax regimes that depend on
    the worker's prior-year reddito complessivo (e.g. L. 199/2025 art. 1
    commi 7-12: 5% rate for contract-renewal increments with 2025 income
    ≤ EUR 33 000; 15% for night/shift supplements with 2025 income ≤ EUR 40 000).

    Attributes:
        reddito_complessivo: Worker's prior-year reddito complessivo in EUR.
            Sourced from the CU (Certificazione Unica) or the prior-year
            tax return.  ``None`` means unknown; the engine will apply the
            most conservative treatment (ordinary IRPEF).
    """

    reddito_complessivo: Decimal | None = None
