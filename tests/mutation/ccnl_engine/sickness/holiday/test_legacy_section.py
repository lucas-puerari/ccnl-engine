"""Conditional legacy-section holiday pay during sickness."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.inputs import WorkInjuryEvent
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import WorkerCategory
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.holiday.rules import (
    covered_target_holidays,
    legacy_section_issue,
)
from tests.integration.ccnl_engine.sickness.builders import sickness_episode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    ("slug", "level", "deduction", "insurer", "top_up"),
    [
        (
            "logistica-trasporto-confetra",
            "4",
            Decimal("507.13"),
            Decimal("338.05"),
            Decimal("28.18"),
        ),
        (
            "logistica-trasporto-confetra-viaggiante",
            "B3",
            Decimal("551.01"),
            Decimal("367.30"),
            Decimal("30.62"),
        ),
    ],
)
def test_legacy_section_holiday_in_sickness(
    slug: str, level: str, deduction: Decimal, insurer: Decimal, top_up: Decimal
) -> None:
    """May 1 is one of six paid days May 1-8, at two-thirds INPS.

    Non-travelling daily pay is 507.13 / 6 = 84.52; its INPS daily
    share is 338.05 / 6 = 56.34, so 84.52 - 56.34 = 28.18.
    Travelling: 551.01 / 6 = 91.84, 367.30 / 6 = 61.22,
    and 91.84 - 61.22 = 30.62. Without eligibility no top-up is due.
    """
    for fact in (False, True, None):
        result = calculate_period(
            PeriodCalculationRequest(
                employer=EmployerProfile(
                    headcount=Headcount(50), legacy_section_applicable=fact
                ),
                period_id=PeriodId(2026, 5),
                payment_date=date(2026, 5, 27),
                ccnl_id=slug,
                level_code=level,
                seniority=new_hire(2026),
                opening_state=PeriodState.zero(),
                events=(
                    sickness_episode("2026-01-01", date(2026, 1, 1), date(2026, 5, 8)),
                ),
                category=WorkerCategory.OPERAIO,
            ),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        items = {
            item.item_id.rsplit("_", 1)[1]: item.amount
            for item in result.pay_items
            if "_evt" in item.item_id
        }
        expected = {"abs": deduction, "inps": insurer}
        if fact is True:
            expected["intg"] = top_up
        assert items == expected
        blockers = [
            issue
            for issue in result.issues
            if issue.fact == "legacy_section_applicable"
        ]
        assert len(blockers) == (1 if fact is None else 0)
        if fact is None:
            assert blockers[0].code == "missing_fact"
            assert blockers[0].capability == "sickness"


def test_injury_holiday_uses_same_employer_condition() -> None:
    """For May 1, the injury target is 100%; without the fact it is absent."""
    contract = load_ccnl("logistica-trasporto-confetra")
    assert contract.work_rules is not None
    insured = contract.work_rules.insured_absence
    assert insured is not None
    assert insured.injury is not None
    target = insured.injury.holiday
    assert target is not None
    assert target.rate == Decimal(1)
    calendar = load_national_holidays()
    for fact in (False, True, None):
        employer = EmployerProfile(
            headcount=Headcount(50), legacy_section_applicable=fact
        )
        covered = covered_target_holidays(target, calendar, 2026, employer)
        assert (date(2026, 5, 1) in covered) is (fact is True)
        issue = legacy_section_issue(
            target,
            calendar,
            date(2026, 5, 1),
            date(2026, 5, 1),
            employer,
            "workplace_injury",
        )
        assert (issue is not None) is (fact is None)
        if issue is not None:
            assert issue.code == "missing_fact"
            assert issue.capability == "workplace_injury"


def test_injury_event_reports_unknown_legacy_section() -> None:
    """A May 1 injury overlap needs known section-two eligibility."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(2026, 5),
            payment_date=date(2026, 5, 27),
            ccnl_id="logistica-trasporto-confetra",
            level_code="4",
            seniority=new_hire(2026),
            opening_state=PeriodState.zero(),
            events=(WorkInjuryEvent(date(2026, 4, 27), date(2026, 5, 8)),),
            category=WorkerCategory.OPERAIO,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert any(
        issue.code == "missing_fact"
        and issue.fact == "legacy_section_applicable"
        and issue.capability == "workplace_injury"
        for issue in result.issues
    )
