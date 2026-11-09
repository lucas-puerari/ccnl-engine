"""Art. 83 weekly overtime tiers on a hand-computed sport-facilities week."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    MissingRuleError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from ccnl_engine.working_time.overtime.weekly import weekly_rate
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


def test_week_crossing_48_hours() -> None:
    """After 40h, 8h x EUR 10 x 1.15 + 2h x EUR 10 x 1.20 = EUR 116.

    Without the week position, no unthresholded band can supply a multiplier.
    """
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="impianti-sportivi-sport",
                level_code="VI",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(Decimal(40)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(160)),
                events=(
                    OvertimeEvent(
                        date(2026, 3, 10),
                        Decimal(10),
                        Decimal(10),
                        weekly_hours_before=Decimal(40),
                    ),
                ),
            ),
        )
    )
    assert sum(
        (item.amount for item in result.pay_items if item.kind == "overtime_earning"),
        Decimal(0),
    ) == Decimal(116)
    assert "overtime_tier_not_applied" not in {issue.code for issue in result.issues}


def test_uncovered_weekly_hours_cannot_be_guessed() -> None:
    """Before the 41st weekly hour, art. 83 gives no overtime multiplier."""
    rules = load_ccnl("impianti-sportivi-sport").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    bands = rules.time_supplements.overtime_bands
    matching = []
    for band in bands[:2]:
        value = band.rate.periods[0].value
        assert value is not None
        matching.append((band, value))
    event = OvertimeEvent(
        date(2026, 3, 10),
        Decimal(2),
        Decimal(10),
        weekly_hours_before=Decimal(39),
    )
    with pytest.raises(MissingRuleError, match="No weekly overtime band"):
        weekly_rate(event, matching)
