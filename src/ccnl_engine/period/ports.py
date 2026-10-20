"""KnowledgeRepository port: the engine's interface to the data bundle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import InsuredAbsenceRates
    from ccnl_engine.agreement.facade import CCNL, TaxSector
    from ccnl_engine.capability.registry.models import CapabilityCatalog
    from ccnl_engine.catalog.loaders import ContractSummary
    from ccnl_engine.family.models import FamilyDeductionRules
    from ccnl_engine.limitation.models import ModelLimitation
    from ccnl_engine.sector.models import YearRules
    from ccnl_engine.sickness.indemnity.models import InpsSickPayRates
    from ccnl_engine.surtax.models import SurtaxRules
    from ccnl_engine.variable_pay.models import VariablePayRules


class KnowledgeRepository(Protocol):  # pragma: no cover
    """Read-only access to the versioned payroll rule bundle.

    The engine depends on this interface, not on any concrete loader.
    :class:`~ccnl_engine.period.repositories.BundledKnowledgeRepository` is the
    production implementation that reads
    from the package-bundled JSON files.

    A CCNL is named by its slug (e.g. ``"metalmeccanico-federmeccanica"``);
    the engine resolves a CNEL code to a slug through
    :meth:`load_contracts`.
    """

    @property
    def bundle_version(self) -> str:
        """Version of the rule bundle, stamped on every result."""
        ...

    def load_contracts(self) -> tuple[ContractSummary, ...]:
        """Load and return the summary of every CCNL, sorted by ``ccnl_id``."""
        ...

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Load and return the CCNL with slug *ccnl_id*."""
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

    def load_engine_limitations(self) -> tuple[ModelLimitation, ...]:
        """Load and return the limitations of the engine's shared code paths."""
        ...

    def load_variable_pay_rules(self, year: int) -> VariablePayRules:
        """Load and return the statutory variable-pay rules for *year*."""
        ...

    def load_family_deduction_rules(self, year: int) -> FamilyDeductionRules:
        """Load and return the Art. 12 TUIR family deduction rules for *year*."""
        ...

    def load_sick_pay_rates(self) -> InpsSickPayRates:
        """Load and return the INPS sickness indemnity rules."""
        ...

    def load_insured_absence_rates(self) -> InsuredAbsenceRates:
        """Load and return the maternity and work-injury indemnities."""
        ...
