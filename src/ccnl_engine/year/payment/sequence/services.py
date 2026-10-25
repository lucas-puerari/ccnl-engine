"""Compute planned payments one after the other on one withholding schedule."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.period.services import calculate_period
from ccnl_engine.year.competence.run.services import run_request

if TYPE_CHECKING:
    from ccnl_engine.assurance.policies import EngineMode
    from ccnl_engine.balance.models import PeriodState
    from ccnl_engine.pay_item.policies import PolicyResolver
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.period.results import PeriodResult
    from ccnl_engine.withholding.schedule.models import WithholdingSchedule
    from ccnl_engine.year.payment.services import PlannedPayment

__all__ = ["Engine", "compute_payments"]


@dataclass(frozen=True)
class Engine:
    """How each payment is computed: knowledge, policies, version and mode."""

    repo: KnowledgeRepository
    resolver: PolicyResolver
    bundle_version: str | None
    mode: EngineMode


def compute_payments(
    payments: tuple[PlannedPayment, ...],
    schedule: WithholdingSchedule,
    opening: PeriodState,
    engine: Engine,
) -> tuple[PeriodResult, ...]:
    """Compute ``payments`` in order, each opening with the state before it.

    Every payment is computed on ``schedule``: which of its slots are paid
    is read from the state each payment opens with, so the conguaglio
    falls on the payment that leaves none unpaid.

    Returns:
        One result per payment, in order.
    """
    results: list[PeriodResult] = []
    state = opening
    for planned in payments:
        request = run_request(
            planned.plan,
            planned.year_plan,
            planned.run,
            planned.payment,
            state,
            schedule,
            uncovered=planned.uncovered,
        )
        result = calculate_period(
            request,
            repo=engine.repo,
            resolver=engine.resolver,
            bundle_version=engine.bundle_version,
            mode=engine.mode,
        )
        results.append(result)
        state = result.closing_state
    return tuple(results)
