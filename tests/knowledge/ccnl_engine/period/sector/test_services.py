"""A year and a termination of each contribution sector against hand oracles.

The oracles are in :mod:`tests.knowledge.ccnl_engine.period.sector.oracles`,
computed by hand from the cited sources.  The engine runs each scenario
through :meth:`~ccnl_engine.PayrollEngine.calculate_competence_year`; every
payment (gross, INPS of the worker, TFR accrued, employer cost) and the
year (taxable, IRPEF, credits, surtax withheld, net cash, TFR, employer
cost) are compared, and so is what the assurance says about each total:
the amounts the CCNL owes and the engine does not compute leave the
employer cost short, and the net pay too when they reach the worker.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from functools import cache
from pathlib import Path

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    ContributableHours,
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode
from tests.knowledge.ccnl_engine.period.sector.oracles import (
    CHIMICA_JUNE,
    CHIMICA_YEAR,
    EDILIZIA_JUNE,
    EDILIZIA_YEAR,
    INDUSTRIA_JUNE,
    INDUSTRIA_YEAR,
    OVERTIME_HOURS,
    STUDI_JUNE,
    STUDI_YEAR,
    TERZIARIO_JUNE,
    TERZIARIO_YEAR,
    TURISMO_JUNE,
    TURISMO_YEAR,
    SectorYear,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_ZERO = Decimal(0)
_JUNE_END = date(2026, 6, 30)
_FACTS = PeriodFacts(
    regione="IT-88",
    comune_belfiore="A192",
    family_composition=FamilyComposition(),
)


@dataclass(frozen=True)
class Scenario:
    """A plan of the engine, its oracle and what its assurance says."""

    ccnl: str
    level: str
    category: WorkerCategory
    headcount: int
    oracle: SectorYear
    owed: frozenset[str]
    net_pay_reliable: bool
    terminated: bool = False
    hours: Decimal | None = None
    overtime: bool = False
    provincial_pay_element: bool | None = None


_METAL = "metalmeccanico-federmeccanica"
_TERZ = "terziario-confesercenti"
_EDIL = "edilizia-ance"
_CHIMICA = "chimica-farmaceutica-federchimica"
_TURISMO = "turismo-federalberghi"
_STUDI = "studi-professionali-confprofessioni"
_METAL_OWED = frozenset({
    f"{_METAL}/health_and_bilateral_funds",
    f"{_METAL}/flexible_benefits",
})
_TERZ_OWED = frozenset({f"{_TERZ}/health_and_bilateral_funds"})
_STUDI_OWED = frozenset({f"{_STUDI}/bilateral_contribution_or_element"})
_TURISMO_OWED = frozenset({f"{_TURISMO}/health_and_bilateral_funds"})
_CHIMICA_OWED: frozenset[str] = frozenset()
_EDIL_OWED = frozenset({
    f"{_EDIL}/cassa_edile_contribution",
    f"{_EDIL}/territorial_sector_allowance",
})

SCENARIOS = {
    "industria-year": Scenario(
        _METAL,
        "C3",
        WorkerCategory.IMPIEGATO,
        50,
        INDUSTRIA_YEAR,
        _METAL_OWED,
        net_pay_reliable=True,
        overtime=True,
    ),
    "industria-june": Scenario(
        _METAL,
        "C3",
        WorkerCategory.IMPIEGATO,
        50,
        INDUSTRIA_JUNE,
        _METAL_OWED,
        net_pay_reliable=True,
        terminated=True,
    ),
    "terziario-year": Scenario(
        _TERZ,
        "IV",
        WorkerCategory.IMPIEGATO,
        50,
        TERZIARIO_YEAR,
        _TERZ_OWED,
        net_pay_reliable=False,
        provincial_pay_element=True,
    ),
    "terziario-june": Scenario(
        _TERZ,
        "IV",
        WorkerCategory.IMPIEGATO,
        50,
        TERZIARIO_JUNE,
        _TERZ_OWED,
        net_pay_reliable=False,
        terminated=True,
        provincial_pay_element=True,
    ),
    "edilizia-year": Scenario(
        _EDIL,
        "1",
        WorkerCategory.OPERAIO,
        30,
        EDILIZIA_YEAR,
        _EDIL_OWED,
        net_pay_reliable=False,
        hours=Decimal(173),
    ),
    "edilizia-june": Scenario(
        _EDIL,
        "1",
        WorkerCategory.OPERAIO,
        30,
        EDILIZIA_JUNE,
        _EDIL_OWED,
        net_pay_reliable=False,
        terminated=True,
        hours=Decimal(173),
    ),
    "studi-year": Scenario(
        _STUDI,
        "4",
        WorkerCategory.IMPIEGATO,
        10,
        STUDI_YEAR,
        _STUDI_OWED,
        net_pay_reliable=False,
    ),
    "studi-june": Scenario(
        _STUDI,
        "4",
        WorkerCategory.IMPIEGATO,
        10,
        STUDI_JUNE,
        _STUDI_OWED,
        net_pay_reliable=False,
        terminated=True,
    ),
    "turismo-year": Scenario(
        _TURISMO,
        "4",
        WorkerCategory.IMPIEGATO,
        10,
        TURISMO_YEAR,
        _TURISMO_OWED,
        net_pay_reliable=False,
    ),
    "turismo-june": Scenario(
        _TURISMO,
        "4",
        WorkerCategory.IMPIEGATO,
        10,
        TURISMO_JUNE,
        _TURISMO_OWED,
        net_pay_reliable=False,
        terminated=True,
    ),
    "chimica-year": Scenario(
        _CHIMICA,
        "D1",
        WorkerCategory.IMPIEGATO,
        50,
        CHIMICA_YEAR,
        _CHIMICA_OWED,
        net_pay_reliable=True,
    ),
    "chimica-june": Scenario(
        _CHIMICA,
        "D1",
        WorkerCategory.IMPIEGATO,
        50,
        CHIMICA_JUNE,
        _CHIMICA_OWED,
        net_pay_reliable=True,
        terminated=True,
    ),
}


@cache
def _year(name: str) -> CompetenceYearResult:
    s = SCENARIOS[name]
    facts = replace(
        _FACTS,
        ordinary_hours_worked=None if s.hours is None else ContributableHours(s.hours),
    )
    periods = {}
    if s.overtime:
        #: Two weekday hours at the hourly minimo the bundle also states:
        #: the request has no overtime event without a rate.
        rate = (Decimal("2158.26") / 173).quantize(Decimal("0.00001"))
        event = OvertimeEvent(
            event_date=date(2026, 3, 10), hours=OVERTIME_HOURS, hourly_rate=rate
        )
        periods = {3: replace(facts, events=(event,))}
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=f"{s.ccnl}.json",
                level_code=s.level,
                category=s.category,
                seniority=new_hire(),
                employment_period=EmploymentPeriod(
                    date(2026, 1, 1), _JUNE_END if s.terminated else None
                ),
                tfr_treasury_fund=False,
                pension_fund=NoPensionFund(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(s.headcount),
                provincial_pay_element=s.provincial_pay_element,
            ),
            default_facts=facts,
            periods=periods,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40_000)),
            current_year=CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1)),
        )
    )


def _posted(result: PeriodResult, account: str) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


def _total(name: str, account: str) -> Decimal:
    return sum((_posted(r, account) for r in _year(name).period_results), _ZERO)


_NAMES = sorted(SCENARIOS)


@pytest.mark.parametrize("name", _NAMES)
def test_every_payment_matches_the_oracle(name: str) -> None:
    """Gross, worker and employer INPS, TFR accrued and employer cost."""
    runs = _year(name).period_results
    oracle = SCENARIOS[name].oracle.payments

    assert [r.run.run_id for r in runs if r.run] == [p.run_id for p in oracle]
    for result, payment in zip(runs, oracle, strict=True):
        assert result.period_gross == payment.gross, payment.run_id
        assert _posted(result, "employee_contributions") == payment.employee_inps
        employer = _posted(result, "employer_contributions")
        assert employer == payment.employer_contributions, payment.run_id
        assert _posted(result, "tfr_accrual") == payment.tfr_accrual, payment.run_id
        assert result.period_employer_cost == payment.employer_cost, payment.run_id


@pytest.mark.parametrize("name", _NAMES)
def test_the_year_matches_the_oracle(name: str) -> None:
    """Taxable, IRPEF, credits, surtax, net cash, TFR and employer cost."""
    oracle = SCENARIOS[name].oracle
    runs = _year(name).period_results
    cash = runs[-1].closing_state.cash

    assert cash.earnings.taxable == oracle.taxable
    assert _total(name, "ordinary_tax") == oracle.irpef
    assert _total(name, "credits") == oracle.credits
    assert _total(name, "surtax") == oracle.surtax
    assert sum((r.period_net for r in runs), _ZERO) == oracle.net
    assert _total(name, "tfr_accrual") == oracle.tfr
    assert sum((r.period_employer_cost for r in runs), _ZERO) == oracle.employer_cost


@pytest.mark.parametrize("name", _NAMES)
def test_owed_amounts_leave_the_totals_they_touch_short(name: str) -> None:
    """Every run carries the owed limitations; their totals decide the axes.

    A CCNL that owes nothing the engine leaves out completes the employer
    cost of every run but the one whose residual leave is not computed.
    """
    s = SCENARIOS[name]
    for result in _year(name).period_results:
        owed = {
            b.detail
            for b in result.blockers
            if b.code is BlockerCode.OPEN_LIMITATION and b.detail in s.owed
        }
        assert owed == s.owed
        if s.owed:
            assert not result.is_employer_cost_complete
            assert not result.is_payable
        else:
            features = {b.feature for b in result.blockers}
            assert result.is_employer_cost_complete is (
                "termination_residual_leave" not in features
            )


@pytest.mark.parametrize("name", _NAMES)
def test_only_the_stated_gaps_block_the_net_pay(name: str) -> None:
    """Besides the owed amounts, only the known gaps of the scenario block."""
    s = SCENARIOS[name]
    year = _year(name)
    others = {
        (b.code, b.feature, b.detail)
        for r in year.period_results
        for b in r.blockers
        if b.detail not in s.owed
    }
    expected = set()
    if s.overtime:
        expected |= {
            (BlockerCode.CALCULATION_ISSUE, "overtime", "ccnl_overtime_band_applied"),
            (BlockerCode.CALCULATION_ISSUE, None, "overtime_tier_not_applied"),
            (BlockerCode.CALLER_SUPPLIED_RULE, "overtime", "hourly_rate"),
            (BlockerCode.CAPABILITY_NOT_COMPUTED, "overtime", "partial_result"),
            (
                BlockerCode.OPEN_LIMITATION,
                "overtime",
                f"{_METAL}/overtime_exempt_quota_supplement",
            ),
        }
    if s.terminated:
        expected.add((
            BlockerCode.CAPABILITY_NOT_COMPUTED,
            "termination_residual_leave",
            "unsupported",
        ))
    if s.ccnl == _EDIL:
        expected.add((
            BlockerCode.CAPABILITY_NOT_COMPUTED,
            "pension_fund_contribution",
            "partial_implementation",
        ))
    assert others == expected
    owed_only = [
        r for r in year.period_results if {b.detail for b in r.blockers} <= s.owed
    ]
    if not owed_only:
        # Every edilizia run also carries the partial Prevedi contribution.
        assert not any(r.is_net_pay_payable for r in year.period_results)
        return
    assert {r.is_net_pay_payable for r in owed_only} == {s.net_pay_reliable}


def test_the_scenarios_are_described_for_the_validation_matrix() -> None:
    """``scenarios.json`` describes exactly the scenarios run here."""
    path = Path(__file__).with_name("scenarios.json")
    described = json.loads(path.read_text(encoding="utf-8"))

    assert {name: d["ccnl"] for name, d in described.items()} == {
        name: s.ccnl for name, s in SCENARIOS.items()
    }
    for name, d in described.items():
        assert ("termination" in d["cycles"]) == SCENARIOS[name].terminated
        assert ("overtime" in d["variables"]) == SCENARIOS[name].overtime
