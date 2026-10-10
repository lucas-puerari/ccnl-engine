"""Result assurance values and their aggregation over several runs."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.assurance.models import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
    decide_payability,
)
from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.assurance.policies_engine_mode import EngineMode
from ccnl_engine.provenance.ruleset.models import VerificationStatus
from tests.unit.ccnl_engine.provenance.ruleset.builders_rulesets import tax_ruleset

if TYPE_CHECKING:
    from ccnl_engine.provenance.ruleset.models_assurance import RulesetAssurance

_GAP = ResultBlocker(
    BlockerCode.CAPABILITY_NOT_COMPUTED, "inail", "unsupported", "compute it"
)
_FACT = ResultBlocker(BlockerCode.MISSING_FACT, None, "sector", "supply it")


def _assurance(
    *blockers: ResultBlocker,
    calculation: CalculationStatus = CalculationStatus.FINAL,
    coverage: CoverageStatus = CoverageStatus.COMPLETE,
    evidence: EvidenceStatus = EvidenceStatus.DERIVED,
    rulesets: tuple[RulesetAssurance, ...] = (),
    mode: EngineMode = EngineMode.SIMULATION,
) -> ResultAssurance:
    return ResultAssurance(
        calculation=calculation,
        coverage=coverage,
        evidence=evidence,
        rulesets=rulesets,
        mode=mode,
        payability=decide_payability(blockers),
        blockers=blockers,
    )


class TestCombine:
    """The assurance of several runs, e.g. a year."""

    def test_axes_take_the_worst_and_lists_are_unique(self) -> None:
        """Blockers and rulesets appear once, in order of first appearance."""
        tax, ccnl = tax_ruleset("tax/2026"), tax_ruleset("ccnl/x")
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

    def test_one_version_read_with_two_contents_blocks_the_year(self) -> None:
        """Rulesets sharing ``id@version`` but not their hash are both kept."""
        tax = tax_ruleset("tax/2026")
        rehashed = replace(
            tax, identity=tax.identity.model_copy(update={"source_hash": "1" * 64})
        )
        relabelled = replace(tax, confidence=VerificationStatus.VERIFIED)

        year = ResultAssurance.combine((
            _assurance(rulesets=(tax,)),
            _assurance(rulesets=(rehashed, relabelled)),
            _assurance(rulesets=(tax,)),
        ))

        assert year.rulesets == (tax, rehashed, relabelled)
        assert [(b.code, b.detail) for b in year.blockers] == [
            (BlockerCode.RULESET_CONFLICT, "tax/2026@2026.1")
        ]
        assert not year.is_payable

    def test_payable_runs_give_a_payable_year(self) -> None:
        """A year is payable when every run is."""
        year = ResultAssurance.combine((_assurance(), _assurance()))

        assert year.is_payable
        assert year.blockers == ()

    def test_mode_is_kept(self) -> None:
        """A year of operational runs is operational."""
        operational = _assurance(mode=EngineMode.OPERATIONAL)

        year = ResultAssurance.combine((operational, operational))

        assert year.mode is EngineMode.OPERATIONAL

    def test_runs_of_different_modes_cannot_be_combined(self) -> None:
        """One policy per aggregate: mixing modes is a programming error."""
        mixed = (_assurance(), _assurance(mode=EngineMode.OPERATIONAL))

        with pytest.raises(ValueError, match="different modes"):
            ResultAssurance.combine(mixed)

    def test_no_run_cannot_be_combined(self) -> None:
        """A year without a run has no assurance."""
        with pytest.raises(ValueError, match="no run"):
            ResultAssurance.combine(())


class TestWithBlockers:
    """Blockers added after the runs, e.g. the runs a year left out."""

    def test_an_added_blocker_makes_a_payable_result_not_payable(self) -> None:
        """The payability is decided again on every blocker."""
        result = _assurance().with_blockers((_FACT,))

        assert result.blockers == (_FACT,)
        assert result.payability is Payability.NOT_PAYABLE

    def test_added_blockers_follow_the_own_and_are_listed_once(self) -> None:
        """A blocker already listed is not repeated."""
        result = _assurance(_GAP).with_blockers((_FACT, _GAP))

        assert result.blockers == (_GAP, _FACT)

    def test_no_added_blocker_keeps_a_payable_result(self) -> None:
        """Nothing added, nothing blocks."""
        assert _assurance().with_blockers(()).is_payable


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
