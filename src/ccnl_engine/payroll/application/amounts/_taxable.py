"""Taxable income of one run: PdR split, run taxable and annual projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._pension import projected_adjustment
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.service.pension_fund import PensionContribution


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
        separate: Part of :attr:`period` withheld apart from the pay of the
            period (art. 23 c. 2 lett. b) DPR 600/1973).
    """

    irpef_base: Decimal
    period: Decimal
    projected: Decimal
    separate: Decimal = _ZERO


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
    pension: PensionContribution | None = None,
) -> _Taxable:
    """Return the taxable income of the run and its annual projection.

    The run enters with its actual employee INPS (IVS ceiling and 1%
    addizionale included); only the slots still to come are projected at
    the current rate, so the last slot settles on the final taxable income.
    Pension fund contributions change the taxable of the run by their
    :attr:`~ccnl_engine.payroll.service.pension_fund.PensionContribution\
.taxable_adjustment`, and the projection by the same change on the slots
    still to come, within the deduction cap left.

    Returns:
        The run and projected annual taxable income.
    """
    # Excess PdR beyond the cap is taxed ordinarily; add it back to the IRPEF base.
    irpef_base = inp.event_irpef_base + pdr.excess
    period_taxable = money(inp.monthly_gross - inps_employee + irpef_base)
    if pension is not None:
        period_taxable += pension.taxable_adjustment
    upcoming_inps = money(inp.upcoming_gross * employee_rate)
    projected = (
        inp.opening.earnings.taxable
        + period_taxable
        + inp.upcoming_gross
        - upcoming_inps
        + projected_adjustment(inp, pension)
    )
    return _Taxable(
        irpef_base=irpef_base,
        period=period_taxable,
        projected=projected,
        separate=_separate(inp, period_taxable, employee_rate, pdr),
    )


def _separate(
    inp: _AmountsInput, period_taxable: Decimal, employee_rate: Decimal, pdr: _PdrSplit
) -> Decimal:
    """Return the taxable the run withholds on under art. 23 c. 2 lett. b).

    The lett. b) of art. 23 c. 2 DPR 600/1973 covers "le mensilità
    aggiuntive e ... i compensi della stessa natura": the whole run of a
    tredicesima or quattordicesima, and the premiums of another run (AdE
    circ. 15/E/2007 par. 2.4: "premi trimestrali, semestrali e annuali"),
    the PdR beyond its cap included, net of the employee INPS at the rate
    of the run.

    Returns:
        The lett. b) taxable, between zero and ``period_taxable``.
    """
    if inp.additional_month:
        return max(_ZERO, period_taxable)
    premiums = money((inp.event_separate_base + pdr.excess) * (1 - employee_rate))
    return max(_ZERO, min(period_taxable, premiums))
