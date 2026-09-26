"""Knowledge repository that serves the bundled 2026 rules as 2027 rules.

The 2027 tax tables are not bundled, so a run of tax year 2027 fails with
``UnsupportedTaxYearError``.  Tests of the year change need a 2027 run: this
repository answers a 2027 request with the bundled 2026 rules relabelled as
2027.  The amounts are 2026 law; only differential assertions (with and
without a carried obligation) are meaningful on its results.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL, TaxSector
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules
    from ccnl_engine.tax.domain.variable_pay import VariablePayRules

SOURCE_YEAR = 2026
TARGET_YEAR = 2027


class NextYearRepository:
    """Bundled repository with the 2026 rules standing in for 2027."""

    def __init__(self) -> None:
        """Wrap the bundled repository."""
        self._bundled = BundledKnowledgeRepository()

    @staticmethod
    def _source(year: int) -> int:
        return SOURCE_YEAR if year == TARGET_YEAR else year

    def load_ccnl(self, filename: str) -> CCNL:
        """Return the bundled CCNL.

        Returns:
            The bundled CCNL for ``filename``.
        """
        return self._bundled.load_ccnl(filename)

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return the tax rules of ``year``, 2026 rules for 2027.

        Returns:
            The rules, labelled with ``year``.
        """
        rules = self._bundled.load_year_rules(self._source(year), sector, num_employees)
        return rules.model_copy(update={"year": year})

    def load_surtax_rules(self, year: int) -> SurtaxRules:
        """Return the surtax rules of ``year``, 2026 rules for 2027.

        Returns:
            The rules, labelled with ``year``.
        """
        rules = self._bundled.load_surtax_rules(self._source(year))
        return rules.model_copy(update={"year": year})

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        """Return the capability catalog of ``year``, 2026 for 2027.

        Returns:
            The catalog, labelled with ``year``.
        """
        catalog = self._bundled.load_capability_catalog(self._source(year))
        return replace(catalog, year=year)

    def load_variable_pay_rules(self, year: int) -> VariablePayRules:
        """Return the variable-pay rules of ``year``, 2026 rules for 2027.

        Returns:
            The rules, labelled with ``year``.
        """
        rules = self._bundled.load_variable_pay_rules(self._source(year))
        return rules.model_copy(update={"year": year})

    def load_family_deduction_rules(self, year: int) -> FamilyDeductionRules:
        """Return the family deduction rules of ``year``, 2026 rules for 2027.

        Returns:
            The rules, labelled with ``year``.
        """
        rules = self._bundled.load_family_deduction_rules(self._source(year))
        return rules.model_copy(update={"year": year})
