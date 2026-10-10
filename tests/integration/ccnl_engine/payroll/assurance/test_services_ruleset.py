"""A run reports the rulesets it read, with their kind and readiness."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models import BlockerCode
from ccnl_engine.payroll.assurance.policies_engine_mode import EngineMode
from ccnl_engine.payroll.assurance.rules_assessment import NO_TRACKED_READINESS
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.provenance.ruleset.models import RulesetReadiness
from ccnl_engine.provenance.ruleset.models_assurance import RulesetKind
from tests.integration.ccnl_engine.contract.catalog.builders_anonymous_repository import (  # noqa: E501
    AnonymousCcnlRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import TaxSector
    from ccnl_engine.payroll.period.results import PeriodResult
    from ccnl_engine.tax.annual.models import YearRules

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


class _NoSommaEsenteRepository(BundledKnowledgeRepository):
    """Bundled rules of a year whose somma esente is not bundled."""

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return the bundled year rules without their somma esente.

        Returns:
            The year rules.
        """
        rules = super().load_year_rules(year, sector, num_employees)
        return rules.model_copy(update={"somma_esente": None})


def test_a_year_without_somma_esente_reports_no_somma_ruleset() -> None:
    """The somma esente file is reported only when the year bundles it."""
    with_somma = {r.id for r in _run().rulesets}
    without = {r.id for r in _run(_NoSommaEsenteRepository()).rulesets}

    assert "tax/2026/somma-esente" in with_somma
    assert "tax/2026/somma-esente" not in without
