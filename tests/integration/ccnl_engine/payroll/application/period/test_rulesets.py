"""A run reports the rulesets it read, with their kind and readiness."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.assessment import NO_TRACKED_READINESS
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.provenance.domain.ruleset_assurance import RulesetKind
from ccnl_engine.provenance.domain.ruleset_identity import RulesetReadiness
from tests.fixtures.anonymous_ccnl_repository import AnonymousCcnlRepository

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.service.bundled_knowledge_repository import (
        BundledKnowledgeRepository,
    )

_METALMECCANICO = "metalmeccanico-federmeccanica.json"


def _run(
    repo: BundledKnowledgeRepository | None = None,
    mode: EngineMode = EngineMode.SIMULATION,
) -> PeriodResult:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        employer=EmployerProfile(headcount=Headcount(50)),
        opening_state=PeriodState.zero(),
    )
    return calculate_period(request, repo=repo, mode=mode)


def test_each_ruleset_is_tagged_by_the_loader_that_read_it() -> None:
    """The CCNL tracks a tier; tax and INPS report none."""
    kinds = {r.id: (r.kind, r.readiness) for r in _run().rulesets}

    assert kinds["ccnl/metalmeccanico-federmeccanica"] == (
        RulesetKind.CCNL,
        RulesetReadiness.REVIEWED,
    )
    assert kinds["tax/2026/industria"] == (RulesetKind.TAX, None)
    assert kinds["inps/2026/industria"] == (RulesetKind.INPS, None)


def test_mode_is_recorded_on_the_result() -> None:
    """The result carries the policy it was assessed under."""
    result = _run(mode=EngineMode.OPERATIONAL)

    assert result.mode is EngineMode.OPERATIONAL
    assert result.assurance.mode is EngineMode.OPERATIONAL


def test_a_ccnl_without_identity_is_not_reported_and_fails_closed() -> None:
    """Operational cannot clear a CCNL nothing identifies."""
    result = _run(AnonymousCcnlRepository(), EngineMode.OPERATIONAL)

    assert all(r.kind is not RulesetKind.CCNL for r in result.rulesets)
    readiness = [
        b.detail
        for b in result.blockers
        if b.code is BlockerCode.RULESET_NOT_PRODUCTION
    ]
    assert readiness == [NO_TRACKED_READINESS]
