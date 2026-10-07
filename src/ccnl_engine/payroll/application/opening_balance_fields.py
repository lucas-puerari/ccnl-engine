"""Field checks of the opening balances imported from another provider.

Each scalar field is checked by its annotation: an amount is a finite,
non-negative ``Decimal`` with at most two decimals, a reason a lower snake
case code; each collection holds only its element type.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    reject,
    require_code,
    require_date,
    require_decimal,
    require_int,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.run import PayrollRunId
    from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
    from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation

__all__ = [
    "FEATURE",
    "check_bases",
    "check_carried",
    "check_scalar_fields",
    "items",
]

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


def check_carried(
    tax_year: int,
    deferred_shortfall: DeferredShortfall | None,
    surtax_obligations: tuple[SurtaxObligation, ...],
) -> None:
    """Reject obligations not carried from a year before ``tax_year``.

    Raises:
        InvalidInputError: When the deferral is of a conguaglio other than
            that of ``tax_year - 1``, or a surtax obligation is determined
            by the conguaglio of ``tax_year`` or later.
    """
    deferred = deferred_shortfall
    if deferred is not None and deferred.tax_year != tax_year - 1:
        msg = (
            "OpeningBalances.deferred_shortfall must be deferred by the "
            f"conguaglio of {tax_year - 1}; got {deferred.tax_year}"
        )
        raise InvalidInputError(
            msg, field="OpeningBalances.deferred_shortfall", feature=FEATURE
        )
    late = [o for o in surtax_obligations if o.tax_year >= tax_year]
    if late:
        msg = (
            f"OpeningBalances.surtax_obligations must be determined by "
            f"the conguaglio of a year before {tax_year}; got "
            f"{[(o.component.value, o.tax_year) for o in late]}"
        )
        raise InvalidInputError(
            msg, field="OpeningBalances.surtax_obligations", feature=FEATURE
        )


def check_bases(
    payments: tuple[PaymentId, ...],
    competence_runs: tuple[PayrollRunId, ...],
    inps_bases: tuple[InpsBaseYtd, ...],
) -> None:
    """Reject runs of a competence year without its INPS base.

    The base of a competence year counts toward the IVS massimale of every
    later run of that year (L. 335/1995 art. 2 c. 18), so a year with a run
    closed by the previous provider needs its base stated, ``own`` and
    ``other_employers``.

    Raises:
        InvalidInputError: When a payment or a competence run is of a year
            without an entry in ``inps_bases``.
    """
    years = {p.run_id.year for p in payments} | {r.year for r in competence_runs}
    missing = sorted(years - {b.year for b in inps_bases})
    if missing:
        msg = (
            f"OpeningBalances.inps_bases has no base for the competence years "
            f"{missing} of the runs already closed: state the INPS base of "
            "this employment and of the other employments of each year"
        )
        raise InvalidInputError(
            msg, field="OpeningBalances.inps_bases", feature=FEATURE
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


def _reason(value: object, path: str) -> None:
    require_code(value, path, feature=FEATURE, optional=True)


def _optional_date(value: object, path: str) -> None:
    require_date(value, path, feature=FEATURE, optional=True)


#: Check of a scalar field, by its annotation.
_FIELD_CHECKS: dict[str, Callable[[object, str], None]] = {
    "Decimal": _amount,
    "Decimal | None": _optional_amount,
    "str | None": _reason,
    "date | None": _optional_date,
}
