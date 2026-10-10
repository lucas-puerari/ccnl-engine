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

from ccnl_engine.knowledge.limitation.models import LimitationFacts
from ccnl_engine.payroll.assurance.services_ruleset import provisional_paths
from ccnl_engine.payroll.capability.results import CapabilityScope
from ccnl_engine.payroll.contribution.rules_contractual_fund import contractual_paths
from ccnl_engine.payroll.contribution.services_enam import enam_paths
from ccnl_engine.payroll.contribution.services_minimum_base import (
    minimum_base_paths,
)
from ccnl_engine.payroll.contribution.services_pension_decision import paid_month_paths
from ccnl_engine.payroll.contribution.services_tfr_compensation import (
    tfr_compensation_paths,
)
from ccnl_engine.payroll.employment.services_seniority import seniority_months_at

if TYPE_CHECKING:
    from ccnl_engine.knowledge.limitation.models import ModelLimitation
    from ccnl_engine.payroll.capability.results import CapabilityReport
    from ccnl_engine.payroll.event.handlers_totals import _EventTotals
    from ccnl_engine.payroll.period.services_run_context import RunContext

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
    ctx: RunContext, report: CapabilityReport, events: _EventTotals
) -> tuple[ModelLimitation, ...]:
    """Return the limitations that concern the run, engine ones first.

    Args:
        ctx: Context of the run.
        report: Capability report of the run.
        events: Totals of the events of the run: the engine limitations
            whose path they took, besides those of the pay chain, and the
            INPS base they add (:func:`paid_month_paths`).

    Returns:
        The applicable limitations, each once.
    """
    traversed = (
        events.limitations
        | paid_month_paths(ctx, events.inps_base)
        | enam_paths(ctx)
        | provisional_paths(ctx)
        | tfr_compensation_paths(ctx)
        | minimum_base_paths(ctx)
    )
    facts = limitation_facts(ctx, report, traversed)
    candidates = (*ctx.repo.load_engine_limitations(), *ctx.contract.ccnl.limitations)
    return tuple(
        limitation for limitation in candidates if limitation.applies_to(facts)
    )
