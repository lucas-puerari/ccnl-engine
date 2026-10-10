"""Eligibility facts: the contribution history and prior-year income."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.validation import require_bool, require_date

__all__ = [
    "CONTRIBUTORY_COHORT_START",
    "ContributionHistory",
    "IvsCeilingBasis",
    "PriorYearFacts",
]

#: First day of the cohort subject to the IVS massimale: workers without
#: contributions before this date (L. 335/1995 art. 2 c. 18).
CONTRIBUTORY_COHORT_START = date(1996, 1, 1)


class IvsCeilingBasis(StrEnum):
    """Reason codes of the IVS massimale eligibility of a worker.

    Attributes:
        FIRST_ENROLMENT_AFTER_1995: First contribution on or after
            1 January 1996: the massimale applies.
        CONTRIBUTORY_OPTION: The worker opted for the contributory system
            (L. 335/1995 art. 1 c. 23): the massimale applies.
        ENROLLED_BEFORE_1996: Contributions before 1 January 1996 and no
            option: the massimale does not apply.
    """

    FIRST_ENROLMENT_AFTER_1995 = "first_enrolment_after_1995"
    CONTRIBUTORY_OPTION = "contributory_option"
    ENROLLED_BEFORE_1996 = "enrolled_before_1996"


@dataclass(frozen=True)
class ContributionHistory:
    """The pension history that decides whether the IVS massimale applies.

    L. 335/1995 art. 2 c. 18 caps the IVS contribution base at an annual
    massimale (EUR 122,295 in 2026) for workers without contributions
    before 1 January 1996 and for those who opted for the contributory
    system under art. 1 c. 23.  Every other worker contributes on the full
    base.  The engine derives the eligibility from these facts; the caller
    never states it.

    The history is the one in force for the run being computed: the engine
    models no effective date of a change.  Pre-1996 periods credited on
    request to a worker hired after 1995 lift the massimale only from the
    month after the request (L. 208/2015 art. 1 c. 280), and the option
    takes effect from when it is exercised: for the runs before those
    dates, supply the history as it stood then.

    Attributes:
        first_enrolled_on: Date of the first contribution credited to any
            mandatory pension scheme (prima iscrizione), from the worker's
            contribution statement.
        contributory_option: Whether the worker opted for the contributory
            system (L. 335/1995 art. 1 c. 23).  Defaults to ``False``.

    Raises:
        InvalidInputError: When a field is not of its type.
    """

    first_enrolled_on: date
    contributory_option: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        feature = "contribution_history"
        require_date(
            self.first_enrolled_on,
            "ContributionHistory.first_enrolled_on",
            feature=feature,
        )
        require_bool(
            self.contributory_option,
            "ContributionHistory.contributory_option",
            feature=feature,
        )

    @property
    def ivs_ceiling_basis(self) -> IvsCeilingBasis:
        """Why the massimale applies to the worker or not."""
        if self.contributory_option:
            return IvsCeilingBasis.CONTRIBUTORY_OPTION
        if self.first_enrolled_on >= CONTRIBUTORY_COHORT_START:
            return IvsCeilingBasis.FIRST_ENROLMENT_AFTER_1995
        return IvsCeilingBasis.ENROLLED_BEFORE_1996

    @property
    def ivs_ceiling_applies(self) -> bool:
        """Whether the annual IVS massimale caps the contribution base."""
        return self.ivs_ceiling_basis is not IvsCeilingBasis.ENROLLED_BEFORE_1996


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
