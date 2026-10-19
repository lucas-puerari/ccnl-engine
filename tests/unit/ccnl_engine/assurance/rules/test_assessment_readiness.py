"""Assessment of a run under each mode: readiness blocks only operational."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.assurance.models import BlockerCode
from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.assurance.rules import NO_TRACKED_READINESS, assess
from ccnl_engine.capability.results import CapabilityReport
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from tests.unit.ccnl_engine.provenance.ruleset.builders import (
    ccnl_ruleset,
    tax_ruleset,
)

if TYPE_CHECKING:
    from ccnl_engine.assurance.models import ResultAssurance
    from ccnl_engine.provenance.ruleset.assurance.models import RulesetAssurance

_SIMULATION = EngineMode.SIMULATION
_OPERATIONAL = EngineMode.OPERATIONAL
_TAX = tax_ruleset("tax/2026/industria")
_PRODUCTION = ccnl_ruleset(RulesetReadiness.PRODUCTION)
_PAID = date(2026, 6, 27)


def _clean_run(
    rulesets: tuple[RulesetAssurance, ...],
    mode: EngineMode,
    payment_date: date = _PAID,
) -> ResultAssurance:
    """Assess a run that nothing but readiness could block.

    Returns:
        The assurance of the run.
    """
    report = CapabilityReport(
        catalog_year=2026,
        gaps=(),
        rule_sources={"irpef": ProvenanceStatus.DERIVED},
        caller_supplied={},
    )
    return assess((), (), report, rulesets, mode, payment_date)


def _readiness_details(assurance: ResultAssurance) -> list[str]:
    return [
        b.detail
        for b in assurance.blockers
        if b.code is BlockerCode.RULESET_NOT_PRODUCTION
    ]


@pytest.mark.parametrize("mode", list(EngineMode))
def test_a_production_ccnl_is_payable_in_both_modes(mode: EngineMode) -> None:
    """Operational adds nothing when every tracked ruleset is production."""
    assurance = _clean_run((_PRODUCTION, _TAX), mode)

    assert assurance.is_payable
    assert assurance.mode is mode
    assert assurance.rulesets == (_PRODUCTION, _TAX)


@pytest.mark.parametrize(
    ("readiness", "confidence"),
    [
        (RulesetReadiness.EXPLORATORY, VerificationStatus.UNVERIFIED),
        (RulesetReadiness.REVIEWED, VerificationStatus.VERIFIED),
        (RulesetReadiness.REVIEWED, VerificationStatus.UNVERIFIED),
        (RulesetReadiness.PRODUCTION, VerificationStatus.UNVERIFIED),
    ],
)
def test_a_ccnl_short_of_production_blocks_only_operational(
    readiness: RulesetReadiness, confidence: VerificationStatus
) -> None:
    """Simulation reports the tier; operational blocks on it."""
    rulesets = (ccnl_ruleset(readiness, confidence, "ccnl/y"), _TAX)

    simulated = _clean_run(rulesets, _SIMULATION)
    operational = _clean_run(rulesets, _OPERATIONAL)

    assert simulated.is_payable
    assert not operational.is_payable
    assert _readiness_details(operational) == ["ccnl/y"]
    (blocker,) = operational.blockers
    assert blocker.feature is None
    assert "simulation mode" in blocker.remediation


def test_untracked_rulesets_never_raise_a_readiness_blocker() -> None:
    """Tax readiness is not tracked: only the CCNL tier is enforced."""
    assurance = _clean_run((_PRODUCTION, _TAX, tax_ruleset("tax/x")), _OPERATIONAL)

    assert _readiness_details(assurance) == []


def test_operational_fails_closed_without_a_tracked_ruleset() -> None:
    """A run whose CCNL identity is missing cannot be cleared."""
    simulated = _clean_run((_TAX,), _SIMULATION)
    operational = _clean_run((_TAX,), _OPERATIONAL)

    assert simulated.is_payable
    assert _readiness_details(operational) == [NO_TRACKED_READINESS]
    assert not operational.is_payable


def _due(review_due: date | None) -> RulesetAssurance:
    return ccnl_ruleset(
        RulesetReadiness.PRODUCTION, ruleset_id="ccnl/y", review_due=review_due
    )


def test_a_production_ccnl_past_its_review_date_blocks_operational() -> None:
    """A review due before the payment date leaves the tier out of date."""
    rulesets = (_due(date(2026, 6, 26)), _TAX)

    operational = _clean_run(rulesets, _OPERATIONAL)

    assert not operational.is_payable
    (blocker,) = operational.blockers
    assert blocker.code is BlockerCode.RULESET_NOT_PRODUCTION
    assert blocker.feature is None
    assert blocker.detail == "ccnl/y"
    assert "2026-06-26" in blocker.remediation
    assert "2026-06-27" in blocker.remediation
    assert "simulation mode" in blocker.remediation


@pytest.mark.parametrize(
    "review_due", [date(2026, 6, 27), date(2027, 1, 31), None], ids=str
)
def test_a_review_not_yet_overdue_keeps_the_ccnl_payable(
    review_due: date | None,
) -> None:
    """The due day itself, a later day or no date at all do not block."""
    assurance = _clean_run((_due(review_due), _TAX), _OPERATIONAL)

    assert assurance.is_payable


def test_simulation_ignores_an_overdue_review() -> None:
    """Simulation reports readiness without enforcing it, dates included."""
    assurance = _clean_run((_due(date(2026, 1, 31)), _TAX), _SIMULATION)

    assert assurance.is_payable


def test_a_ccnl_short_of_production_keeps_its_own_remediation() -> None:
    """A ruleset already short of production raises one blocker, not two."""
    ruleset = ccnl_ruleset(
        RulesetReadiness.REVIEWED, ruleset_id="ccnl/y", review_due=date(2026, 1, 31)
    )

    (blocker,) = _clean_run((ruleset, _TAX), _OPERATIONAL).blockers

    assert blocker.detail == "ccnl/y"
    assert "promote it" in blocker.remediation
