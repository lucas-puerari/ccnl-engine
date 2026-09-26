"""Employer domain types: headcount value object and employer model."""

from __future__ import annotations

from dataclasses import dataclass, field

from ccnl_engine.engine.errors import InvalidInputError

__all__ = ["Employer", "Headcount"]

_FEATURE = "employer"
_DEFAULT_HEADCOUNT_VALUE = 50


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
class Employer:
    """The employer of the worker being paid.

    The only employer model the payroll pipeline consumes.

    Attributes:
        headcount: Employer headcount, used to select the INPS contribution
            tier.  Defaults to 50 employees when the employer does not
            declare it.

    Raises:
        InvalidInputError: When ``headcount`` is not a :class:`Headcount`.
    """

    headcount: Headcount = field(
        default_factory=lambda: Headcount(_DEFAULT_HEADCOUNT_VALUE)
    )

    def __post_init__(self) -> None:  # noqa: D105
        _require_headcount(self.headcount)


def _require_headcount(value: object) -> None:
    if not isinstance(value, Headcount):
        msg = f"headcount must be a Headcount; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE)
