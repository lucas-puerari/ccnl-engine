"""Pension fund contributions of one run and their effect on the taxable."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.compensation import FundContributionBase
from ccnl_engine.payroll.service.pension_fund import contribute, upcoming_adjustment

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.service.pension_fund import PensionContribution

_ZERO = Decimal(0)


def run_pension(inp: _AmountsInput) -> PensionContribution | None:
    """Return the fund contributions of the run, on the base of the fund.

    The base is the INPS base of the run or, for a fund assessed on the pay
    counted for the TFR (e.g. Fon.Te.), the TFR base: the recurring gross,
    the benefits in kind and the events entering the TFR.

    Returns:
        ``None`` when the worker is not enrolled.
    """
    if inp.pension is None:
        return None
    base = fund_base(
        inp.pension.fund.contribution_base,
        inps_base=inp.monthly_gross + inp.event_inps_base,
        tfr_base=inp.monthly_gross + inp.in_kind + inp.event_tfr_base,
    )
    return contribute(inp.pension, base, inp.opening.earnings.pension_deducted)


def fund_base(
    kind: FundContributionBase, *, inps_base: Decimal, tfr_base: Decimal
) -> Decimal:
    """Return the base of the run that ``kind`` names.

    Returns:
        ``tfr_base`` for a fund on the TFR base, ``inps_base`` otherwise.
    """
    return tfr_base if kind is FundContributionBase.TFR_BASE else inps_base


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
