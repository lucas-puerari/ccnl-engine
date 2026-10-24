"""Contribution and capacity thresholds, and events that share a base.

Generated from the values the bundle declares:

- the headcount tiers of each sector and year: the rates of the last
  employee of a tier and of the first of the next;
- the IVS massimale (L. 335/1995 art. 2 c. 18) of a worker first insured
  after 1995: the yearly base stops at the ceiling to the euro;
- the capacity of the trattamento integrativo up to 15,000 EUR: due once
  the gross tax exceeds the work deduction less 75 EUR, by one cent;
- the INPS rates of a run, those of the sector of its CCNL;
- events of one run that share the INPS and IRPEF bases add up in them.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from functools import cache
from itertools import pairwise
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.events import BonusEvent, OvertimeEvent
from ccnl_engine.inputs import (
    ContributionHistory,
    EmploymentPeriod,
    Permanent,
    PriorYearTaxFacts,
)
from ccnl_engine.irpef.deduction.rules import work_income_deduction
from ccnl_engine.irpef.rules import irpef_gross
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.tax_credit.rules import trattamento_integrativo_outcome
from scripts.provenance.rules import KNOWLEDGE_DIR
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.sector.models import YearRules

_D = Decimal
_REPO = BundledKnowledgeRepository()
_ENGINE = PayrollEngine.bundled()
_YEARS = (2026, 2027)


@cache
def _rules(year: int, sector: TaxSector, headcount: int) -> YearRules:
    return _REPO.load_year_rules(year, sector, headcount)


def _tiers() -> list[tuple[int, TaxSector, str, int]]:
    found = []
    for year in _YEARS:
        for path in sorted((KNOWLEDGE_DIR / "contribution" / str(year)).glob("*.json")):
            inps = json.loads(path.read_text(encoding="utf-8")).get("inps") or {}
            for side in ("employee", "employer"):
                tiers = inps.get(f"{side}_tiers") or []
                found += [
                    (year, TaxSector(path.stem), side, tier["max_employees"])
                    for tier, nxt in pairwise(tiers)
                    if tier["max_employees"] is not None and tier["rate"] != nxt["rate"]
                ]
    return found


@pytest.mark.parametrize(("year", "sector", "side", "last"), _tiers())
def test_a_headcount_tier_ends_with_its_last_employee(
    year: int, sector: TaxSector, side: str, last: int
) -> None:
    """N employees pay the rate of the tier up to N; N + 1 the next one."""

    def rate(headcount: int) -> Decimal:
        inps = _rules(year, sector, headcount).inps
        assert inps is not None
        return inps.employee_rate if side == "employee" else inps.employer_rate

    assert rate(last) == rate(max(1, last - 1))
    assert rate(last + 1) != rate(last)


def _metal(bonus: Decimal) -> list[PeriodResult]:
    employment = Employment(
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2026, 1, 1)),
        contract_type=Permanent(),
        contribution_history=ContributionHistory(date(2005, 3, 1)),
    )
    december = PeriodFacts(
        regione="IT-25",
        comune_belfiore="A005",
        events=(BonusEvent(event_date=date(2026, 12, 10), amount=bonus),),
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EmployerProfile(headcount=Headcount(20)),
            default_facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
            periods={12: december},
        )
    )
    return list(year.period_results)


def _ivs_base(results: list[PeriodResult]) -> Decimal:
    return sum(
        (
            c.base
            for r in results
            for c in r.contribution_breakdown.components
            if c.name == "ivs_employee"
        ),
        _D(0),
    )


@pytest.mark.parametrize("offset", [-1, 0, 1, 500])
def test_the_ivs_base_stops_at_the_massimale(offset: int) -> None:
    """A December bonus brings the year to the ceiling less 1, at it, above it."""
    inps = _rules(2026, TaxSector.INDUSTRIA, 20).inps
    assert inps is not None
    ceiling = inps.ceiling
    assert ceiling is not None
    without = _ivs_base(_metal(_D(0)))
    bonus = ceiling - without + offset

    assert _ivs_base(_metal(bonus)) == min(without + bonus, ceiling)


def _capacity(year: int) -> Decimal:
    """Return the lowest income, to the cent, whose gross tax exceeds the floor.

    Returns:
        The first income with the full trattamento integrativo.
    """
    rules = _rules(year, TaxSector.TERZIARIO, 20)
    w = rules.work_deduction

    def exceeds(income: Decimal) -> bool:
        floor = money(max(_D(0), work_income_deduction(income, constants=w) - 75))
        return irpef_gross(income, rules) > floor

    low, high = _D(0), _D(15000)
    while high - low > _D("0.01"):
        mid = money((low + high) / 2)
        low, high = (low, mid) if exceeds(mid) else (mid, high)
    return high


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize(
    ("offset", "reason"),
    [("-0.01", "irpef_not_above_work_deduction"), ("0", "full_amount")],
)
def test_the_trattamento_needs_a_gross_tax_above_the_deduction(
    year: int, offset: str, reason: str
) -> None:
    """Incapiente one cent below the capacity, the whole credit at it."""
    rules = _rules(year, TaxSector.TERZIARIO, 20)
    ti = rules.trattamento_integrativo
    assert ti is not None
    income = _capacity(year) + _D(offset)
    work = work_income_deduction(income, constants=rules.work_deduction)

    outcome = trattamento_integrativo_outcome(
        income,
        irpef_gross(income, rules),
        work,
        work,
        ti,
        constants=rules.work_deduction,
    )

    assert outcome.reason_code == reason


_PRODUCTION = {
    "commercio-confcommercio": "4",
    "metalmeccanico-federmeccanica": "C3",
    "edilizia-ance-impiegati": "4",
    "pubblici-esercizi-fipe-angem-ristorazione-collettiva": "4",
}


def _month(ccnl: str, events: tuple[Any, ...] = ()) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id=ccnl,
                level_code=_PRODUCTION[ccnl],
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005", events=events),
            prior_year=PriorYearTaxFacts(employment_income=_D(30000)),
        )
    )


@pytest.mark.parametrize("ccnl", sorted(_PRODUCTION))
def test_the_inps_rates_of_a_run_are_those_of_its_sector(ccnl: str) -> None:
    """The IVS share of the worker is the rate of the CCNL's tax sector."""
    sector = _REPO.load_ccnl(ccnl).meta.tax_sector
    inps = _rules(2026, sector, 20).inps
    assert inps is not None
    (ivs,) = (
        c
        for c in _month(ccnl).contribution_breakdown.components
        if c.name == "ivs_employee"
    )

    assert ivs.rate == inps.employee_ivs_rate


def _bases(result: PeriodResult) -> tuple[Decimal, Decimal]:
    ivs = sum(
        (
            c.base
            for c in result.contribution_breakdown.components
            if c.name == "ivs_employee"
        ),
        _D(0),
    )
    return ivs, result.closing_state.cash.earnings.taxable


def test_events_that_share_a_base_add_up_in_it() -> None:
    """A bonus and overtime in one run: each base grows by the sum of both."""
    ccnl = "commercio-confcommercio"
    bonus = BonusEvent(event_date=date(2026, 1, 15), amount=_D(300))
    overtime = OvertimeEvent(event_date=date(2026, 1, 20), hours=_D(5))
    none = _bases(_month(ccnl))
    alone = [_bases(_month(ccnl, (e,))) for e in (bonus, overtime)]
    both = _bases(_month(ccnl, (bonus, overtime)))

    assert both[0] - none[0] == sum((a[0] - none[0] for a in alone), _D(0))
    assert abs((both[1] - none[1]) - sum((a[1] - none[1] for a in alone), _D(0))) <= (
        _D("0.02")
    )
