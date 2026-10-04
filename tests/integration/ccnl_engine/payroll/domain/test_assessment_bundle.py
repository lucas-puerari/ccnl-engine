"""Assurance of the bundled CCNLs: the first level of each, June 2026.

Every CCNL of the bundle is run once, for its first level, on a regular run
of June 2026 with no event.  A run the engine rejects before producing a
result is left out: it exposes no amount to pay.
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
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.results import BlockerCode
from tests.fixtures.seniority import new_hire

_WEAK = frozenset({"assumed", "missing"})


def _june(engine: PayrollEngine, slug: str, level: str) -> PeriodResult | None:
    try:
        return engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 6),
                payment_date=date(2026, 6, 27),
                employment=Employment(
                    ccnl_slug=slug, level_code=level, seniority=new_hire()
                ),
                employer=EmployerProfile(headcount=Headcount(50)),
            )
        )
    except (CcnlEngineError, ValueError):
        return None


@pytest.fixture(scope="module")
def results() -> dict[str, PeriodResult]:
    """Return the June 2026 result of each CCNL that produces one.

    Returns:
        Results by CCNL id.
    """
    engine, repo = PayrollEngine.bundled(), BundledKnowledgeRepository()
    computed: dict[str, PeriodResult] = {}
    for info in PayrollEngine.list_contracts():
        slug = f"{info.ccnl_id}.json"
        result = _june(engine, slug, repo.load_ccnl(slug).levels[0].code)
        if result is not None:
            computed[info.ccnl_id] = result
    return computed


def test_most_contracts_produce_a_result(results: dict[str, PeriodResult]) -> None:
    """The scan is not vacuous."""
    assert len(results) >= 120


def test_no_payable_result_has_an_open_coverage_or_weak_rule(
    results: dict[str, PeriodResult],
) -> None:
    """Payability never contradicts the report, the issues or the sources."""
    contradictions = [
        ccnl_id
        for ccnl_id, result in results.items()
        if result.is_payable
        and (
            result.capability_report.gaps
            or result.issues
            or result.capability_report.caller_supplied
            or _WEAK & set(result.capability_report.rule_sources.values())
        )
    ]
    assert contradictions == []


def test_coverage_axis_is_the_report_status(
    results: dict[str, PeriodResult],
) -> None:
    """Every gap of the report is a blocker of the same feature."""
    for result in results.values():
        gaps = [gap.feature for gap in result.capability_report.gaps]
        blocked = [
            b.feature
            for b in result.blockers
            if b.code is BlockerCode.CAPABILITY_NOT_COMPUTED
        ]
        assert result.assurance.coverage is result.capability_report.status
        assert blocked == gaps


def test_ordinary_runs_have_no_coverage_gap(
    results: dict[str, PeriodResult],
) -> None:
    """No unsupported capability applies to an ordinary month of any CCNL."""
    gapped = {
        ccnl_id: [gap.feature for gap in result.capability_report.gaps]
        for ccnl_id, result in results.items()
        if result.capability_report.gaps
    }
    assert gapped == {}
    assert all(r.assurance.coverage == "complete" for r in results.values())


def test_every_result_names_its_rulesets(results: dict[str, PeriodResult]) -> None:
    """The CCNL, tax and INPS rulesets of the year are always read."""
    repo = BundledKnowledgeRepository()
    for ccnl_id, result in results.items():
        ids = {ruleset.id for ruleset in result.rulesets}
        identities = [ruleset.identity for ruleset in result.rulesets]
        assert repo.load_ccnl(f"{ccnl_id}.json").ruleset in identities
        assert any(i.startswith("tax/2026/") for i in ids)
        assert any(i.startswith("inps/2026/") for i in ids)


def test_no_bundled_result_is_payable_today(
    results: dict[str, PeriodResult],
) -> None:
    """The somma esente rule is assumed, so every result is blocked by it.

    Documented in the trust pages: amounts are for simulation until the
    blocked rules are sourced.
    """
    somma = (BlockerCode.RULE_SOURCE_WEAK, "somma_esente", "assumed")
    assert not any(result.is_payable for result in results.values())
    assert all(
        somma in {(b.code, b.feature, b.detail) for b in result.blockers}
        for result in results.values()
    )


def test_open_limitations_block_where_they_apply(
    results: dict[str, PeriodResult],
) -> None:
    """Each blocking limitation of a run is one blocker; most runs have none.

    An ordinary month executes no work-rule capability and no apprenticeship
    path, so only the limitations of every run of a CCNL (an unverified
    INPS rate, a salary table from a proxy) are recorded: a minority.
    """
    limited = 0
    for result in results.values():
        blocking = [lim.id for lim in result.assurance.limitations if lim.blocks]
        blocked = [
            b.detail for b in result.blockers if b.code is BlockerCode.OPEN_LIMITATION
        ]
        assert blocked == blocking
        limited += bool(blocking)
    assert 0 < limited < len(results) // 3
