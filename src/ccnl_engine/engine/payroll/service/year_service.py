"""Year payroll services: compute_payroll_year, summarize_payroll_year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.period_payroll import (
    AnnualPayrollSummary,
    PayrollYearRequest,
    PayrollYearResult,
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.service.period_service import compute_period_payroll

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle

_ZERO = Decimal(0)


def compute_payroll_year(
    request: PayrollYearRequest,
    bundle: PayrollBundle | None = None,
) -> PayrollYearResult:
    """Compute a full payroll year by chaining twelve period computations.

    Calls :func:`compute_period_payroll` once per month, threading the
    closing :class:`~PayrollState` of each period into the next as its
    opening state.  The structural scenario's ``as_of`` date is overridden
    to the first day of each month; all other structural fields are reused.

    Args:
        request: Year payroll request: structural scenario, year, twelve
            period descriptors (one per calendar month), and the YTD opening
            state for January.
        bundle: Optional pre-loaded knowledge bundle shared across all twelve
            calls.  When ``None``, rulesets are loaded on demand.

    Returns:
        A :class:`~PayrollYearResult` containing twelve period results and
        the final YTD closing state after December.
    """
    state = request.opening_state
    results: list[PeriodPayrollResult] = []
    for i, ev in enumerate(request.month_periods):
        month = i + 1
        updated_employment = request.structural.employment.model_copy(
            update={"as_of": date(request.year, month, 1)}
        )
        updated_structural = request.structural.model_copy(
            update={"employment": updated_employment}
        )
        period_req = PeriodPayrollRequest(
            structural=updated_structural,
            period=ev,
            opening_state=state,
        )
        r = compute_period_payroll(period_req, bundle)
        results.append(r)
        state = r.closing_state
    return PayrollYearResult(periods=tuple(results), closing_state=state)


def summarize_payroll_year(result: PayrollYearResult) -> AnnualPayrollSummary:
    """Derive an annual payroll summary from aggregating period results.

    Sums the per-period figures (gross, net, employer cost) across all twelve
    periods and collects every ledger entry into a single flat tuple.  The
    :attr:`~AnnualPayrollSummary.closing_state` mirrors
    :attr:`PayrollYearResult.closing_state`, which already holds the final
    year-to-date progressives after December.

    Args:
        result: A completed :class:`PayrollYearResult` returned by
            :func:`compute_payroll_year`.

    Returns:
        An :class:`AnnualPayrollSummary` with the annual totals and all
        ledger entries from every period in calendar order.
    """
    total_gross = sum((p.period_gross for p in result.periods), _ZERO)
    total_net = sum((p.period_net for p in result.periods), _ZERO)
    total_employer_cost = sum((p.period_employer_cost for p in result.periods), _ZERO)
    ledger_entries = tuple(entry for p in result.periods for entry in p.ledger_entries)
    return AnnualPayrollSummary(
        total_gross=total_gross,
        total_net=total_net,
        total_employer_cost=total_employer_cost,
        closing_state=result.closing_state,
        ledger_entries=ledger_entries,
    )
