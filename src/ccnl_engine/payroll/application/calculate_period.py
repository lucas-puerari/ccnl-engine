"""Period-first payroll calculation: single competence month.

The run is computed in four stages: the request is normalised into a
:class:`~ccnl_engine.payroll.application.period._context.RunContext`; the
pipeline of :mod:`~ccnl_engine.payroll.application.period._pipeline` posts
(1) variable events and extra-month settlements, (2) INPS contributions and
TFR accrual, (3) IRPEF via conguaglio YTD and surtax, (4) credits and
recoveries, (5) pay items and ledger entries after the withholding cap; the
result is then assembled with its closing YTD state and checked.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._assembly import assemble_result
from ccnl_engine.payroll.application.period._context import build_context
from ccnl_engine.payroll.application.period._pipeline import (
    run_amounts,
    run_decisions,
    run_events,
)
from ccnl_engine.payroll.application.period._posting import post_run, run_credits

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodResult
    from ccnl_engine.payroll.domain.policy import PolicyResolver


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
) -> PeriodResult:
    """Compute payroll for one competence period using the period-first model.

    Args:
        request: Period calculation input: CCNL, level, period, YTD state and
            optional variable events.
        repo: Optional knowledge repository. Uses
            :class:`~ccnl_engine.payroll.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` when ``None``.
        resolver: Optional pre-loaded :class:`~ccnl_engine.payroll.domain.policy\
.PolicyResolver`.  When ``None``, the bundled Italian ruleset is loaded on every
            call.  Pass a cached instance (e.g. from :attr:`PayrollEngine._resolver`)
            to avoid repeated JSON parsing.
        bundle_version: Knowledge-bundle version string to embed in the result.
            ``None`` when called outside a :class:`PayrollEngine` context.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.period.PeriodResult`
        with gross, net, employer cost, closing YTD state, pay items and ledger.

    A run that cannot close next in the tax year, or whose unpaid absences
    deduct more than its pay, raises ``InvalidInputError``.  IRPEF and surtax
    are withheld up to the pay left and the rest is carried to the next runs
    of the tax year (:func:`~ccnl_engine.payroll.application.withholding._cap\
.cap_withholding`); unpaid absences that leave less pay than the other
    deductions raise ``OutOfScopeError``.
    A closing state or a reconciliation invariant that fails raises
    ``DataIntegrityError``: it indicates an internal consistency error.
    """
    ctx = build_context(request, repo, resolver)
    events = run_events(ctx)
    amounts = run_amounts(ctx, events.totals)
    decisions = run_decisions(ctx, events.totals, amounts.amounts)
    recoveries = run_credits(ctx, amounts.tax_computation)
    posted = post_run(
        ctx,
        amounts.amounts,
        events.entries + recoveries.somma.entries + recoveries.carried.entries,
    )
    return assemble_result(
        ctx, events, amounts, recoveries, posted, decisions, bundle_version
    )
