"""Pay elements of a company or territorial agreement, stated by the caller.

A second-level agreement (contratto aziendale or territoriale) adds monthly
amounts on top of the CCNL tables.  The bundle does not carry these
agreements: the employer states each element once, with the levels it
applies to and the period it is in force, and the engine pays it as a fixed
allowance of the level, like an element of the CCNL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    parse_enum,
    reject,
    require_bool,
    require_code,
    require_date,
    require_decimal,
    require_instance,
    require_str,
)

__all__ = [
    "SecondLevelAgreement",
    "SecondLevelElement",
    "check_second_level_elements",
]

_FEATURE = "second_level"


class SecondLevelAgreement(StrEnum):
    """Kind of the agreement an element comes from.

    Values:
        COMPANY: A contratto aziendale of the employer.
        TERRITORIAL: A contratto territoriale (provincial or regional).
    """

    COMPANY = "company"
    TERRITORIAL = "territorial"


@dataclass(frozen=True, slots=True)
class SecondLevelElement:
    """A monthly element of a company or territorial agreement.

    Attributes:
        code: Lower snake case code of the element, unique within the
            employer, e.g. ``"premio_presenza"``; it names the earning on
            the payslip.
        monthly: Full-time monthly amount in EUR, above zero.
        agreement: The kind of agreement, ``company`` or ``territorial``.
        valid_from: First day the element is in force.
        valid_until: Last day it is in force, ``None`` while open.
        levels: Codes of the CCNL levels it applies to; empty for every
            level.
        extra_months: Whether it is paid on the extra months of the CCNL.
        tfr_relevant: Whether it enters the TFR base (art. 2120 c. 2 c.c.,
            unless the agreement excludes it).

    Raises:
        InvalidInputError: When a field is not of its type, ``monthly`` is
            not above zero, or the period ends before it starts.
    """

    code: str
    monthly: Decimal
    agreement: SecondLevelAgreement
    valid_from: date
    valid_until: date | None = None
    levels: tuple[str, ...] = ()
    extra_months: bool = True
    tfr_relevant: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        owner = "SecondLevelElement"
        require_code(self.code, f"{owner}.code", feature=_FEATURE)
        require_decimal(
            self.monthly, f"{owner}.monthly", feature=_FEATURE, positive=True
        )
        agreement = parse_enum(
            self.agreement, SecondLevelAgreement, f"{owner}.agreement", feature=_FEATURE
        )
        object.__setattr__(self, "agreement", agreement)
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
        for name in ("extra_months", "tfr_relevant"):
            require_bool(getattr(self, name), f"{owner}.{name}", feature=_FEATURE)

    def applies_to(self, level_code: str, day: date) -> bool:
        """Return whether the element is paid to ``level_code`` on ``day``.

        Returns:
            ``True`` when the day is in its period and the level is listed,
            or no level is.
        """
        in_force = self.valid_from <= day and (
            self.valid_until is None or day <= self.valid_until
        )
        return in_force and (not self.levels or level_code in self.levels)


def check_second_level_elements(
    value: object, path: str
) -> tuple[SecondLevelElement, ...]:
    """Validate the second-level elements of an employer.

    Returns:
        The elements as a tuple.

    Raises:
        InvalidInputError: When ``value`` is not a tuple or a list of
            :class:`SecondLevelElement`, or two elements share a code.
    """
    if not isinstance(value, tuple | list):
        reject(path, "a tuple or a list of SecondLevelElement", value, feature=_FEATURE)
    for i, element in enumerate(value):
        require_instance(element, SecondLevelElement, f"{path}[{i}]", feature=_FEATURE)
    codes = [e.code for e in value]
    if len(set(codes)) != len(codes):
        msg = f"two second-level elements share a code: {sorted(codes)}"
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    return tuple(value)
