"""INPS contributions and TFR accrual of one run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._domestic import (
    compute_domestic_breakdown,
)
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.payroll.service.contributions import resolve_contributions

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown


def _ordinary_breakdown(inp: _AmountsInput, base: Decimal) -> ContributionBreakdown:
    """Return the ordinary INPS breakdown of ``base`` for the run.

    Returns:
        The breakdown with the YTD INPS base and the IVS ceiling of the run.
    """
    return resolve_contributions(
        base,
        inp.rules,
        inp.contract_type,
        inp.category,
        ytd_inps_base=inp.opening.earnings.inps_base,
        ivs_ceiling_applies=inp.ivs_ceiling_applies,
    )


def run_contributions(inp: _AmountsInput) -> tuple[ContributionBreakdown, Decimal]:
    """Return the INPS breakdown of the run and the employee rate for IRPEF.

    Domestic CCNLs have no ordinary INPS rules: their flat per-hour
    contributions apply and no employee rate is projected on the slots
    still to come.

    Returns:
        ``(breakdown, employee_rate)``.
    """
    period_inps_base = inp.monthly_gross + inp.event_inps_base
    if inp.rules.inps is not None:
        breakdown = _ordinary_breakdown(inp, period_inps_base)
        rates = resolve_rates(inp.rules, inp.contract_type, inp.category)
        return breakdown, rates.employee_rate
    breakdown = compute_domestic_breakdown(
        inp.rules,
        inp.weekly_hours,
        inp.contributable_hours,
        inp.domestic_hourly_rate,
        inp.contract_type,
    )
    return breakdown, _ZERO


def recurring_employee_inps(inp: _AmountsInput, inps_employee: Decimal) -> Decimal:
    """Return the employee INPS of the recurring pay of the run alone.

    Returns:
        ``inps_employee`` for domestic CCNLs, else the employee INPS of the
        monthly gross without the events.
    """
    return (
        inps_employee
        if inp.rules.inps is None
        else _ordinary_breakdown(inp, inp.monthly_gross).employee
    )


def tfr_accrual(inp: _AmountsInput) -> Decimal:
    """Return the TFR accrued on the run.

    Returns:
        The TFR base of the run over the accrual divisor, rounded.
    """
    period_tfr_base = inp.monthly_gross + inp.event_tfr_base
    return money(period_tfr_base / inp.rules.tfr.accrual_divisor)
