"""KnowledgeRepository port: the engine's interface to the data bundle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules


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

    def load_surtax_rules(self, year: int) -> SurtaxRules:
        """Load and return the surtax rules for *year*."""
        ...
