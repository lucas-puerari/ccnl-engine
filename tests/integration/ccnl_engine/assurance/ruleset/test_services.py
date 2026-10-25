"""A run reports the rulesets it read, with their kind and readiness."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.assurance.models import BlockerCode
from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.assurance.rules import NO_TRACKED_READINESS
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.services import inspect_ruleset, list_contracts
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.provenance.ruleset.assurance.models import RulesetKind
from ccnl_engine.provenance.ruleset.models import RulesetReadiness
from ccnl_engine.run.types import PeriodId
from tests.integration.ccnl_engine.catalog.builders import (
    AnonymousCcnlRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL, TaxSector
    from ccnl_engine.period.results import PeriodResult
    from ccnl_engine.sector.models import YearRules

_METALMECCANICO = "metalmeccanico-federmeccanica"


def _run(
    repo: BundledKnowledgeRepository | None = None,
    mode: EngineMode = EngineMode.SIMULATION,
) -> PeriodResult:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_id=_METALMECCANICO,
        level_code="C3",
        employer=EmployerProfile(headcount=Headcount(50)),
        opening_state=PeriodState.zero(),
    )
    return calculate_period(
        request,
        repo=repo or bundled_repository(),
        mode=mode,
        resolver=bundled_policies(),
    )


def test_each_ruleset_is_tagged_by_the_loader_that_read_it() -> None:
    """The CCNL tracks a tier; tax and INPS report none."""
    kinds = {r.id: (r.kind, r.readiness) for r in _run().rulesets}

    assert kinds["ccnl/metalmeccanico-federmeccanica"] == (
        RulesetKind.CCNL,
        RulesetReadiness.PRODUCTION,
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


class _ReviewDueRepository(BundledKnowledgeRepository):
    """Bundled rules whose CCNL records another review date."""

    def __init__(self, review_due: date) -> None:
        super().__init__()
        self._review_due = review_due

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the bundled CCNL with its review due on the given day.

        Returns:
            The CCNL.
        """
        ccnl = super().load_ccnl(ccnl_id)
        verification = ccnl.verification.model_copy(
            update={"review_due": self._review_due}
        )
        return ccnl.model_copy(update={"verification": verification})


def _readiness_details(result: PeriodResult) -> list[str]:
    return [
        b.detail
        for b in result.blockers
        if b.code is BlockerCode.RULESET_NOT_PRODUCTION
    ]


def test_a_production_ccnl_past_its_review_date_is_not_production() -> None:
    """A review due the day before the payment blocks the operational run."""
    repo = _ReviewDueRepository(date(2026, 3, 26))

    operational = _run(repo, EngineMode.OPERATIONAL)
    simulated = _run(repo, EngineMode.SIMULATION)

    assert _readiness_details(operational) == ["ccnl/metalmeccanico-federmeccanica"]
    assert _readiness_details(simulated) == []
    (ccnl,) = [r for r in operational.rulesets if r.kind is RulesetKind.CCNL]
    assert ccnl.readiness is RulesetReadiness.PRODUCTION
    assert ccnl.review_due == date(2026, 3, 26)


@pytest.mark.parametrize("review_due", [date(2026, 3, 27), date(2026, 12, 31)])
def test_a_review_due_on_or_after_the_payment_keeps_the_tier(review_due: date) -> None:
    """The run pays on 27 March: a review due that day or later is in time."""
    result = _run(_ReviewDueRepository(review_due), EngineMode.OPERATIONAL)

    assert _readiness_details(result) == []


def test_no_bundled_production_ccnl_is_past_its_review_date_in_2026() -> None:
    """Every production CCNL records a review date later than 2026."""
    repo = BundledKnowledgeRepository()
    production = [
        inspect_ruleset(repo, summary.ccnl_id)
        for summary in list_contracts(repo)
        if summary.readiness is RulesetReadiness.PRODUCTION
    ]

    assert production
    assert [
        r.id
        for r in production
        if r.review_due is None or r.review_overdue(date(2026, 12, 31))
    ] == []
