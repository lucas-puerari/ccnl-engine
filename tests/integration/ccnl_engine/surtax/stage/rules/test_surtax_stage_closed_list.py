"""A closed municipal list makes the carried rates of the capoluoghi final.

The bundled 2026 list was retrieved before 20 December 2026, so a comune
without a 2026 delibera carries its 2025 rates as ``assumed`` and blocks the
conguaglio.  Once a list retrieved after 20 December is bundled, the build
marks those rows ``derived`` (D.Lgs. 23/2011 art. 14 c. 8): this test
injects that table and runs the base case of a payable pilot for a resident
of each capoluogo di regione.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    IncomeEstimateQuality,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.provenance.ruleset.models import RulesetReadiness
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.rule.models import (
    ProvenanceStatus,
    RuleProvenance,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.models import CCNL
    from ccnl_engine.surtax.models import SurtaxRules

_HIRED = date(2026, 1, 1)
#: Capoluoghi di regione and their region: (Belfiore code, region code).
_CAPOLUOGHI = (
    ("L219", "IT-21"),
    ("A326", "IT-23"),
    ("F205", "IT-25"),
    ("L378", "IT-TN"),
    ("L736", "IT-34"),
    ("L424", "IT-36"),
    ("D969", "IT-42"),
    ("A944", "IT-45"),
    ("D612", "IT-52"),
    ("G478", "IT-55"),
    ("A271", "IT-57"),
    ("H501", "IT-62"),
    ("A345", "IT-65"),
    ("B519", "IT-67"),
    ("F839", "IT-72"),
    ("A662", "IT-75"),
    ("G942", "IT-77"),
    ("C352", "IT-78"),
    ("G273", "IT-82"),
    ("B354", "IT-88"),
)
#: Perugia exempts a category of income, which the engine does not apply.
_SPECIFIC_EXEMPTIONS = frozenset({"G478"})
_CLOSED = RuleProvenance(
    status=ProvenanceStatus.DERIVED,
    location=SourceLocation(
        source_document=SourceDocument(
            document_id="mef-addizionale-comunale-elenco-2026",
            title="MEF elenco generale 2026, retrieved after 20 December 2026",
            kind=SourceKind.AMMINISTRAZIONE,
        ),
        section="elenco generale 2026, closed on 20 December",
    ),
)


class _ClosedListRepository(BundledKnowledgeRepository):
    """The bundle, with the 2026 municipal list as if closed.

    Chimica is ``reviewed``; the stub reads it as ``production`` so that
    only the surtax decides whether the operational run pays.
    """

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        verification = ccnl.verification.model_copy(
            update={"readiness": RulesetReadiness.PRODUCTION}
        )
        return ccnl.model_copy(update={"verification": verification})

    def load_surtax_rules(self, year: int) -> SurtaxRules:
        rules = super().load_surtax_rules(year)
        comunale = {
            code: entry.model_copy(update={"provenance": _CLOSED})
            if entry.rates_year is not None and entry.rates_year < year
            else entry
            for code, entry in rules.comunale.items()
        }
        return rules.model_copy(update={"comunale": comunale})


@pytest.fixture(scope="module")
def engine() -> PayrollEngine:
    """Return an operational engine reading the closed list.

    Returns:
        The engine.
    """
    return PayrollEngine(repository=_ClosedListRepository(), mode="operational")


@pytest.mark.parametrize(("comune", "regione"), _CAPOLUOGHI)
def test_a_closed_list_leaves_no_surtax_blocker(
    engine: PayrollEngine, comune: str, regione: str
) -> None:
    """A resident of a capoluogo is payable on chimica, the carried rates final."""
    year = engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_id="chimica-farmaceutica-federchimica",
                level_code="D1",
                contract_type=Permanent(),
                category=WorkerCategory.IMPIEGATO,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                roles=frozenset(),
                sector=EmploymentSector.PRIVATE,
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=True,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), provincial_pay_element=False
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40000)),
            current_year=CurrentYearTaxFacts(
                tax_year=2026,
                other_employment_income=Decimal(0),
                other_employment_inps_base=Decimal(0),
                other_income=Decimal(0),
                main_dwelling_income=Decimal(0),
                exempt_regime_income=Decimal(0),
                estimated_on=_HIRED,
                quality=IncomeEstimateQuality.DECLARED,
            ),
            default_facts=PeriodFacts(
                regione=regione,
                comune_belfiore=comune,
                family_composition=FamilyComposition(),
            ),
        )
    )
    details = {b.detail for b in year.blockers}
    if comune in _SPECIFIC_EXEMPTIONS:
        assert details
        assert not any("prior_year" in detail for detail in details)
        assert all(
            b.feature == "addizionale_comunale" or "specific" in b.detail
            for b in year.blockers
        )
    else:
        assert details == set()
        assert year.is_payable
