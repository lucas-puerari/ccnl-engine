"""Each kind of weak record of the bundle blocks the runs that read it.

A value the bundle holds as ``assumed`` (adopted without a located
citation) or ``missing`` must never reach a payable result.  The bundle
holds them in four shapes, and each reaches the result its own way:

- a CCNL rule recorded ``assumed``: a ``rule_source_weak`` blocker of the
  capability that read it;
- a CCNL series with a ``missing`` gap: the run on a date inside the gap is
  refused (:class:`~ccnl_engine.errors.MissingRuleError`), no amount comes
  out;
- an ``assumed`` block of a 2026 INPS file (the agricultural apprentice
  rates, the minimum base of the public administrations): a
  ``rule_source_weak`` blocker of the INPS capabilities, only on the runs
  that read the block;
- a municipal surtax row carried from the year before, ``assumed`` until
  the municipality publishes its delibera: the ``municipal_surtax_prior_
  year_rates`` issue of the conguaglio.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.inputs import (
    Apprentice,
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_INPS = {"inps_employee", "inps_employer"}
_CARRIED = "municipal_surtax_prior_year_rates"


def _weak(result: PeriodResult) -> set[tuple[str | None, str]]:
    return {
        (b.feature, b.detail)
        for b in result.blockers
        if b.code is BlockerCode.RULE_SOURCE_WEAK
    }


def test_an_assumed_ccnl_rule_blocks_the_capability_that_reads_it() -> None:
    """Agenti immobiliari, level Q: its minimum is recorded assumed."""
    result = regular_period(ccnl_id="agenti-immobiliari-fiaip", level_code="Q")

    assert ("base_salary", "assumed") in _weak(result)
    assert not result.is_payable


def test_a_missing_gap_refuses_the_run() -> None:
    """Grafica editoria declares no seniority amount of Q before July 2026."""
    employment = Employment(
        ccnl_id="grafica-editoria-aieg",
        level_code="Q",
        seniority=SeniorityFact.since(
            date(2018, 1, 1), SenioritySource.EMPLOYER_RECORDS
        ),
        contract_type=Permanent(),
    )

    with pytest.raises(MissingRuleError):
        regular_period(employment=employment)


def _agricultural(contract_type: Permanent | Apprentice) -> PeriodResult:
    return regular_period(
        employment=Employment(
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area1",
            seniority=new_hire(2026),
            contract_type=contract_type,
        )
    )


def test_agricultural_runs_read_no_weak_inps_rule() -> None:
    """The OTI rates and the apprentice rates with the CISOA are sourced."""
    apprentice = _weak(_agricultural(Apprentice(months_elapsed=6)))
    permanent = _weak(_agricultural(Permanent()))

    assert not {feature for feature, _ in apprentice} & _INPS
    assert not {feature for feature, _ in permanent} & _INPS


def test_a_public_run_reads_no_weak_inps_rule() -> None:
    """The minimum base and the CTPS rates of the State are verified."""
    result = regular_period(ccnl_id="funzioni-centrali-aran", level_code="FUNZIONARI")

    assert not {feature for feature, _ in _weak(result)} & _INPS


def _concia_year(comune: str, regione: str) -> tuple[PeriodResult, ...]:
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_id="concia-unic",
                level_code="D2",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                tfr_treasury_fund=False,
                pension_fund=NoPensionFund(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            default_facts=PeriodFacts(
                regione=regione,
                comune_belfiore=comune,
                family_composition=FamilyComposition(),
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40_000)),
            current_year=CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1)),
        )
    )
    return year.period_results


def _carried(results: tuple[PeriodResult, ...]) -> bool:
    return any(
        b.code is BlockerCode.CALCULATION_ISSUE and b.detail == _CARRIED
        for r in results
        for b in r.blockers
    )


def test_a_carried_municipal_row_blocks_the_conguaglio() -> None:
    """Roma has no 2026 delibera yet: its 2025 rates are provisional."""
    roma = _concia_year("H501", "IT-62")

    assert _carried(roma)
    assert not any(r.is_payable for r in roma)


def test_a_published_municipal_row_does_not() -> None:
    """Alghero published its 2026 delibera: the conguaglio is final."""
    assert not _carried(_concia_year("A192", "IT-88"))
