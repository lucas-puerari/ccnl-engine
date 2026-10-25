"""A run reports the provenance of the payable rules it read.

A rule whose status is ``missing`` makes the result incomplete; the weakest
status of each executed capability is in the capability report.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.assurance.models import BlockerCode
from ccnl_engine.assurance.rule_source.services import (
    MISSING_SOURCE_CODE,
    RuleSource,
    missing_source_issues,
    weakest_by_capability,
)
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.fact.inputs import EmploymentPeriod
from ccnl_engine.family.inputs import (
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.inputs import NoPensionFund, WorkerCategory
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.run.types import PeriodId
from tests.integration.ccnl_engine.family.builders import (
    declared_dependent,
)
from tests.integration.ccnl_engine.irpef.declaration.builders import (
    RENEWAL_WAIVED,
)
from tests.integration.ccnl_engine.surtax.residence.builders import (
    COMUNE_BELFIORE,
    REGIONE,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import TaxSector
    from ccnl_engine.period.results import PeriodResult
    from ccnl_engine.sector.models import YearRules

_METALMECCANICO = "metalmeccanico-federmeccanica"
#: A CCNL whose salary table still reads assumed rules.
_AGENTI = "agenti-immobiliari-fiaip"
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
    fields: dict[str, object] = {
        "ccnl_id": _METALMECCANICO,
        "level_code": "C3",
        "category": WorkerCategory.IMPIEGATO,
        "current_year": employment_only(),
    } | kwargs
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        seniority=new_hire(),
        tfr_treasury_fund=False,
        pension_fund=NoPensionFund(),
        employer=EmployerProfile(headcount=Headcount(50)),
        opening_state=PeriodState.zero(),
        employment_period=EmploymentPeriod(date(2026, 3, 1)),
        **fields,  # type: ignore[arg-type]
    )
    return calculate_period(
        request, repo=repo or bundled_repository(), resolver=bundled_policies()
    )


class TestBundledRun:
    """Bundled data holds no ``missing`` rule, so no source issue is raised."""

    def test_report_holds_the_weakest_status_per_capability(self) -> None:
        """Executed capabilities report the status of the rules they read."""
        result = _run()
        sources = result.capability_report.rule_sources
        # The industria tax rules, the INPS and TFR rules of industria and
        # the metalmeccanico salary table and seniority were re-checked
        # against their signed texts: verified.
        assert sources["irpef"] is ProvenanceStatus.VERIFIED
        assert sources["tfr"] is ProvenanceStatus.VERIFIED
        assert sources["inps_employer"] is ProvenanceStatus.VERIFIED
        assert sources["base_salary"] is ProvenanceStatus.VERIFIED
        # The somma esente sits in its own ruleset, quoted from the law.
        assert sources["somma_esente"] is ProvenanceStatus.VERIFIED
        # A known seniority decides the increments, so their rule is read.
        assert sources["seniority"] is ProvenanceStatus.VERIFIED
        assert all(i.code != MISSING_SOURCE_CODE for i in result.issues)

    def test_assumed_rules_block_payability_without_an_issue(self) -> None:
        """An assumed rule is a blocker, not an issue: the calculation is final.

        The worker resides in Alghero, whose surtax rows are not assumed,
        and waived the renewal regime on the minimo in writing.
        """
        result = _run(
            ccnl_id=_AGENTI,
            level_code="IV",
            category=None,
            regione=REGIONE,
            comune_belfiore=COMUNE_BELFIORE,
            prior_year=RENEWAL_WAIVED,
        )
        weak = {
            (b.feature, b.detail)
            for b in result.blockers
            if b.code is BlockerCode.RULE_SOURCE_WEAK
        }
        assert result.assurance.calculation is CalculationStatus.FINAL
        assert ("base_salary", "assumed") in weak
        assert all(detail != "derived" for _, detail in weak)
        assert not result.is_payable

    def test_surtax_and_family_rules_are_reported_when_computed(self) -> None:
        """Tables loaded for the run report their record.

        The regional table is checked on the MEF pages (``verified``); Modena
        (F257) published no 2026 delibera, so its row carries the 2025 rates
        with its own ``assumed`` record.
        """
        family = FamilyComposition(
            dependents=(declared_dependent(relationship=DependentRelationship.SPOUSE),)
        )
        result = _run(
            regione="IT-45",
            comune_belfiore="F257",
            family_composition=family,
            current_year=employment_only(),
        )
        sources = result.capability_report.rule_sources
        assert sources["addizionale_regionale"] is ProvenanceStatus.VERIFIED
        assert sources["addizionale_comunale"] is ProvenanceStatus.ASSUMED
        assert sources["family_deductions"] is ProvenanceStatus.VERIFIED
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
