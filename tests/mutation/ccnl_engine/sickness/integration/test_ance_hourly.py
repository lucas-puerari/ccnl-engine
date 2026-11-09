"""Direct employer integration of hourly building workers under Art. 26.

March 2026 level 1: minimum 1117.36 + ex contingenza 512.87 =
1630.23 per 173 hours, excluding EDR 10.33. Each payable day takes
40/6 hours; Sundays and holidays do not receive the employer coefficient.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.inputs import WeeklyHours
from ccnl_engine.employment.period.inputs import EmploymentPeriod, TerminationCause
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.day.models import SickPayRules
from ccnl_engine.sickness.day.rules import SickDayKind, SickDaySegment
from ccnl_engine.sickness.indemnity.models import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)
from ccnl_engine.sickness.integration.hourly import (
    HourlyEmployerIntegration,
    hourly_employer_pay,
)
from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory
from ccnl_engine.sickness.pay.handlers import episode_pay
from ccnl_engine.sickness.pay.hourly import hourly_segment_pay
from ccnl_engine.sickness.term.rules import DailyQuota, SicknessTerms
from tests.integration.ccnl_engine.sickness.builders import sickness_episode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    ("days", "waiting", "integration"),
    [
        (3, Decimal(0), Decimal(0)),
        (10, Decimal("103.56"), Decimal("143.05")),
        (30, Decimal("197.79"), Decimal("436.26")),
    ],
)
def test_hourly_employer_sickness_episode(
    days: int, waiting: Decimal, integration: Decimal
) -> None:
    """Three days: zero; ten: 3*.5495 = 103.56 and 6*.3795 = 143.05.

    Thirty: 3*1.0495 = 197.79; 15*.3795 plus 8*.1565 = 436.26.
    All multipliers use (1630.23 / 173) * (40 / 6); each day band is
    rounded to cents separately. No sick hours deduct from hourly wages.
    """
    episode = sickness_episode(
        "march-illness", date(2026, 3, 2), date(2026, 3, days + 1)
    )
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_id="edilizia-ance",
        level_code="1",
        seniority=new_hire(),
        opening_state=PeriodState.zero(),
        events=(episode,),
        category=WorkerCategory.OPERAIO,
    )
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    amounts = {
        item.item_id.rsplit("_", 1)[1]: item.amount
        for item in result.pay_items
        if "_evt" in item.item_id
    }
    assert amounts.get("crnz", Decimal(0)) == waiting
    assert amounts.get("intg", Decimal(0)) == integration
    assert "abs" not in amounts
    assert ("missing_fact", "weekly_hours") not in {
        (blocker.code, blocker.detail) for blocker in result.blockers
    }


def _hourly_rule() -> HourlyEmployerIntegration:
    rules = load_ccnl("edilizia-ance").work_rules
    assert rules is not None
    assert rules.sickness_rules is not None
    spec = rules.sickness_rules.hourly_employer_integration
    assert spec is not None
    return spec


def _march_request(episode: SicknessEpisode) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_id="edilizia-ance",
        level_code="1",
        seniority=new_hire(),
        opening_state=PeriodState.zero(),
        events=(episode,),
        category=WorkerCategory.OPERAIO,
    )


def _employer_items(request: PeriodCalculationRequest) -> tuple[Decimal, Decimal]:
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    return (
        sum(
            (i.amount for i in result.pay_items if i.item_id.endswith("_crnz")),
            Decimal(0),
        ),
        sum(
            (i.amount for i in result.pay_items if i.item_id.endswith("_intg")),
            Decimal(0),
        ),
    )


def test_twenty_hour_week_uses_agreed_hours_divided_by_six() -> None:
    """Seven days: (1630.23/173)*(20/6)*(3*.5495+3*.3795) = EUR 87.54."""
    episode = sickness_episode("part-time", date(2026, 3, 2), date(2026, 3, 8))
    request = replace(
        _march_request(episode),
        weekly_hours=WeeklyHours(Decimal(20)),
        full_time_weekly_hours=WeeklyHours(Decimal(40)),
    )
    assert _employer_items(request) == (Decimal("51.78"), Decimal("35.76"))


def test_recognised_relapse_continues_the_inps_day_coefficient() -> None:
    """After 10 days, March 16-20 are days 11-15: 5*.3795*62.821965 = 119.20."""
    prior = sickness_episode("original", date(2026, 3, 2), date(2026, 3, 11))
    relapse = sickness_episode(
        "recognised", date(2026, 3, 16), date(2026, 3, 20), "original"
    )
    request = replace(_march_request(prior), events=(prior, relapse))
    assert _employer_items(request) == (Decimal("103.56"), Decimal("262.25"))


def test_termination_inside_episode_stops_employer_cash() -> None:
    """March 2-6 only: 3*.5495*62.821965 = 103.56; 2*.3795 = 47.68."""
    episode = sickness_episode("ill", date(2026, 3, 2), date(2026, 3, 11))
    request = replace(
        _march_request(episode),
        employment_period=EmploymentPeriod(
            date(2026, 1, 1), date(2026, 3, 6), TerminationCause.RESIGNATION
        ),
    )
    assert _employer_items(request) == (Decimal("103.56"), Decimal("47.68"))


def test_non_hourly_ance_keeps_monthly_target_and_absence() -> None:
    """At 1730/26, 3 waiting days deduct 199.62; legacy zero rate pays zero."""
    agreement = load_ccnl("edilizia-ance").work_rules
    assert agreement is not None
    assert agreement.sickness_rules is not None
    rules = SickPayRules(
        inps=InpsSickPayRates(
            carenza_days=3,
            bands=[SickPayBand(day_from=4, day_to=20, rate=Decimal("0.5"))],
            annual_max_days=180,
            coverage=(SickPayCoverage(covered=True, source="test: covered"),),
        ),
        inps_cover=True,
        ccnl=agreement.sickness_rules,
    )
    episode = SicknessEpisode("monthly", date(2026, 3, 2), date(2026, 3, 4))
    terms = SicknessTerms(
        rules=rules,
        quota=DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        chain=MonthlyPayChain(Decimal(1730), Decimal(0), ()),
        paid_by_the_hour=False,
        history=SicknessHistory(),
    )
    pay = episode_pay(episode, (episode.started_on, episode.ended_on), terms)
    assert pay is not None
    assert pay.absence == Decimal("199.62")
    assert pay.carenza == Decimal(0)


def test_inps_gates_and_episode_end() -> None:
    """A 0.3795 band pays 0 without INPS; day 181 pays 0 with INPS.

    Day 181 without INPS uses 0.5495; day 366 pays 0 after the last
    employer band. The coefficient is applied before hourly rounding.
    """
    spec = _hourly_rule()
    assert spec.coefficient(4, 30, Decimal(0)) == 0
    assert spec.coefficient(181, 181, Decimal("0.5")) == 0
    assert spec.coefficient(181, 181, Decimal(0)) == Decimal("0.5495")
    assert spec.coefficient(366, 366, Decimal(0)) == 0


@pytest.mark.parametrize(
    "kind", [SickDayKind.BEYOND_COMPORTO, SickDayKind.FIXED_TERM_LIMIT]
)
def test_unpaid_days_have_no_employer_hourly_payment(kind: SickDayKind) -> None:
    """A 10 EUR/hour base times 40/6 hours times 0 is EUR 0.00."""
    segment = SickDaySegment(
        first=date(2026, 3, 2),
        last=date(2026, 3, 2),
        first_index=1,
        kind=kind,
        inps_rate=Decimal(0),
        worker_rate=Decimal(0),
    )
    assert hourly_employer_pay(
        _hourly_rule(),
        segment,
        MonthlyPayChain(Decimal(1730), Decimal(0), ()),
        Decimal(173),
        Decimal(40),
        frozenset(),
        30,
    ) == Decimal(0)


def test_hourly_exclusion_leaves_inps_advance_unchanged() -> None:
    """EUR 5.00 advanced by INPS stays EUR 5.00; excluded employer pays zero."""
    day = date(2026, 3, 2)
    segment = SickDaySegment(
        first=day,
        last=day,
        first_index=4,
        kind=SickDayKind.INDEMNIFIED,
        inps_rate=Decimal("0.5"),
        worker_rate=Decimal("0.5"),
    )
    paid = (Decimal(5), Decimal(0), Decimal(0))
    assert (
        hourly_segment_pay(
            paid,
            _hourly_rule(),
            segment,
            SicknessEpisode("ill", day, day),
            SicknessTerms(),
            MonthlyPayChain(Decimal(1730), Decimal(0), ()),
            Decimal(173),
            excluded=True,
        )
        == paid
    )
