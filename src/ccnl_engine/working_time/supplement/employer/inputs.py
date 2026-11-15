"""Supplement rates of a company or territorial agreement, stated by the employer.

A CCNL may leave the night, holiday or shift supplement to the second-level
agreement (Università art. 26 c. 6: "La contrattazione collettiva
integrativa stabilisce [...] la relativa maggiorazione retributiva"), or let
it raise the national one ("eventualmente elevabile in sede di
contrattazione integrativa").  The employer states each rate once, and the
engine prices every event of that work with it, like a band of the CCNL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.compensation.second_level.inputs import SecondLevelAgreement
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    parse_enum,
    reject,
    require_bool,
    require_date,
    require_decimal,
    require_instance,
    require_str,
)
from ccnl_engine.working_time.supplement.models import SupplementWork

__all__ = ["RateUnit", "SecondLevelRate", "check_second_level_rates"]

_FEATURE = "second_level"


class RateUnit(StrEnum):
    """What a second-level rate is a measure of.

    Values:
        PERCENTAGE: A share of the hourly base of the CCNL for each hour.
        PER_HOUR: An amount in EUR for each hour.
        PER_SHIFT: An amount in EUR for each turn or day of shift.
    """

    PERCENTAGE = "percentage"
    PER_HOUR = "per_hour"
    PER_SHIFT = "per_shift"


@dataclass(frozen=True, slots=True)
class SecondLevelRate:
    """The supplement of one kind of work set by a second-level agreement.

    Attributes:
        work: The work it pays (night, holiday, a shift, ...).
        rate: ``0.15`` for 15% with :attr:`RateUnit.PERCENTAGE`, else EUR.
        unit: What the rate measures.
        agreement: The kind of agreement, ``company`` or ``territorial``.
        valid_from: First day the rate is in force.
        valid_until: Last day it is in force, ``None`` while open.
        levels: Codes of the CCNL levels it applies to; empty for every level.
        hours_paid_apart: Whether the hours themselves are paid on top of the
            monthly pay (a public holiday worked: L. 260/1949 art. 5).

    Raises:
        InvalidInputError: When a field is not of its type, ``rate`` is not
            above zero, or the period ends before it starts.
    """

    work: SupplementWork
    rate: Decimal
    unit: RateUnit
    agreement: SecondLevelAgreement
    valid_from: date
    valid_until: date | None = None
    levels: tuple[str, ...] = ()
    hours_paid_apart: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        owner = "SecondLevelRate"
        for name, kind in (
            ("work", SupplementWork),
            ("unit", RateUnit),
            ("agreement", SecondLevelAgreement),
        ):
            value = parse_enum(
                getattr(self, name), kind, f"{owner}.{name}", feature=_FEATURE
            )
            object.__setattr__(self, name, value)
        require_decimal(self.rate, f"{owner}.rate", feature=_FEATURE, positive=True)
        require_date(self.valid_from, f"{owner}.valid_from", feature=_FEATURE)
        require_date(
            self.valid_until, f"{owner}.valid_until", feature=_FEATURE, optional=True
        )
        if self.valid_until is not None and self.valid_until < self.valid_from:
            reject(
                f"{owner}.valid_until",
                "a day on or after valid_from",
                self.valid_until,
                feature=_FEATURE,
            )
        if not isinstance(self.levels, tuple | list):
            reject(
                f"{owner}.levels",
                "a tuple of level codes",
                self.levels,
                feature=_FEATURE,
            )
        for i, level in enumerate(self.levels):
            require_str(level, f"{owner}.levels[{i}]", feature=_FEATURE, non_blank=True)
        object.__setattr__(self, "levels", tuple(self.levels))
        require_bool(
            self.hours_paid_apart, f"{owner}.hours_paid_apart", feature=_FEATURE
        )

    def applies_to(self, level_code: str, day: date) -> bool:
        """Return whether the rate prices the work of ``level_code`` on ``day``.

        Returns:
            ``True`` when the day is in its period and the level is listed,
            or no level is.
        """
        in_force = self.valid_from <= day and (
            self.valid_until is None or day <= self.valid_until
        )
        return in_force and (not self.levels or level_code in self.levels)


def check_second_level_rates(value: object, path: str) -> tuple[SecondLevelRate, ...]:
    """Validate the second-level rates of an employer.

    Returns:
        The rates as a tuple.

    Raises:
        InvalidInputError: When ``value`` is not a tuple or a list of
            :class:`SecondLevelRate`, or two rates price the same work of
            the same levels.
    """
    if not isinstance(value, tuple | list):
        reject(path, "a tuple or a list of SecondLevelRate", value, feature=_FEATURE)
    for i, rate in enumerate(value):
        require_instance(rate, SecondLevelRate, f"{path}[{i}]", feature=_FEATURE)
    keys = [(r.work, r.levels, r.valid_from) for r in value]
    if len(set(keys)) != len(keys):
        msg = "two second-level rates price the same work of the same levels"
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    return tuple(value)
