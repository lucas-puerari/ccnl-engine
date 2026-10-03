"""Result assurance values and their aggregation over several runs."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.domain.assurance import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
    decide_payability,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetIdentity,
    SourceType,
    VerificationStatus,
)

_GAP = ResultBlocker(
    BlockerCode.CAPABILITY_NOT_COMPUTED, "inail", "feature_absent", "compute it"
)
_FACT = ResultBlocker(BlockerCode.MISSING_FACT, None, "sector", "supply it")


def _ruleset(ruleset_id: str) -> RulesetIdentity:
    return RulesetIdentity(
        id=ruleset_id,
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="unavailable",
        source_type=SourceType.DERIVED,
        source_hash="0" * 64,
        verification_status=VerificationStatus.UNVERIFIED,
    )


def _assurance(
    *blockers: ResultBlocker,
    calculation: CalculationStatus = CalculationStatus.FINAL,
    coverage: CoverageStatus = CoverageStatus.COMPLETE,
    evidence: EvidenceStatus = EvidenceStatus.DERIVED,
    rulesets: tuple[RulesetIdentity, ...] = (),
) -> ResultAssurance:
    return ResultAssurance(
        calculation=calculation,
        coverage=coverage,
        evidence=evidence,
        rulesets=rulesets,
        payability=decide_payability(blockers),
        blockers=blockers,
    )


class TestCombine:
    """The assurance of several runs, e.g. a year."""

    def test_axes_take_the_worst_and_lists_are_unique(self) -> None:
        """Blockers and rulesets appear once, in order of first appearance."""
        tax, ccnl = _ruleset("tax/2026"), _ruleset("ccnl/x")
        clean = _assurance(rulesets=(tax,))
        flagged = _assurance(
            _FACT,
            _GAP,
            calculation=CalculationStatus.PROVISIONAL,
            coverage=CoverageStatus.INCOMPLETE,
            evidence=EvidenceStatus.ASSUMED,
            rulesets=(ccnl, tax),
        )

        year = ResultAssurance.combine((clean, flagged, flagged))

        assert year.calculation is CalculationStatus.PROVISIONAL
        assert year.coverage is CoverageStatus.INCOMPLETE
        assert year.evidence is EvidenceStatus.ASSUMED
        assert year.rulesets == (tax, ccnl)
        assert year.blockers == (_FACT, _GAP)
        assert year.payability is Payability.NOT_PAYABLE
        assert not year.is_payable

    def test_payable_runs_give_a_payable_year(self) -> None:
        """A year is payable when every run is."""
        year = ResultAssurance.combine((_assurance(), _assurance()))

        assert year.is_payable
        assert year.blockers == ()

    def test_no_run_cannot_be_combined(self) -> None:
        """A year without a run has no assurance."""
        with pytest.raises(ValueError, match="no run"):
            ResultAssurance.combine(())


def test_payability_is_blocked_by_any_blocker() -> None:
    """The default policy: every blocker blocks."""
    assert decide_payability(()) is Payability.PAYABLE
    assert decide_payability((_FACT,)) is Payability.NOT_PAYABLE


def test_coverage_worst_of_nothing_is_complete() -> None:
    """With no run to compare, nothing is missing."""
    assert CoverageStatus.worst(()) is CoverageStatus.COMPLETE
    assert CoverageStatus.worst(list(CoverageStatus)) is CoverageStatus.INCOMPLETE


def test_evidence_weakest_reads_provenance_values() -> None:
    """The weakest backing wins; no record at all is missing evidence."""
    assert EvidenceStatus.weakest(("derived", "verified")) is EvidenceStatus.DERIVED
    assert EvidenceStatus.weakest(("derived", "assumed")) is EvidenceStatus.ASSUMED
    assert EvidenceStatus.weakest(()) is EvidenceStatus.MISSING


def test_blocker_is_hashable_and_comparable() -> None:
    """Blockers are values: equal fields, equal blockers."""
    copy = ResultBlocker(BlockerCode.MISSING_FACT, None, "sector", "supply it")

    assert copy == _FACT
    assert len({copy, _FACT}) == 1
