"""Validators of the public inputs, shared by every input dataclass.

The public inputs are frozen dataclasses that validate themselves in
``__post_init__`` with these functions, so a value of the wrong type, a
non-finite decimal, a ``bool`` given as an ``int`` or a ``datetime`` given
as a ``date`` is rejected on construction with
:class:`~ccnl_engine.shared.domain.errors.InvalidInputError`, never with a
``TypeError``, an ``AttributeError`` or a ``decimal`` signal deep in a
calculation.  Collections are validated element by element by
:mod:`ccnl_engine.shared.domain.collection_validation`.

Every validator takes the ``path`` of the field, e.g.
``"PeriodFacts.events"``, and rejects through :func:`reject`, which raises
``InvalidInputError`` with the path as
:attr:`~ccnl_engine.shared.domain.errors.InvalidInputError.field`, the
feature and a remediation.
"""

from __future__ import annotations

import re
import reprlib
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, NoReturn

from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = [
    "MAX_DECIMAL_MAGNITUDE",
    "FieldSpec",
    "parse_enum",
    "reject",
    "require_bool",
    "require_choice",
    "require_code",
    "require_date",
    "require_decimal",
    "require_instance",
    "require_instances",
    "require_int",
    "require_str",
    "type_names",
]

#: A field whose type to check: name, value, accepted types, ``None``
#: accepted.
type FieldSpec = tuple[str, object, type | tuple[type, ...], bool]

#: Exclusive bound of the magnitude of any decimal input: a billion.
MAX_DECIMAL_MAGNITUDE = Decimal("1E+9")

_REPR = reprlib.Repr(maxstring=60, maxother=60)
_CODE = re.compile(r"[a-z][a-z0-9_]*")


def reject(path: str, expected: str, value: object, *, feature: str) -> NoReturn:
    """Reject a field that is not what it must be.

    Every validator of this module rejects through it, so every rejected
    field carries its path, its feature and the same remediation.

    Args:
        path: Path of the field, e.g. ``"OvertimeEvent.hours"``.
        expected: What the field must be, e.g. ``"a finite Decimal > 0"``.
        value: The rejected value.
        feature: Feature of the input that rejected the field.

    Raises:
        InvalidInputError: Always, with ``path`` as its field.
    """
    msg = f"{path} must be {expected}; got {_REPR.repr(value)}"
    raise InvalidInputError(
        msg,
        field=path,
        feature=feature,
        remediation=f"Supply {path} as {expected}.",
    )


def type_names(expected: type | tuple[type, ...]) -> str:
    """Name the accepted types of a field for an error message.

    Returns:
        E.g. ``"a WeeklyHours"``, ``"an int"`` or ``"a Permanent or a
        FixedTerm"``.
    """
    types = expected if isinstance(expected, tuple) else (expected,)
    return " or ".join(_with_article(t.__name__) for t in types)


def _with_article(name: str) -> str:
    article = "an" if name[:1].lower() in "aeiou" else "a"
    return f"{article} {name}"


def require_instance(
    value: object,
    expected: type | tuple[type, ...],
    path: str,
    *,
    feature: str,
    optional: bool = False,
) -> None:
    """Reject a value that is not an instance of ``expected``.

    ``None`` is accepted when ``optional``.
    """
    if not ((optional and value is None) or isinstance(value, expected)):
        reject(path, type_names(expected), value, feature=feature)


def require_instances(owner: str, fields: Iterable[FieldSpec], *, feature: str) -> None:
    """Reject the first field that is not of its type.

    Args:
        owner: Name of the input, prefixed to each field name in the path.
        fields: The fields to check, in order.
        feature: Feature of the input.
    """
    for name, value, expected, optional in fields:
        require_instance(
            value, expected, f"{owner}.{name}", feature=feature, optional=optional
        )


def require_bool(value: object, path: str, *, feature: str) -> None:
    """Reject a value that is not ``True`` or ``False``."""
    if not isinstance(value, bool):
        reject(path, "a bool", value, feature=feature)


def require_int(
    value: object,
    path: str,
    *,
    feature: str,
    minimum: int | None = None,
    maximum: int | None = None,
    optional: bool = False,
) -> None:
    """Reject a value that is not an ``int`` within ``[minimum, maximum]``.

    A ``bool`` is not an ``int`` here, although Python makes it one.
    ``None`` is accepted when ``optional``.
    """
    if optional and value is None:
        return
    expected = _bounded("an int", minimum, maximum)
    if isinstance(value, bool) or not isinstance(value, int):
        reject(path, expected, value, feature=feature)
    if not _within(value, minimum, maximum):
        reject(path, expected, value, feature=feature)


def require_decimal(
    value: object,
    path: str,
    *,
    feature: str,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
    positive: bool = False,
    optional: bool = False,
) -> None:
    """Reject a value that is not a finite ``Decimal`` within its bounds.

    The finiteness is checked before any comparison, so ``NaN`` and the
    infinities are rejected as input instead of signalling
    ``decimal.InvalidOperation``.  So is a magnitude of
    :data:`MAX_DECIMAL_MAGNITUDE` or more, which no payroll amount reaches
    and whose products would overflow the 28 digits of a cent rounding.
    An ``int`` or a ``float`` is rejected: amounts and rates are exact
    decimals.

    Args:
        value: The value to check.
        path: Path of the field.
        feature: Feature of the input.
        minimum: Lowest accepted value, inclusive.
        maximum: Highest accepted value, inclusive.
        positive: Reject zero and below.
        optional: Accept ``None``.
    """
    if optional and value is None:
        return
    expected = _bounded("a finite Decimal", minimum, maximum, positive=positive)
    if not isinstance(value, Decimal) or not value.is_finite():
        reject(path, expected, value, feature=feature)
    if abs(value) >= MAX_DECIMAL_MAGNITUDE:
        bounded = f"{expected} below {MAX_DECIMAL_MAGNITUDE} in magnitude"
        reject(path, bounded, value, feature=feature)
    if (positive and value <= 0) or not _within(value, minimum, maximum):
        reject(path, expected, value, feature=feature)


def _within[N: (int, Decimal)](value: N, minimum: N | None, maximum: N | None) -> bool:
    return (minimum is None or value >= minimum) and (
        maximum is None or value <= maximum
    )


def _bounded(
    kind: str,
    minimum: object | None,
    maximum: object | None,
    *,
    positive: bool = False,
) -> str:
    bounds = [
        text
        for applies, text in (
            (positive, "> 0"),
            (minimum is not None, f">= {minimum}"),
            (maximum is not None, f"<= {maximum}"),
        )
        if applies
    ]
    return kind if not bounds else f"{kind} {' and '.join(bounds)}"


def require_date(
    value: object, path: str, *, feature: str, optional: bool = False
) -> None:
    """Reject a value that is not a ``date``, a ``datetime`` included.

    A ``datetime`` does not compare with a ``date``.  ``None`` is accepted
    when ``optional``.
    """
    if optional and value is None:
        return
    if isinstance(value, datetime) or not isinstance(value, date):
        reject(path, "a date (not a datetime)", value, feature=feature)


def require_str(
    value: object,
    path: str,
    *,
    feature: str,
    non_blank: bool = False,
    optional: bool = False,
) -> None:
    """Reject a value that is not a ``str``, or a blank one when ``non_blank``.

    ``None`` is accepted when ``optional``.
    """
    if optional and value is None:
        return
    expected = "a non-blank str" if non_blank else "a str"
    if not isinstance(value, str) or (non_blank and not value.strip()):
        reject(path, expected, value, feature=feature)


def require_code(
    value: object, path: str, *, feature: str, optional: bool = False
) -> None:
    """Reject a value that is not a lower snake case code, e.g. ``"full_amount"``.

    ``None`` is accepted when ``optional``.
    """
    if optional and value is None:
        return
    if not isinstance(value, str) or not _CODE.fullmatch(value):
        reject(path, "a lower snake case code", value, feature=feature)


def require_choice(
    value: object, choices: tuple[str, ...], path: str, *, feature: str
) -> None:
    """Reject a value that is not one of the strings ``choices``."""
    if not isinstance(value, str) or value not in choices:
        reject(path, f"one of {list(choices)}", value, feature=feature)


def parse_enum[E: StrEnum](
    value: object, enum: type[E], path: str, *, feature: str
) -> E:
    """Return ``value`` as a member of ``enum``.

    A member or its string value is accepted; anything else is rejected.

    Returns:
        The member named by ``value``.
    """
    if isinstance(value, enum):
        return value
    members = {member.value: member for member in enum}
    if isinstance(value, str) and value in members:
        return members[value]
    reject(path, f"one of {list(members)}", value, feature=feature)
