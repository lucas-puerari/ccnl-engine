"""Gate A of the pilot CCNLs: what keeps the base case from being payable.

The base case is a full-time permanent impiegato hired on 1 January 2026,
middle level of the CCNL, every fact the engine asks for stated, computed as
a competence year in operational mode.  Four worker profiles cross the two
facts that decide the cross-cutting blockers:

- the 2025 employment income, 25,000 EUR (eligible to the renewal regime of
  L. 199/2025 art. 1 c. 7) or 40,000 EUR (excluded);
- the comune of residence, A005 (a 2026 delibera in force) or F205 (Milan,
  no 2026 delibera: the 2025 rates stay in force).

Each pilot passes Gate A when every profile is payable.  The expected
blockers are today's: a change that closes one updates this table, so the
progress of the plan shows in the diff.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Final

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
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

type Blocker = tuple[str, str, str]

_HIRED: Final = date(2026, 1, 1)
_ELIGIBLE: Final = Decimal(25000)
_EXCLUDED: Final = Decimal(40000)
_WITH_DELIBERA: Final = "A005"
_MILAN: Final = "F205"
#: The employer pays every contractual fund of the pilots (codes of other
#: CCNLs are ignored).
_FUNDS_PAID: Final = frozenset({
    "ebnt",
    "fast",
    "quas",
    "ebt",
    "fondo_est",
    "aster",
    "quadrifor",
    "ebm",
    "ebm_salute",
})

#: Blockers of a worker eligible to the renewal regime: the increment paid
#: inside the minimo is not quantified (REVIEW A1).
_RENEWAL: Final[frozenset[Blocker]] = frozenset({
    (
        "calculation_issue",
        "rinnovo_substitute_tax",
        "renewal_increment_in_minimum_unquantified",
    ),
    (
        "calculation_issue",
        "rinnovo_substitute_tax",
        "rinnovo_minimum_increment_unquantified",
    ),
})
#: Blocker of a resident of a comune whose 2026 row carries earlier rates
#: (REVIEW A2).
_SURTAX_SOURCE: Final[frozenset[Blocker]] = frozenset({
    ("rule_source_weak", "addizionale_comunale", "assumed")
})
#: Blockers of the same resident above the comune's exemption threshold.
_SURTAX_PRIOR_RATES: Final[frozenset[Blocker]] = frozenset({
    ("calculation_issue", "addizionale_comunale", "deferred_to_installments"),
    (
        "calculation_issue",
        "addizionale_comunale",
        "municipal_surtax_prior_year_rates",
    ),
    ("calculation_issue", "addizionale_comunale", "prior_year_rates_applied"),
})


def _owed(ccnl_id: str, feature: str, limitation: str) -> Blocker:
    return ("open_limitation", feature, f"{ccnl_id}/{limitation}")


#: Blockers of each pilot that no fact of the base case clears.
_SPECIFIC: Final[dict[str, frozenset[Blocker]]] = {
    "chimica-farmaceutica-federchimica": frozenset(),
    "turismo-federalberghi": frozenset(),
    "pubblici-esercizi-fipe-angem": frozenset(),
    "terziario-confesercenti": frozenset(),
    "metalmeccanico-confapi": frozenset(),
    "metalmeccanico-federmeccanica": frozenset({
        _owed(
            "metalmeccanico-federmeccanica",
            "bilateral_funds",
            "health_and_bilateral_funds",
        ),
        _owed("metalmeccanico-federmeccanica", "welfare", "flexible_benefits"),
    }),
    "studi-professionali-confprofessioni": frozenset({
        _owed(
            "studi-professionali-confprofessioni",
            "bilateral_funds",
            "bilateral_contribution_or_element",
        ),
        _owed(
            "studi-professionali-confprofessioni",
            "inps_employer",
            "fsbap_rates_above_15",
        ),
    }),
    "commercio-confcommercio": frozenset({
        _owed(
            "commercio-confcommercio",
            "bilateral_funds",
            "health_and_bilateral_funds",
        ),
        ("ruleset_not_production", "", "ccnl/commercio-confcommercio"),
    }),
}
#: Pilots whose renewal increment cannot be measured yet: the CCNL does not
#: list its renewal (``parameters.renewals``) or lacks the table before it.
_RENEWAL_UNMEASURED: Final = frozenset({
    "chimica-farmaceutica-federchimica",
    "pubblici-esercizi-fipe-angem",
    "studi-professionali-confprofessioni",
    "commercio-confcommercio",
})
#: Pilots whose middle level stays under Milan's exemption threshold: the
#: comunale is a final zero and only its source is weak.
_UNDER_MILAN_THRESHOLD: Final = frozenset({
    "turismo-federalberghi",
    "pubblici-esercizi-fipe-angem",
    "studi-professionali-confprofessioni",
})
#: Pilots whose middle level drops under Milan's threshold once the renewal
#: increment is taxed at 5% and leaves the IRPEF base.
_UNDER_MILAN_THRESHOLD_TAXED: Final = frozenset({"terziario-confesercenti"})
_PROFILES: Final = [
    (income, comune)
    for income in (_ELIGIBLE, _EXCLUDED)
    for comune in (_WITH_DELIBERA, _MILAN)
]


def _expected(ccnl_id: str, income: Decimal, comune: str) -> frozenset[Blocker]:
    expected = set(_SPECIFIC[ccnl_id])
    if income == _ELIGIBLE and ccnl_id in _RENEWAL_UNMEASURED:
        expected |= _RENEWAL
    if comune == _MILAN:
        expected |= _SURTAX_SOURCE
        under = ccnl_id in _UNDER_MILAN_THRESHOLD or (
            income == _ELIGIBLE and ccnl_id in _UNDER_MILAN_THRESHOLD_TAXED
        )
        if not under:
            expected |= _SURTAX_PRIOR_RATES
    return frozenset(expected)


@pytest.fixture(scope="module")
def engine() -> PayrollEngine:
    """Return the bundled engine in operational mode.

    Returns:
        The engine.
    """
    return PayrollEngine.bundled(mode="operational")


def _base_case(
    engine: PayrollEngine, ccnl_id: str, income: Decimal, comune: str
) -> CompetenceYearResult:
    levels = engine.list_levels(ccnl_id)
    return engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=levels[len(levels) // 2].code,
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
                headcount=Headcount(60),
                provincial_pay_element=False,
                contractual_funds=_FUNDS_PAID,
            ),
            prior_year=PriorYearTaxFacts(employment_income=income),
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
                regione="IT-25",
                comune_belfiore=comune,
                family_composition=FamilyComposition(),
            ),
        )
    )


@pytest.mark.parametrize("ccnl_id", sorted(_SPECIFIC))
@pytest.mark.parametrize(("income", "comune"), _PROFILES)
def test_base_case_blockers(
    engine: PayrollEngine, ccnl_id: str, income: Decimal, comune: str
) -> None:
    """The base case keeps exactly the blockers the plan still has to close."""
    year = _base_case(engine, ccnl_id, income, comune)
    blockers = {(b.code.value, b.feature or "", str(b.detail)) for b in year.blockers}
    expected = _expected(ccnl_id, income, comune)
    assert blockers == expected
    assert year.is_payable is (not expected)
