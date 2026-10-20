"""The payslip voce of a pay item: its code, unit, quantity and unit rate.

A pay item is one line of the payslip.  Its engine code is its kind, with
the qualifier of a kind that holds several voci (the allowance code of a
fixed allowance, 13 or 14 of an extra month), which a payroll provider maps
to its own voci.  The quantity a line prints is the measure of its unit:
hours for overtime and time supplements, days for absences and sickness,
the item quantity otherwise; the unit rate is the amount over it.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.pay_item.models import PayItem

__all__ = ["VoceSide", "VoceUnit", "measure", "side", "unit", "unit_rate", "voce_code"]

_RATE = Decimal("0.00001")
#: Field holding the qualifier of a kind with several voci.
_QUALIFIERS = ("allowance_code", "month_number")
#: Field holding the hours or the days of a kind measured in them.
_HOURS = ("hours",)
_DAYS = ("absence_days", "sick_days")


class VoceSide(StrEnum):
    """Column of the payslip a pay item belongs to.

    Attributes:
        EARNING: Competenze, added to the gross.
        DEDUCTION: Trattenute, taken from the pay.
        EMPLOYER: A cost of the employer, outside the pay (contributions,
            TFR accrued).
        FIGURATIVE: Shown for its effect on the bases or the tax, not paid
            (fringe benefits, welfare, the credits applied to IRPEF).
    """

    EARNING = "earning"
    DEDUCTION = "deduction"
    EMPLOYER = "employer"
    FIGURATIVE = "figurative"


_SIDES = {
    "absence_deduction": VoceSide.DEDUCTION,
    "employee_withholding_item": VoceSide.DEDUCTION,
    "employer_contribution_item": VoceSide.EMPLOYER,
    "tfr_accrual_item": VoceSide.EMPLOYER,
    "fringe_benefit_item": VoceSide.FIGURATIVE,
    "welfare_item": VoceSide.FIGURATIVE,
    "tax_credit_item": VoceSide.FIGURATIVE,
}


class VoceUnit(StrEnum):
    """Unit a payslip line counts its quantity in.

    Attributes:
        HOURS: Hours (straordinario, maggiorazioni).
        DAYS: Days (assenze, malattia).
        UNITS: The item quantity (one month, one rateo, one payment).
    """

    HOURS = "hours"
    DAYS = "days"
    UNITS = "units"


def voce_code(item: PayItem) -> str:
    """Return the engine code of the voce of ``item``.

    Returns:
        The kind, with ``:qualifier`` for a fixed allowance or an extra
        month.
    """
    for name in _QUALIFIERS:
        value = getattr(item, name, None)
        if value not in {None, ""}:
            return f"{item.kind}:{value}"
    return item.kind


def _counted(item: PayItem, names: tuple[str, ...]) -> Decimal | None:
    """Return the first of ``names`` the item records above zero.

    Returns:
        The value, ``None`` when none is above zero.
    """
    for name in names:
        value = getattr(item, name, None)
        if isinstance(value, Decimal) and value > 0:
            return value
    return None


def unit(item: PayItem) -> VoceUnit:
    """Return the unit ``item`` counts its quantity in.

    Returns:
        Hours or days when the item records them, units otherwise (a
        supplement stated as an amount has no hours).
    """
    if _counted(item, _HOURS) is not None:
        return VoceUnit.HOURS
    if _counted(item, _DAYS) is not None:
        return VoceUnit.DAYS
    return VoceUnit.UNITS


def measure(item: PayItem) -> Decimal:
    """Return the quantity of ``item`` in its :func:`unit`.

    Returns:
        The hours or days the item records, else its quantity.
    """
    hours = _counted(item, _HOURS)
    if hours is not None:
        return hours
    days = _counted(item, _DAYS)
    return item.quantity if days is None else days


def unit_rate(item: PayItem) -> Decimal | None:
    """Return the amount of ``item`` per unit of its quantity.

    Returns:
        The amount over :func:`measure`, to five decimals half up; ``None`` for a
        zero quantity.
    """
    quantity = measure(item)
    if not quantity:
        return None
    return (item.amount / quantity).quantize(_RATE, rounding=ROUND_HALF_UP)


def side(item: PayItem) -> VoceSide:
    """Return the payslip column of ``item``.

    Returns:
        Deduction, employer or figurative for the kinds listed so, earning
        otherwise.
    """
    return _SIDES.get(item.kind, VoceSide.EARNING)
