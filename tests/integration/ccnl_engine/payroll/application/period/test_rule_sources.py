"""A run reports the provenance of the payable rules it read.

A rule whose status is ``missing`` makes the result incomplete; the weakest
status of each executed capability is in the capability report.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.period._rule_sources import (
    MISSING_SOURCE_CODE,
    RuleSource,
    missing_source_issues,
    weakest_by_capability,
)
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import TaxSector
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.tax.domain.ruleset import YearRules

_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_MISSING = RuleProvenance(status=ProvenanceStatus.MISSING, note="no source")


class _MissingTfrSource(BundledKnowledgeRepository):
    """Bundled rules whose TFR divisor has no source."""

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return the bundled rules with a ``missing`` TFR record.

        Returns:
            The rules of ``year``.
        """
        rules = super().load_year_rules(year, sector, num_employees)
        tfr = rules.tfr.model_copy(update={"provenance": _MISSING})
        return rules.model_copy(update={"tfr": tfr})


def _run(
    repo: BundledKnowledgeRepository | None = None, **kwargs: object
) -> PeriodResult:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        seniority=new_hire(),
        employer=EmployerProfile(headcount=Headcount(50)),
        opening_state=PeriodState.zero(),
        **kwargs,  # type: ignore[arg-type]
    )
    return calculate_period(request, repo=repo)


class TestBundledRun:
    """Bundled data holds no ``missing`` rule, so no source issue is raised."""

    def test_report_holds_the_weakest_status_per_capability(self) -> None:
        """Executed capabilities report the status of the rules they read."""
        result = _run()
        sources = result.capability_report.rule_sources
        assert sources["irpef"] is ProvenanceStatus.DERIVED
        assert sources["tfr"] is ProvenanceStatus.DERIVED
        assert sources["somma_esente"] is ProvenanceStatus.ASSUMED
        # A known seniority decides the increments, so their rule is read.
        assert "seniority" in sources
        assert all(i.code != MISSING_SOURCE_CODE for i in result.issues)

    def test_assumed_rules_block_payability_without_an_issue(self) -> None:
        """An assumed rule is a blocker, not an issue: the calculation is final."""
        result = _run()
        weak = {
            (b.feature, b.detail)
            for b in result.blockers
            if b.code is BlockerCode.RULE_SOURCE_WEAK
        }
        assert result.assurance.calculation is CalculationStatus.FINAL
        assert ("somma_esente", "assumed") in weak
        assert all(detail != "derived" for _, detail in weak)
        assert not result.is_payable

    def test_surtax_and_family_rules_are_reported_when_computed(self) -> None:
        """Tables loaded for the run report their record.

        The regional table is taken from the MEF pages (``derived``); Modena
        (F257) published no 2026 delibera, so its row carries the 2025 rates
        with its own ``assumed`` record.
        """
        family = FamilyComposition(
            dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
        )
        result = _run(
            regione="IT-45", comune_belfiore="F257", family_composition=family
        )
        sources = result.capability_report.rule_sources
        assert sources["addizionale_regionale"] is ProvenanceStatus.DERIVED
        assert sources["addizionale_comunale"] is ProvenanceStatus.ASSUMED
        assert sources["family_deductions"] is ProvenanceStatus.DERIVED
        ids = [ruleset.id for ruleset in result.rulesets]
        assert ids == sorted(ids)
        assert len(ids) == len(set(ids))
        assert {"tax/2026/family-deductions", "surtax/2026/regionale"} <= set(ids)


class TestMissingSource:
    """A ``missing`` rule makes the result incomplete and names the rule."""

    def test_missing_tfr_source_makes_the_result_incomplete(self) -> None:
        """The TFR accrual rests on a value no source backs."""
        result = _run(_MissingTfrSource())
        (issue,) = [i for i in result.issues if i.code == MISSING_SOURCE_CODE]
        assert result.assurance.calculation is CalculationStatus.INCOMPLETE
        assert issue.status is CalculationStatus.INCOMPLETE
        assert "tfr: rule tax/2026/industria:tfr has no source" in issue.message
        assert result.capability_report.rule_sources["tfr"] is ProvenanceStatus.MISSING


class TestAggregation:
    """Statuses combine per capability; only ``missing`` raises an issue."""

    _SOURCES = (
        RuleSource("irpef", "a", ProvenanceStatus.DERIVED),
        RuleSource("irpef", "b", ProvenanceStatus.ASSUMED),
        RuleSource("irpef", "c", ProvenanceStatus.VERIFIED),
        RuleSource("tfr", "d", ProvenanceStatus.MISSING),
    )

    def test_weakest_status_per_capability(self) -> None:
        """The weakest status of each capability wins."""
        assert weakest_by_capability(self._SOURCES) == {
            "irpef": ProvenanceStatus.ASSUMED,
            "tfr": ProvenanceStatus.MISSING,
        }

    def test_one_issue_per_missing_rule(self) -> None:
        """Only the missing rule becomes an issue."""
        (issue,) = missing_source_issues(self._SOURCES)
        assert issue.code == MISSING_SOURCE_CODE
        assert "rule d" in issue.message
