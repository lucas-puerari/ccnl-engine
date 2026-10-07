"""Every bundled CCNL in both modes: operational adds readiness, nothing else.

The first level of each CCNL runs a regular June 2026 run in ``simulation``
and in ``operational`` mode.  A run the engine rejects before producing a
result is left out.  No count of the bundle is frozen: the invariants hold
whatever the readiness of each CCNL.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    CcnlEngineError,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.catalog import RulesetKind
from ccnl_engine.inputs import Permanent
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.results import BlockerCode

type Pair = tuple[PeriodResult, PeriodResult]


def _june(engine: PayrollEngine, slug: str, level: str) -> PeriodResult | None:
    try:
        return engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 6),
                payment_date=date(2026, 6, 27),
                employment=Employment(
                    ccnl_slug=slug, level_code=level, contract_type=Permanent()
                ),
                employer=EmployerProfile(headcount=Headcount(50)),
            )
        )
    except (CcnlEngineError, ValueError):
        return None


@pytest.fixture(scope="module")
def pairs() -> dict[str, Pair]:
    """Return the simulation and operational result of each CCNL that runs.

    Returns:
        Result pairs by CCNL id.
    """
    simulation = PayrollEngine.bundled()
    operational = PayrollEngine.bundled(mode="operational")
    repo = BundledKnowledgeRepository()
    computed: dict[str, Pair] = {}
    for summary in PayrollEngine.list_contracts():
        slug = f"{summary.ccnl_id}.json"
        level = repo.load_ccnl(slug).levels[0].code
        simulated = _june(simulation, slug, level)
        if simulated is not None:
            cleared = _june(operational, slug, level)
            assert cleared is not None, f"operational rejected {slug}"
            computed[summary.ccnl_id] = (simulated, cleared)
    return computed


def test_most_contracts_run_in_both_modes(pairs: dict[str, Pair]) -> None:
    """The scan is not vacuous; operational rejects no run simulation runs."""
    assert len(pairs) >= 120


def test_every_run_reports_its_ccnl_readiness(pairs: dict[str, Pair]) -> None:
    """The CCNL ruleset of every run carries the tier of the catalog."""
    tiers = {str(s.ccnl_id): s.readiness for s in PayrollEngine.list_contracts()}
    for ccnl_id, (simulated, _) in pairs.items():
        (ccnl,) = [r for r in simulated.rulesets if r.kind is RulesetKind.CCNL]
        assert ccnl.readiness is tiers[ccnl_id]


def test_operational_adds_exactly_the_readiness_blockers(
    pairs: dict[str, Pair],
) -> None:
    """Same amounts and blockers, plus one per CCNL short of production."""
    for simulated, operational in pairs.values():
        (ccnl,) = [r for r in simulated.rulesets if r.kind is RulesetKind.CCNL]
        expected = () if ccnl.is_production else (ccnl.id,)
        added = [b for b in operational.blockers if b not in simulated.blockers]
        assert operational.period_net == simulated.period_net
        assert tuple(b.detail for b in added) == expected
        assert all(b.code is BlockerCode.RULESET_NOT_PRODUCTION for b in added)
        assert all(
            b.code is not BlockerCode.RULESET_NOT_PRODUCTION for b in simulated.blockers
        )


def test_operational_pays_only_production_rulesets(pairs: dict[str, Pair]) -> None:
    """Operational pays when simulation does and the CCNL is production."""
    for simulated, operational in pairs.values():
        (ccnl,) = [r for r in simulated.rulesets if r.kind is RulesetKind.CCNL]
        assert operational.is_payable == (simulated.is_payable and ccnl.is_production)
