"""Hand oracle: the renewal increment of the turismo minimo taxed at 5%.

CCNL Turismo Federalberghi, level 4, renewal signed on 5 July 2024 (ipotesi
di accordo), first tranche from 1 July 2024.  The minimo in force before it,
1,550.69 EUR from 1 April 2016, is the base of the increment (Agenzia delle
Entrate circ. 2/E of 24 February 2026, par. 1): every tranche of the renewal
paid in 2026 is taxed at 5%, the ones started in 2024 and 2025 too.

Tables of level 4 (signed renewal, p. 42): 1,660.69 EUR from 1 June 2025 and
1,695.69 EUR from 1 May 2026.  A worker hired on 1 January 2026 with a 2025
income of 25,000 EUR is in the regime: the increment is 110 EUR a month from
January to April and 145 EUR from May; the tredicesima pays a full December
minimo, the quattordicesima of June 6/12 of the June minimo (accrual from
July to June).
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

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
    SubstituteTaxRegime,
    WorkerCategory,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2026, 1, 1)
_PRE_RENEWAL = Decimal("1550.69")
_JUNE_2025 = Decimal("1660.69")
_MAY_2026 = Decimal("1695.69")
_RATE = Decimal("0.05")
_CENT = Decimal("0.01")


def _tax(increment: Decimal) -> Decimal:
    return (increment * _RATE).quantize(_CENT, rounding=ROUND_HALF_UP)


#: Increment of each run, in payment order: January-May, the June regular
#: run and its quattordicesima, July-December and the tredicesima.
_INCREMENTS = (
    *[_JUNE_2025 - _PRE_RENEWAL] * 4,
    *[_MAY_2026 - _PRE_RENEWAL] * 2,
    (_MAY_2026 - _PRE_RENEWAL) * 6 / 12,
    *[_MAY_2026 - _PRE_RENEWAL] * 6,
    _MAY_2026 - _PRE_RENEWAL,
)


def _year(*, waived: bool) -> CompetenceYearResult:
    waivers = frozenset({SubstituteTaxRegime.RINNOVO}) if waived else frozenset()
    return PayrollEngine.bundled().calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="turismo-federalberghi",
                level_code="4",
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
            prior_year=PriorYearTaxFacts(
                employment_income=Decimal(25000), waived_regimes=waivers
            ),
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
                comune_belfiore="A005",
                family_composition=FamilyComposition(),
            ),
        )
    )


@pytest.fixture(scope="module")
def year() -> CompetenceYearResult:
    """Return the year of the worker in the regime.

    Returns:
        The competence year.
    """
    return _year(waived=False)


def test_each_run_taxes_its_increment(year: CompetenceYearResult) -> None:
    """Every run posts 5% of the increment its minimo carries."""
    posted = [
        sum(
            (
                e.amount
                for e in r.ledger_entries
                if e.account is AccountKind.SUBSTITUTE_TAX
            ),
            Decimal(0),
        )
        for r in year.period_results
    ]
    assert posted == [_tax(i) for i in _INCREMENTS]
    assert sum(posted) == Decimal("90.88")


def test_the_decision_cites_the_circular(year: CompetenceYearResult) -> None:
    """The taxed decision names the increment, the table before and circ. 2/E."""
    (decision,) = [
        d
        for d in year.period_results[0].decisions
        if d.capability == "rinnovo_substitute_tax"
    ]
    assert decision.reason_code == "renewal_increment_in_minimum_taxed"
    assert decision.inputs["increment"] == Decimal("110.00")
    assert decision.inputs["pre_renewal_minimum"] == _PRE_RENEWAL
    assert decision.source is not None
    assert decision.source.source_document.document_id == "ade-circ-2e-2026"


def test_a_written_waiver_keeps_the_ordinary_taxation(
    year: CompetenceYearResult,
) -> None:
    """Waived, nothing is taxed at 5% and the net is lower."""
    waived = _year(waived=True)
    assert not any(
        e.account is AccountKind.SUBSTITUTE_TAX
        for r in waived.period_results
        for e in r.ledger_entries
    )
    assert waived.annual_net < year.annual_net
