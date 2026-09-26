"""BundledKnowledgeRepository: reads rules from the package-bundled JSON files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.tax.service.surtax_loaders import load_surtax_rules
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.tax.service.tax_optional_loaders import (
    load_family_deduction_rules,
    load_variable_pay_rules,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL, TaxSector
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules
    from ccnl_engine.tax.domain.variable_pay import VariablePayRules


class BundledKnowledgeRepository:
    """Production implementation of the knowledge repository port.

    Satisfies :class:`~ccnl_engine.payroll.application.knowledge_repository\
.KnowledgeRepository`. Reads from the versioned JSON files bundled inside
    the ``ccnl_engine`` package.  All loader functions are cached, so repeated
    calls for the same arguments return the same (immutable) object without
    re-parsing.
    """

    def load_ccnl(self, filename: str) -> CCNL:  # noqa: PLR6301
        """Return the CCNL for *filename* from the bundled data files.

        Returns:
            The validated, immutable CCNL.
        """
        return load_ccnl(filename)

    def load_year_rules(  # noqa: PLR6301
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return resolved tax year rules for *year*, *sector*, *num_employees*.

        Returns:
            A :class:`~ccnl_engine.tax.domain.ruleset.YearRules` with
            INPS rates resolved for the given headcount.
        """
        return load_year_rules(year, sector, num_employees)

    def load_surtax_rules(self, year: int) -> SurtaxRules:  # noqa: PLR6301
        """Return surtax rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxRules`
            with regionale and comunale rate tables.
        """
        return load_surtax_rules(year)

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:  # noqa: PLR6301
        """Return the capability catalog for *year*.

        Returns:
            A :class:`~ccnl_engine.payroll.domain.capability_catalog.CapabilityCatalog`
            with all declared capabilities for the requested year.
        """
        return load_capability_catalog(year)

    def load_variable_pay_rules(self, year: int) -> VariablePayRules:  # noqa: PLR6301
        """Return the statutory variable-pay rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.domain.variable_pay.VariablePayRules`
            with fringe thresholds, PdR and L. 199/2025 regimes.
        """
        return load_variable_pay_rules(year)

    def load_family_deduction_rules(self, year: int) -> FamilyDeductionRules:  # noqa: PLR6301
        """Return the Art. 12 TUIR family deduction rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.domain.family.FamilyDeductionRules`.
        """
        return load_family_deduction_rules(year)
