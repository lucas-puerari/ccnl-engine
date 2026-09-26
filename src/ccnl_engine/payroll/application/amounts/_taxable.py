"""Taxable income of one run: PdR split, run taxable and annual projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._contributions import (
    recurring_employee_inps,
)
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _AmountsInput


@dataclass(frozen=True)
class _PdrSplit:
    """PdR of the run within and beyond the annual cap.

    Attributes:
        eligible: Part taxed at the substitute rate.
        excess: Part beyond the cap, taxed ordinarily.
        substitute_tax: Substitute tax on ``eligible``.
    """

    eligible: Decimal
    excess: Decimal
    substitute_tax: Decimal


@dataclass(frozen=True)
class _Taxable:
    """Taxable income of the run.

    Attributes:
        irpef_base: Event IRPEF base plus the PdR excess.
        period: Taxable income of the run.
        projected: Annual taxable income: the opening YTD, the run and the
            recurring pay of the slots still to come.
    """

    irpef_base: Decimal
    period: Decimal
    projected: Decimal


def pdr_split(inp: _AmountsInput) -> _PdrSplit:
    """Split the PdR of the run at what is left of its annual cap.

    PdR eligibility must be resolved before taxable, because any excess
    beyond the annual cap (L. 199/2025, comma 9) returns to the ordinary
    IRPEF base.

    Returns:
        The eligible and excess parts and the substitute tax.
    """
    headroom = max(_ZERO, inp.pdr_rules.max_amount - inp.opening.fringe.pdr)
    eligible = min(inp.event_substitute_base, headroom)
    return _PdrSplit(
        eligible=eligible,
        excess=inp.event_substitute_base - eligible,
        substitute_tax=money(eligible * inp.pdr_rules.flat_tax_rate),
    )


def taxable_income(
    inp: _AmountsInput,
    inps_employee: Decimal,
    employee_rate: Decimal,
    pdr: _PdrSplit,
) -> _Taxable:
    """Return the taxable income of the run and its annual projection.

    The run enters with its actual employee INPS (IVS ceiling and 1%
    addizionale included); only the slots still to come are projected at
    the current rate, so the last slot settles on the final taxable income.

    Returns:
        The run and projected annual taxable income.
    """
    # Excess PdR beyond the cap is taxed ordinarily; add it back to the IRPEF base.
    irpef_base = inp.event_irpef_base + pdr.excess
    period_taxable = money(inp.monthly_gross - inps_employee + irpef_base)
    upcoming_inps = money(inp.upcoming_gross * employee_rate)
    projected = (
        inp.opening.earnings.taxable
        + period_taxable
        + inp.upcoming_gross
        - upcoming_inps
    )
    return _Taxable(irpef_base=irpef_base, period=period_taxable, projected=projected)


def one_off_taxable(
    inp: _AmountsInput, taxable: _Taxable, inps_employee: Decimal
) -> Decimal:
    """Return the taxable income of the one-off pay of the run.

    One-off income of the run (events, excess PdR) is withheld on the run:
    its taxable is the run's taxable less that of its recurring pay alone.

    Returns:
        Zero when the run has no event IRPEF base.
    """
    if taxable.irpef_base <= _ZERO:
        return _ZERO
    recurring_inps = recurring_employee_inps(inp, inps_employee)
    recurring_taxable = money(inp.monthly_gross - recurring_inps)
    return max(_ZERO, taxable.period - recurring_taxable)
