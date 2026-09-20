"""Annual estimate services: estimate_annual, estimate_period_effects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.payroll.service.pipeline import _annual_to_scenario, compute

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.payroll.domain.scenario import (
        AnnualEstimateInput,
        PeriodPayrollInput,
    )


def estimate_annual(
    scenario: AnnualEstimateInput,
    bundle: PayrollBundle | None = None,
    *,
    repo: KnowledgeRepository | None = None,
) -> Calculation:
    """Estimate annual gross-to-net salary and employer cost.

    Computes annual payroll figures for the given scenario without any
    period-specific events (overtime, absences, sick leave, etc.).  All
    output figures are annual estimates based on the structural inputs only.

    Args:
        scenario: The annual payroll scenario describing the worker and the
            employment relationship.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with all gross, net and cost figures.
    """
    return compute(_annual_to_scenario(scenario), bundle, repo=repo)


def estimate_period_effects(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput,
    bundle: PayrollBundle | None = None,
    *,
    repo: KnowledgeRepository | None = None,
) -> Calculation:
    """Estimate the informational effect of period events on the annual figures.

    Merges the period-specific events from *period* (overtime hours, absences,
    sick leave, fringe benefits, bonuses) into the structural scenario and runs
    the computation chain.  The period events appear in dedicated result fields
    (e.g. ``overtime_supplement_monthly``, ``sick_days_monthly``) but do **not**
    flow into ``net_annual`` or ``employer_cost_annual`` in this version — those
    figures remain annualised estimates.

    Use :func:`estimate_annual` when you need the structural annual gross-to-net.
    Use this function only when you need the per-period breakdown fields alongside
    the annual figures.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        period: The period-specific events to merge in.  Must include
            :attr:`~ccnl_engine.engine.payroll.domain.scenario\
.PeriodPayrollInput.tax_period` for fiscal pro-rata; the function raises
            :exc:`~ccnl_engine.engine.errors.InvalidInputError` when absent.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with annual figures plus informational period-event fields.

    Raises:
        InvalidInputError: When ``period.tax_period`` is ``None``.
    """
    if period.tax_period is None:
        msg = "period.tax_period is required for period payroll computation"
        raise InvalidInputError(
            msg,
            feature="tax_period",
            remediation=(
                "Set PeriodPayrollInput.tax_period to a TaxPeriod with "
                "the worker's employment start, end, and eligible_work_days "
                "in the tax year.  Never omit it: the engine does not "
                "silently apply 365/365 for period computations."
            ),
        )
    return compute(
        _annual_to_scenario(scenario, period), bundle, _period=period, repo=repo
    )
