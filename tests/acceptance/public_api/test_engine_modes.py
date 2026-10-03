"""Simulation and operational modes, and readiness before and after a run.

Both modes compute the same amounts.  ``operational`` adds one
``ruleset_not_production`` blocker for the CCNL ruleset when it is not
``production``, and nothing else; ``simulation`` reports readiness without
enforcing it.  The readiness a run reports is the one the catalog reports
before any run.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    BlockerCode,
    EmployerProfile,
    Employment,
    EngineMode,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
    RulesetKind,
    RulesetReadiness,
    YearInput,
)

_SIMULATION = PayrollEngine.bundled()
_OPERATIONAL = PayrollEngine.bundled(mode="operational")
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METALMECCANICO = "metalmeccanico-federmeccanica"
_EMPLOYMENT = Employment(ccnl_slug=f"{_METALMECCANICO}.json", level_code="C3")


def _june(engine: PayrollEngine) -> PeriodResult:
    return engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
        )
    )


def test_default_mode_is_simulation() -> None:
    """An engine built without a mode simulates."""
    assert PayrollEngine.bundled().mode is EngineMode.SIMULATION
    assert PayrollEngine().mode is EngineMode.SIMULATION
    assert _OPERATIONAL.mode is EngineMode.OPERATIONAL
    assert PayrollEngine.bundled(mode=EngineMode.OPERATIONAL).mode is (
        EngineMode.OPERATIONAL
    )


def test_unknown_mode_is_invalid_input() -> None:
    """A mode typo is rejected when the engine is built, not on a run."""
    with pytest.raises(InvalidInputError, match=r"PayrollEngine\.mode must be one of"):
        PayrollEngine.bundled(mode="production")  # type: ignore[arg-type]


def test_operational_adds_only_the_readiness_blocker() -> None:
    """Same amounts; one more blocker, naming the reviewed CCNL ruleset."""
    simulated, operational = _june(_SIMULATION), _june(_OPERATIONAL)
    ccnl_id = f"ccnl/{_METALMECCANICO}"

    assert operational.period_net == simulated.period_net
    assert operational.period_gross == simulated.period_gross
    assert operational.rulesets == simulated.rulesets
    (extra,) = set(operational.blockers) - set(simulated.blockers)
    assert (extra.code, extra.feature, extra.detail) == (
        BlockerCode.RULESET_NOT_PRODUCTION,
        None,
        ccnl_id,
    )
    assert set(simulated.blockers) <= set(operational.blockers)
    assert simulated.assurance.mode is EngineMode.SIMULATION
    assert operational.assurance.mode is EngineMode.OPERATIONAL
    assert not operational.is_payable


def test_run_reports_the_readiness_the_catalog_reports() -> None:
    """``inspect_ruleset`` before a run equals the CCNL entry of the run."""
    inspected = _SIMULATION.inspect_ruleset(_METALMECCANICO)
    (ccnl,) = [r for r in _june(_SIMULATION).rulesets if r.kind is RulesetKind.CCNL]
    (summary,) = [
        s for s in PayrollEngine.list_contracts() if s.ccnl_id == _METALMECCANICO
    ]

    assert ccnl == inspected
    assert inspected.readiness is summary.readiness is RulesetReadiness.REVIEWED
    assert inspected.source_hash == inspected.identity.source_hash
    assert _SIMULATION.inspect_ruleset(summary.cnel_code) == inspected


def test_tax_and_inps_readiness_is_not_tracked() -> None:
    """Only CCNL rulesets carry a tier; the others say so with ``None``."""
    others = [r for r in _june(_SIMULATION).rulesets if r.kind is not RulesetKind.CCNL]

    assert {r.kind for r in others} >= {RulesetKind.TAX, RulesetKind.INPS}
    assert all(r.readiness is None and not r.readiness_tracked for r in others)


def test_an_operational_year_is_blocked_on_every_run() -> None:
    """Each run of an operational year carries the readiness blocker."""
    year = _OPERATIONAL.calculate_year(
        YearInput(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER)
    )

    assert year.assurance.mode is EngineMode.OPERATIONAL
    assert all(r.mode is EngineMode.OPERATIONAL for r in year.period_results)
    assert all(
        any(b.code is BlockerCode.RULESET_NOT_PRODUCTION for b in r.blockers)
        for r in year.period_results
    )
    assert not year.is_payable
