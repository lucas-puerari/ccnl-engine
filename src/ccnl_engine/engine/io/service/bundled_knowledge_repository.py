"""BundledKnowledgeRepository: reads rules from the package-bundled JSON files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.io.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import load_year_rules

if TYPE_CHECKING:
    from ccnl_engine.engine.capability_catalog import CapabilityCatalog
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules


class BundledKnowledgeRepository:
    """Concrete :class:`~ccnl_engine.engine.knowledge_repository.KnowledgeRepository`.

    Reads from the versioned JSON files bundled inside the ``ccnl_engine``
    package.  All loader functions are cached, so repeated calls for the same
    arguments return the same (immutable) object without re-parsing.
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
            A :class:`~ccnl_engine.engine.tax.domain.rules.YearRules` with
            INPS rates resolved for the given headcount.
        """
        return load_year_rules(year, sector, num_employees)

    def load_surtax_rules(self, year: int) -> SurtaxRules:  # noqa: PLR6301
        """Return surtax rules for *year*.

        Returns:
            A :class:`~ccnl_engine.engine.surtax.domain.rules.SurtaxRules`
            with regionale and comunale rate tables.
        """
        return load_surtax_rules(year)

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:  # noqa: PLR6301
        """Return the capability catalog for *year*.

        Returns:
            A :class:`~ccnl_engine.engine.capability_catalog.CapabilityCatalog`
            with all declared capabilities for the requested year.
        """
        return load_capability_catalog(year)
