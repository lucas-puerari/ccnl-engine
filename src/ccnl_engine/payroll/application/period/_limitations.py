"""Model limitations that concern one run.

The candidates are the engine limitations of the bundle and those the
simplification notes of the CCNL declare.  Each is matched against the
facts of the run: the CCNL, the competence date the rules were read at,
the contract type, level, category, run kind and seniority of the request,
the capabilities the capability report scopes as applicable, and the
engine limitations whose code path built the pay chain or paid an event.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._contractual_fund import contractual_paths
from ccnl_engine.payroll.application.period._seniority import seniority_months_at
from ccnl_engine.payroll.domain.capability_report import CapabilityScope
from ccnl_engine.shared.domain.limitation import LimitationFacts

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.capability_report import CapabilityReport
    from ccnl_engine.shared.domain.limitation import ModelLimitation

__all__ = ["limitation_facts", "run_limitations"]


def limitation_facts(
    ctx: RunContext,
    report: CapabilityReport,
    traversed: frozenset[str] = frozenset(),
) -> LimitationFacts:
    """Return the facts of the run the limitation scopes are matched against.

    Returns:
        The facts of the run.
    """
    request = ctx.request
    category = ctx.worker_category
    return LimitationFacts(
        ccnl_id=ctx.contract.ccnl.meta.ccnl_id,
        as_of=ctx.contract.tctx.competence,
        contract_type=request.contract_type.type,
        level_code=ctx.contract.level.code,
        worker_category=None if category is None else str(category),
        run_kind=str(ctx.run_kind),
        seniority_months=seniority_months_at(
            request.seniority, ctx.contract.tctx.competence
        ),
        applicable=frozenset(
            feature
            for feature, scope in report.scope.items()
            if scope is CapabilityScope.APPLICABLE
        ),
        traversed=frozenset(ctx.chain.limitations) | traversed | contractual_paths(ctx),
    )


def run_limitations(
    ctx: RunContext,
    report: CapabilityReport,
    traversed: frozenset[str] = frozenset(),
) -> tuple[ModelLimitation, ...]:
    """Return the limitations that concern the run, engine ones first.

    Args:
        ctx: Context of the run.
        report: Capability report of the run.
        traversed: Engine limitations whose path the events of the run
            took, besides those of the pay chain.

    Returns:
        The applicable limitations, each once.
    """
    facts = limitation_facts(ctx, report, traversed)
    candidates = (*ctx.repo.load_engine_limitations(), *ctx.contract.ccnl.limitations)
    return tuple(
        limitation for limitation in candidates if limitation.applies_to(facts)
    )
