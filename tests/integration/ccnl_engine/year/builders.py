"""Knowledge repository that serves the bundled 2026 rules as 2027 rules.

The bundled 2027 tables are provisional copies of 2026, so a run of tax
year 2027 is not payable.  Tests of the year change need a 2027 run on
rules that are not provisional: this repository answers a 2027 request
with the bundled 2026 rules relabelled as 2027.  The amounts are 2026
law; only differential assertions (with and without a carried obligation)
are meaningful on its results.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import InsuredAbsenceRates
    from ccnl_engine.agreement.facade import CCNL, TaxSector
    from ccnl_engine.calendar.holiday.models import NationalHolidays
    from ccnl_engine.capability.registry.models import CapabilityCatalog
    from ccnl_engine.catalog.loaders import ContractSummary
    from ccnl_engine.family.models import FamilyDeductionRules
    from ccnl_engine.limitation.models import ModelLimitation
    from ccnl_engine.sector.models import YearRules
    from ccnl_engine.sickness.indemnity.models import InpsSickPayRates
    from ccnl_engine.surtax.models import SurtaxRules
    from ccnl_engine.variable_pay.models import VariablePayRules

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

    @property
    def bundle_version(self) -> str:
        """Version of the bundled datasets."""
        return self._bundled.bundle_version

    def load_contracts(self) -> tuple[ContractSummary, ...]:
        """Return the bundled contracts.

        Returns:
            The summary of every bundled CCNL.
        """
        return self._bundled.load_contracts()

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the bundled CCNL.

        Returns:
            The bundled CCNL with slug ``ccnl_id``.
        """
        return self._bundled.load_ccnl(ccnl_id)

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

    def load_sick_pay_rates(self) -> InpsSickPayRates:
        """Return the bundled INPS sickness indemnity rules.

        Returns:
            The rules, not tied to a year.
        """
        return self._bundled.load_sick_pay_rates()

    def load_insured_absence_rates(self) -> InsuredAbsenceRates:
        """Return the bundled maternity and work-injury indemnities.

        Returns:
            The indemnities, not tied to a year.
        """
        return self._bundled.load_insured_absence_rates()

    def load_national_holidays(self) -> NationalHolidays:
        """Return the bundled national holidays.

        Returns:
            The holidays of the bundle.
        """
        return self._bundled.load_national_holidays()

    def load_engine_limitations(self) -> tuple[ModelLimitation, ...]:
        """Return the bundled engine limitations.

        Returns:
            The engine limitations of the bundle.
        """
        return self._bundled.load_engine_limitations()
