"""Seniority and RAL-override helper types for payroll input models.

The top-level input types (:class:`~ccnl_engine.engine.payroll.domain\
.scenario.Employee`, :class:`~ccnl_engine.engine.payroll.domain.scenario\
.Employer`, :class:`~ccnl_engine.engine.payroll.domain.scenario.Employment`,
:class:`~ccnl_engine.engine.payroll.domain.scenario.PayrollScenario`) live
in :mod:`ccnl_engine.engine.payroll.domain.scenario`.

This module retains only the discriminated-union helpers that those top-level
types reference:

- :class:`SeniorityByCount` / :class:`SeniorityByMonths` / :class:`SeniorityByDate`
- :class:`RalOverride` / :class:`DestinationRalOverride`
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

_ZERO: Decimal = Decimal(0)


# ---------------------------------------------------------------------------
# Seniority discriminated union
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SeniorityByCount:
    """Seniority expressed as an explicit number of *scatti* already accrued.

    Use this when you know the exact increment count. Mutually exclusive with
    :class:`SeniorityByMonths` — the union makes it impossible to supply both.

    Attributes:
        value: Number of seniority increments accrued. Must be ``>= 0``.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that value is non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if self.value < 0:
            msg = f"SeniorityByCount.value must be >= 0, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class SeniorityByMonths:
    """Seniority expressed as months of service elapsed.

    The engine derives the increment count from the CCNL cadence rules.
    Use this when you track tenure in months rather than counting *scatti*
    manually. Mutually exclusive with :class:`SeniorityByCount`.

    Attributes:
        value: Months of continuous service elapsed. Must be ``>= 0``.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that value is non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if self.value < 0:
            msg = f"SeniorityByMonths.value must be >= 0, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class SeniorityByDate:
    """Seniority expressed as a hire or service-start date.

    The engine derives months of service from the gap between this date and
    :attr:`~ccnl_engine.engine.payroll.domain.scenario.Employment\
.calculation_date`, then applies the CCNL cadence rules to arrive at an
    increment count.

    Use this when you track the worker's hire date rather than months or
    increment count directly.

    Attributes:
        value: Hire date or continuous-service start date.
    """

    value: date


#: Union of all seniority input strategies.
Seniority = SeniorityByCount | SeniorityByMonths | SeniorityByDate


# ---------------------------------------------------------------------------
# RAL-override discriminated union
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RalOverride:
    """Replace the CCNL-derived gross annual salary with a fixed agreed value.

    Valid for any employment type. The value is used as-is (not scaled by
    the part-time coefficient). Mutually exclusive with
    :class:`DestinationRalOverride`.

    Attributes:
        value: Agreed annual salary in euros. Must be ``> 0``.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that value is positive.

        Raises:
            ValueError: If value is zero or negative.
        """
        if self.value <= _ZERO:
            msg = f"RalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class DestinationRalOverride:
    """Destination-level RAL for a percentage-track apprentice.

    The engine applies the apprenticeship percentage to this value to produce
    the apprentice's actual pay. Only valid for
    :class:`~ccnl_engine.engine.payroll.domain.employment.Apprentice`
    employment on a percentage track. Mutually exclusive with
    :class:`RalOverride`.

    Attributes:
        value: Destination-level annual salary in euros. Must be ``> 0``.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that value is positive.

        Raises:
            ValueError: If value is zero or negative.
        """
        if self.value <= _ZERO:
            msg = f"DestinationRalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)


#: Union of the two RAL-override strategies.
RalOverrideMode = RalOverride | DestinationRalOverride
