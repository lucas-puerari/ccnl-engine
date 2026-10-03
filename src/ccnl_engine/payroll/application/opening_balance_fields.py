"""Field checks of the opening balances imported from another provider.

Each scalar field is checked by its annotation: an amount is a finite,
non-negative ``Decimal`` with at most two decimals, a counter a
non-negative ``int``, a reason a lower snake case code; each collection holds
only its element type.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.validation import (
    reject,
    require_code,
    require_decimal,
    require_int,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

__all__ = ["FEATURE", "check_scalar_fields", "items"]

#: Feature reported by the errors of the opening balances.
FEATURE = "opening_balances"

_OWNER = "OpeningBalances"
_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_MIN_TAX_YEAR = 2020
_MAX_TAX_YEAR = 9999


def check_scalar_fields(balances: DataclassInstance) -> None:
    """Validate every scalar field of ``balances`` on its own.

    Args:
        balances: The opening balances being constructed.
    """
    require_int(
        getattr(balances, "tax_year", None),
        f"{_OWNER}.tax_year",
        feature=FEATURE,
        minimum=_MIN_TAX_YEAR,
        maximum=_MAX_TAX_YEAR,
    )
    for f in fields(balances):
        check = _FIELD_CHECKS.get(str(f.type))
        if check is not None and f.name != "tax_year":
            check(getattr(balances, f.name), f"{_OWNER}.{f.name}")


def items[T](value: object, name: str, item: type[T]) -> tuple[T, ...]:
    """Validate a collection field element by element.

    Returns:
        The elements as a tuple.
    """
    return tuple_of(
        value,
        f"{_OWNER}.{name}",
        items_of_type(item, feature=FEATURE),
        feature=FEATURE,
    )


def _amount(value: object, path: str) -> None:
    """Reject an amount that is not a non-negative Decimal in cents."""
    require_decimal(value, path, feature=FEATURE, minimum=_ZERO)
    amount = cast("Decimal", value)
    if amount != amount.quantize(_CENT):
        reject(path, "an amount with at most two decimals", value, feature=FEATURE)


def _optional_amount(value: object, path: str) -> None:
    """Reject an amount that is neither ``None`` nor a valid amount."""
    if value is not None:
        _amount(value, path)


def _counter(value: object, path: str) -> None:
    require_int(value, path, feature=FEATURE, minimum=0)


def _reason(value: object, path: str) -> None:
    require_code(value, path, feature=FEATURE, optional=True)


#: Check of a scalar field, by its annotation.
_FIELD_CHECKS: dict[str, Callable[[object, str], None]] = {
    "Decimal": _amount,
    "Decimal | None": _optional_amount,
    "int": _counter,
    "str | None": _reason,
}
