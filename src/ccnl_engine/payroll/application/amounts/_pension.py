"""Pension fund contributions of one run and their effect on the taxable."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.pension_fund import contribute, upcoming_adjustment

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.service.pension_fund import PensionContribution

_ZERO = Decimal(0)


def run_pension(inp: _AmountsInput) -> PensionContribution | None:
    """Return the fund contributions of the run, on its INPS base.

    Returns:
        ``None`` when the worker is not enrolled.
    """
    if inp.pension is None:
        return None
    return contribute(
        inp.pension,
        inp.monthly_gross + inp.event_inps_base,
        inp.opening.earnings.pension_deducted,
    )


def recurring_adjustment(inp: _AmountsInput) -> Decimal:
    """Return the taxable change of the fund on the recurring pay alone.

    Returns:
        Zero when the worker is not enrolled.
    """
    if inp.pension is None:
        return _ZERO
    recurring = contribute(
        inp.pension, inp.monthly_gross, inp.opening.earnings.pension_deducted
    )
    return recurring.taxable_adjustment


def projected_adjustment(
    inp: _AmountsInput, pension: PensionContribution | None
) -> Decimal:
    """Return the taxable change of the fund on the slots still to come.

    The recurring gross still to come is taken as their INPS base, as the
    projection of the employee INPS does.

    Returns:
        Zero when the worker is not enrolled.
    """
    if pension is None:
        return _ZERO
    deducted = inp.opening.earnings.pension_deducted + pension.deductible
    return upcoming_adjustment(pension.terms, inp.upcoming_gross, deducted)
