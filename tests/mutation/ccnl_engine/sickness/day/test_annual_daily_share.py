"""A hypothetical EUR 80 reference wage gives EUR 20 per eligible day.

A recognized five-day illness receives EUR 60 on waiting days 1-3 and
EUR 40 on days 4-5, on top of (not instead of) the statutory indemnity.
After 89 prior paid days the same five-day illness receives only EUR 20.
These synthetic wages illustrate Art. 62; no provincial wage is asserted.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.sickness.day.models import SickPayRules
from ccnl_engine.sickness.day.rules import SickDayKind, classify_days
from ccnl_engine.sickness.indemnity.models import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)
from ccnl_engine.sickness.integration.models import SicknessRules
from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory
from ccnl_engine.sickness.pay.handlers import episode_pay
from ccnl_engine.sickness.term.rules import DailyQuota, SicknessTerms

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_START = date(2026, 7, 6)
_WAGE = {2026: Decimal(80)}
_EMPTY_HISTORY = SicknessHistory()
_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[SickPayBand(day_from=4, day_to=180, rate=Decimal("0.5"))],
    annual_max_days=180,
    coverage=(SickPayCoverage(covered=True, source="synthetic test"),),
)


def _rules(*, florovivaisti: bool = True, fixed_term: bool = False) -> SickPayRules:
    contract = load_ccnl("operai-agricoli-florovivaisti")
    assert contract.work_rules is not None
    work = contract.work_rules
    ccnl = (
        work.subsector_rules["florovivaisti"].sickness_rules
        if florovivaisti
        else work.sickness_rules
    )
    assert ccnl is not None
    return SickPayRules(_INPS, True, ccnl, fixed_term=fixed_term)


def _episode(
    identifier: str,
    first: date,
    length: int,
    *,
    recognized: bool | None = True,
    wages: dict[int, Decimal] | None = _WAGE,
) -> SicknessEpisode:
    return SicknessEpisode(
        identifier,
        first,
        first + timedelta(days=length - 1),
        inps_recognized=recognized,
        contractual_daily_wage_by_year=wages,
    )


def _pay(
    episode: SicknessEpisode,
    history: SicknessHistory = _EMPTY_HISTORY,
    *,
    florovivaisti: bool = True,
) -> tuple[Decimal, Decimal]:
    rules = _rules(florovivaisti=florovivaisti)
    terms = SicknessTerms(
        rules=rules,
        history=history,
        quota=DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        chain=MonthlyPayChain(base=Decimal(2600), seniority=Decimal(0), allowances=()),
    )
    result = episode_pay(episode, (episode.started_on, episode.ended_on), terms)
    assert result is not None
    return result.carenza, result.integration


def test_five_days_pay_waiting_days_retroactively() -> None:
    """EUR 80 * 25% * 3 = 60 carenza; two later days add EUR 40."""
    episode = _episode("five", _START, 5)
    assert _pay(episode) == (Decimal(60), Decimal(40))
    assert _pay(episode, florovivaisti=False) == (Decimal(0), Decimal(0))


def test_three_days_or_unrecognized_illness_pay_no_supplement() -> None:
    """Three days do not exceed three: EUR 0; no recognition also EUR 0."""
    assert _pay(_episode("three", _START, 3)) == (Decimal(0), Decimal(0))
    assert _pay(_episode("denied", _START, 5, recognized=False)) == (
        Decimal(0),
        Decimal(0),
    )
    assert _pay(_episode("unknown", _START, 5, wages=None)) == (Decimal(0), Decimal(0))


def test_annual_cap_across_episodes_and_year_reset() -> None:
    """89 previous days leave one at EUR 20, not five at EUR 100."""
    earlier = _episode("prior", date(2026, 3, 1), 89)
    later = _episode("later", _START, 5)
    history = SicknessHistory((earlier,))
    assert _pay(later, history) == (Decimal(20), Decimal(0))
    at_cap = SicknessHistory((_episode("full", date(2026, 3, 1), 90),))
    assert _pay(later, at_cap) == (Decimal(0), Decimal(0))
    segments = classify_days(
        later, (later.started_on, later.ended_on), history, _rules()
    )
    assert [(s.kind, s.daily_share) for s in segments] == [
        (SickDayKind.CARENZA, Decimal("0.25")),
        (SickDayKind.CARENZA, Decimal(0)),
        (SickDayKind.INDEMNIFIED, Decimal(0)),
    ]
    next_year = _episode("next", date(2027, 7, 5), 5, wages={2027: Decimal(80)})
    assert _pay(next_year, history) == (Decimal(60), Decimal(40))


def test_period_selects_the_subsector_and_flags_missing_facts() -> None:
    """Five days at EUR 80: the sub-sector adds EUR 60 + EUR 40; default EUR 0."""

    def run(subsector: str | None, episode: SicknessEpisode) -> PeriodResult:
        return PayrollEngine.bundled().calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 7),
                payment_date=date(2026, 7, 27),
                employment=Employment(
                    ccnl_id="operai-agricoli-florovivaisti",
                    level_code="Area1",
                    category=WorkerCategory.OPERAIO,
                    contract_type=Permanent(),
                    employment_period=EmploymentPeriod(date(2026, 1, 1), None),
                    seniority=SeniorityFact.since(
                        date(2026, 1, 1), SenioritySource.EMPLOYER_RECORDS
                    ),
                    pension_fund=NoPensionFund(),
                    tfr_treasury_fund=False,
                ),
                employer=EmployerProfile(headcount=Headcount(20), subsector=subsector),
                facts=PeriodFacts(events=(episode,)),
            )
        )

    flor = run("florovivaisti", _episode("five", _START, 5))
    agric = run(None, _episode("five", _START, 5))
    flor_decision = next(d for d in flor.decisions if d.capability == "sickness")
    agric_decision = next(d for d in agric.decisions if d.capability == "sickness")
    assert flor_decision.inputs["employer_share_wage_reference"] == (
        "02-01 each calendar year"
    )
    assert flor_decision.inputs["carenza_pay"] == Decimal(60)
    assert flor_decision.inputs["employer_integration"] == Decimal(40)
    assert agric_decision.inputs["carenza_pay"] == Decimal(0)
    assert agric_decision.inputs["employer_integration"] == Decimal(0)
    unknown = run("florovivaisti", _episode("unknown", _START, 5, recognized=None))
    assert "sickness_recognition_unknown" in {i.code for i in unknown.issues}
    no_wage = run("florovivaisti", _episode("no_wage", _START, 5, wages=None))
    assert "sickness_reference_wage_unknown" in {i.code for i in no_wage.issues}


@pytest.mark.parametrize(
    ("recognized", "wages"),
    [("yes", _WAGE), (True, {2026: Decimal(-1)})],
)
def test_reference_facts_are_validated(
    recognized: bool, wages: dict[int, Decimal]
) -> None:
    """A negative reference wage or non-Boolean recognition is not payable."""
    with pytest.raises(InvalidInputError):
        _episode("bad", _START, 5, recognized=recognized, wages=wages)


def test_annual_share_cannot_omit_its_cap_or_reference_date() -> None:
    """A 25% share without the sourced 90-day cap must not pay uncapped days."""
    with pytest.raises(ValueError, match="annual cap"):
        SicknessRules(
            carenza_integration_rate=Decimal(0),
            full_pay_integration_rate=Decimal(0),
            annual_daily_share=Decimal("0.25"),
            daily_share_min_days=3,
        )


@pytest.mark.parametrize("fixed_term", [True, False])
def test_only_permanent_workers_take_the_permanent_rule(fixed_term: bool) -> None:
    """Five days at EUR 20 each: permanent EUR 100, fixed-term EUR 0."""
    episode = _episode("term", _START, 5)
    segments = classify_days(
        episode,
        (_START, episode.ended_on),
        SicknessHistory(),
        _rules(fixed_term=fixed_term),
    )
    total = sum(
        (
            Decimal((s.last - s.first).days + 1) * s.daily_share * Decimal(80)
            for s in segments
        ),
        Decimal(0),
    )
    assert total == (Decimal(0) if fixed_term else Decimal(100))
