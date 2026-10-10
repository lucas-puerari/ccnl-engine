"""BundledKnowledgeRepository: reads rules from the package-bundled JSON files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.knowledge.limitation.loaders import load_engine_limitations
from ccnl_engine.tax.annual.loaders import load_year_rules
from ccnl_engine.tax.annual.loaders_optional import (
    load_family_deduction_rules,
    load_sick_pay_rates,
    load_variable_pay_rules,
)
from ccnl_engine.tax.surtax.loaders import load_surtax_rules

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL, TaxSector
    from ccnl_engine.knowledge.limitation.models import ModelLimitation
    from ccnl_engine.payroll.capability.models_catalog import CapabilityCatalog
    from ccnl_engine.tax.annual.models import YearRules
    from ccnl_engine.tax.family.models import FamilyDeductionRules
    from ccnl_engine.tax.regime.models_variable_pay import VariablePayRules
    from ccnl_engine.tax.sickness.models import InpsSickPayRates
    from ccnl_engine.tax.surtax.models import SurtaxRules


class BundledKnowledgeRepository:
    """Production implementation of the knowledge repository port.

    Satisfies :class:`~ccnl_engine.payroll.period.ports\
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
            A :class:`~ccnl_engine.tax.annual.models.YearRules` with
            INPS rates resolved for the given headcount.
        """
        return load_year_rules(year, sector, num_employees)

    def load_surtax_rules(self, year: int) -> SurtaxRules:  # noqa: PLR6301
        """Return surtax rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.surtax.models.SurtaxRules`
            with regionale and comunale rate tables.
        """
        return load_surtax_rules(year)

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:  # noqa: PLR6301
        """Return the capability catalog for *year*.

        Returns:
            A :class:`~ccnl_engine.payroll.capability.models_catalog.CapabilityCatalog`
            with all declared capabilities for the requested year.
        """
        return load_capability_catalog(year)

    def load_engine_limitations(self) -> tuple[ModelLimitation, ...]:  # noqa: PLR6301
        """Return the limitations of the engine's shared code paths.

        Returns:
            The engine limitations of the bundle, in file order.
        """
        return load_engine_limitations()

    def load_variable_pay_rules(self, year: int) -> VariablePayRules:  # noqa: PLR6301
        """Return the statutory variable-pay rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.regime.models_variable_pay.VariablePayRules`
            with fringe thresholds, PdR and L. 199/2025 regimes.
        """
        return load_variable_pay_rules(year)

    def load_family_deduction_rules(self, year: int) -> FamilyDeductionRules:  # noqa: PLR6301
        """Return the Art. 12 TUIR family deduction rules for *year*.

        Returns:
            A :class:`~ccnl_engine.tax.family.models.FamilyDeductionRules`.
        """
        return load_family_deduction_rules(year)

    def load_sick_pay_rates(self) -> InpsSickPayRates:  # noqa: PLR6301
        """Return the INPS sickness indemnity rules.

        Returns:
            The waiting period, bands, annual maximum and coverage rules.
        """
        return load_sick_pay_rates()
