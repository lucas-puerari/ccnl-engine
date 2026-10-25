"""Period-first payroll calculation of one competence month, and its bundled sources.

The run is computed in four stages: the request is normalised into a
:class:`~ccnl_engine.period.context.services.RunContext`; the
pipeline of :mod:`~ccnl_engine.period.step.services` posts
(1) variable events and extra-month settlements, (2) INPS contributions and
TFR accrual, then the TFR settlement the engine computes, (3) IRPEF via
conguaglio YTD and surtax, (4) credits and recoveries, (5) pay items and
ledger entries after the withholding cap; the result is then assembled
with its closing YTD state and checked.

The API layer builds its defaults through these factories so that it depends
on the application layer only, never on the concrete loaders.
"""

from __future__ import annotations

from dataclasses import replace
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.period.context.request.services import build_context
from ccnl_engine.period.posting.services import post_run, run_credits
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.result.services import assemble_result
from ccnl_engine.period.step.services import (
    run_amounts,
    run_decisions,
    run_events,
    run_tfr_settlement,
)

if TYPE_CHECKING:
    from ccnl_engine.pay_item.policies import PolicyResolver
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.period.results import PeriodResult


__all__ = [
    "bundled_policies",
    "bundled_repository",
]


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository,
    resolver: PolicyResolver,
    bundle_version: str | None = None,
    mode: EngineMode = EngineMode.SIMULATION,
) -> PeriodResult:
    """Compute payroll for one competence period using the period-first model.

    Args:
        request: Period calculation input: CCNL, level, period, YTD state and
            optional variable events.
        repo: Knowledge repository the run reads; the facade passes its own.
        resolver: Policy resolver of the pay-item treatments.
        bundle_version: Knowledge-bundle version string to embed in the result.
            ``None`` when called outside a :class:`PayrollEngine` context.
        mode: Payability policy recorded on the result; ``operational``
            blocks every ruleset short of ``production``.

    Returns:
        A :class:`~ccnl_engine.period.results.PeriodResult`
        with gross, net, employer cost, closing YTD state, pay items and ledger.

    A run that cannot close next in the tax year, or whose unpaid absences
    deduct more than its pay, raises ``InvalidInputError``.  IRPEF and surtax
    are withheld up to the pay left and the rest is carried to the next runs
    of the tax year (:func:`~ccnl_engine.withholding.cap.services.cap_withholding`);
    unpaid absences that leave less pay than the other
    deductions raise ``OutOfScopeError``.
    A closing state or a reconciliation invariant that fails raises
    ``DataIntegrityError``: it indicates an internal consistency error.
    """
    ctx = build_context(request, repo, resolver)
    events = run_events(ctx)
    amounts = run_amounts(ctx, events.totals)
    events = run_tfr_settlement(ctx, events, amounts)
    decisions = run_decisions(ctx, events.totals, amounts)
    recoveries = run_credits(ctx, amounts.tax_computation)
    posted = post_run(
        ctx,
        amounts.amounts,
        events.entries + recoveries.somma.entries + recoveries.carried.entries,
    )
    result = assemble_result(
        ctx, events, amounts, recoveries, posted, decisions, bundle_version
    )
    return replace(result, mode=mode)


def bundled_repository() -> KnowledgeRepository:
    """Return the repository backed by the package-bundled JSON files.

    Returns:
        A new :class:`~ccnl_engine.period.repositories.BundledKnowledgeRepository`.
    """
    return BundledKnowledgeRepository()


@cache
def bundled_policies() -> PolicyResolver:
    """Return the pay-item policy resolver of the bundled Italian ruleset.

    Returns:
        A freshly loaded :class:`~ccnl_engine.pay_item.policies.PolicyResolver`.
    """
    return load_policy_resolver()
