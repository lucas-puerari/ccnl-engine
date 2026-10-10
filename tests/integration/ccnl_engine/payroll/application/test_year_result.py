"""Assurance of a year whose repository changes a ruleset between runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from tests.fixtures.explicit_facts import competence_year

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import TaxSector
    from ccnl_engine.tax.domain.ruleset import YearRules


class _RehashingRepository(BundledKnowledgeRepository):
    """Bundled rules whose tax ruleset changes hash, not version, on each read."""

    def __init__(self) -> None:
        super().__init__()
        self.reads = 0

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return the bundled year rules, rehashed after the first read.

        Returns:
            The year rules.
        """
        rules = super().load_year_rules(year, sector, num_employees)
        self.reads += 1
        if self.reads == 1 or rules.ruleset is None:
            return rules
        rehashed = rules.ruleset.model_copy(update={"source_hash": "f" * 64})
        return rules.model_copy(update={"ruleset": rehashed})


def test_a_ruleset_version_with_two_contents_blocks_the_year() -> None:
    """The year keeps both contents and is not payable."""
    repo = _RehashingRepository()

    year = calculate_competence_year(competence_year(), repo=repo)

    conflicts = [b for b in year.blockers if b.code is BlockerCode.RULESET_CONFLICT]
    assert repo.reads > 1
    assert len(conflicts) == 1
    hashes = {r.source_hash for r in year.rulesets if str(r) == conflicts[0].detail}
    assert len(hashes) == 2
    assert not year.is_payable


def test_a_repository_that_does_not_change_reports_no_conflict() -> None:
    """Identical rulesets read by every run are listed once."""
    year = calculate_competence_year(competence_year())

    names = [str(r) for r in year.rulesets]
    assert len(names) == len(set(names))
    assert BlockerCode.RULESET_CONFLICT not in {b.code for b in year.blockers}
