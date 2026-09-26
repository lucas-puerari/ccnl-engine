"""Employer domain types: headcount value object and employer profile."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.tax.domain.preferential_regime import EmployerActivity

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
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            msg = f"headcount must be an int; got {self.value!r}"
            raise InvalidInputError(msg, feature=_FEATURE)
        if self.value < 1:
            msg = f"headcount must be >= 1; got {self.value}"
            raise InvalidInputError(msg, feature=_FEATURE)


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
        _require_headcount(self.headcount)
        if self.activity is not None:
            object.__setattr__(self, "activity", _activity(self.activity))


def _require_headcount(value: object) -> None:
    """Reject a headcount that is not a :class:`Headcount`.

    Raises:
        InvalidInputError: When ``value`` is not a :class:`Headcount`.
    """
    if not isinstance(value, Headcount):
        msg = f"headcount must be a Headcount; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE)


def _activity(value: object) -> EmployerActivity:
    """Return ``value`` as an :class:`EmployerActivity`.

    Returns:
        The activity named by ``value``.

    Raises:
        InvalidInputError: When ``value`` is not an activity.
    """
    try:
        return EmployerActivity(str(value))
    except ValueError:
        valid = [a.value for a in EmployerActivity]
        msg = f"activity must be one of {valid}; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE) from None
