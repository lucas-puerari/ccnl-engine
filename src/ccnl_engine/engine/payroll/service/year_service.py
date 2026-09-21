"""Year payroll services: compute_payroll_year, summarize_payroll_year."""

from __future__ import annotations

import warnings
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
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle

_ZERO = Decimal(0)


def compute_payroll_year(
    request: PayrollYearRequest,
    bundle: PayrollBundle | None = None,
    *,
    repo: KnowledgeRepository | None = None,
) -> PayrollYearResult:
    """Compute a full payroll year by chaining twelve period computations.

    .. deprecated::
        Each period is computed via :func:`compute_period_payroll`, which
        divides annual figures and does not perform genuine period-based
        payroll.  Will be replaced in a future release.

    Args:
        request: Year payroll request: structural scenario, year, twelve
            period descriptors (one per calendar month), and the YTD opening
            state for January.
        bundle: Optional pre-loaded knowledge bundle shared across all twelve
            calls.  When ``None``, rulesets are loaded on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A :class:`~PayrollYearResult` containing twelve period results and
        the final YTD closing state after December.
    """
    warnings.warn(
        "compute_payroll_year() chains compute_period_payroll() calls, which divide "
        "annual figures and do not compute real period payroll. "
        "It will be replaced in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
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
        r = compute_period_payroll(period_req, bundle, repo=repo)
        results.append(r)
        state = r.closing_state
    return PayrollYearResult(periods=tuple(results), closing_state=state)


def summarize_payroll_year(result: PayrollYearResult) -> AnnualPayrollSummary:
    """Derive an annual payroll summary from aggregating period results.

    .. deprecated::
        Aggregates results from :func:`compute_payroll_year`, which uses
        annualized division rather than real period computation.
        Will be replaced in a future release.

    Args:
        result: A completed :class:`PayrollYearResult` returned by
            :func:`compute_payroll_year`.

    Returns:
        An :class:`AnnualPayrollSummary` with the annual totals and all
        ledger entries from every period in calendar order.
    """
    warnings.warn(
        "summarize_payroll_year() aggregates results from compute_payroll_year(), "
        "which divides annual figures rather than computing real period payroll. "
        "It will be replaced in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
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
