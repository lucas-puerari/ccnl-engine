"""KnowledgeRepository port: the engine's interface to the data bundle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ccnl_engine.engine.capability_catalog import CapabilityCatalog
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.engine.tax.domain.variable_pay import VariablePayRules


class KnowledgeRepository(Protocol):  # pragma: no cover
    """Read-only access to the versioned payroll rule bundle.

    The engine depends on this interface, not on any concrete loader.
    :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is the production implementation that reads
    from the package-bundled JSON files.
    """

    def load_ccnl(self, filename: str) -> CCNL:
        """Load and return the CCNL for *filename*."""
        ...

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Load and return the tax year rules for *year*, *sector*, *num_employees*."""
        ...

    def load_surtax_rules(self, year: int) -> SurtaxRules | None:
        """Load and return the surtax rules for *year*, or None when unavailable."""
        ...

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        """Load and return the capability catalog for *year*."""
        ...

    def load_variable_pay_rules(self, year: int) -> VariablePayRules:
        """Load and return the statutory variable-pay rules for *year*."""
        ...

    def load_family_deduction_rules(self, year: int) -> FamilyDeductionRules:
        """Load and return the Art. 12 TUIR family deduction rules for *year*."""
        ...
