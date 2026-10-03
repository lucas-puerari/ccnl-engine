"""Employer domain types: headcount value object and employer profile."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.shared.domain.validation import (
    parse_enum,
    require_instance,
    require_int,
)
from ccnl_engine.tax.domain.preferential_regime import EmployerActivity

__all__ = ["EmployerActivity", "EmployerProfile", "Headcount"]

_FEATURE = "employer"


@dataclass(frozen=True, slots=True)
class Headcount:
    """Employer headcount used to select INPS contribution tiers.

    At least one: the worker being paid is an employee of the employer.

    Attributes:
        value: Number of employees, ``>= 1``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is below 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.value, "Headcount.value", feature=_FEATURE, minimum=1)


@dataclass(frozen=True, slots=True)
class EmployerProfile:
    """The employer of the worker being paid.

    The only employer model of the payroll pipeline.  The INPS
    classification of the employer follows from the CCNL, so the headcount
    is the only contribution fact the employer declares.

    Attributes:
        headcount: Employer headcount, used to select the INPS contribution
            tier.  Required: no size is assumed.
        activity: Activity of the employer, for the regimes that exclude
            some activities.  ``None`` means not known: the night, holiday
            and shift substitute tax (L. 199/2025 art. 1 c. 11) excludes the
            activities of c. 18, so its eligibility is then ``unknown``.

    Raises:
        InvalidInputError: When ``headcount`` is not a :class:`Headcount` or
            ``activity`` is not an :class:`EmployerActivity` value.
    """

    headcount: Headcount
    activity: EmployerActivity | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_instance(
            self.headcount, Headcount, "EmployerProfile.headcount", feature=_FEATURE
        )
        if self.activity is not None:
            activity = parse_enum(
                self.activity,
                EmployerActivity,
                "EmployerProfile.activity",
                feature=_FEATURE,
            )
            object.__setattr__(self, "activity", activity)
