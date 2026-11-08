"""Contract holiday targets in a period calculation, including excluded holidays."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import WorkerCategory
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from tests.integration.ccnl_engine.sickness.builders import sickness_episode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


def _may(
    slug: str, level: str, category: WorkerCategory, *, start_year: int = 2026
) -> dict[str, Decimal]:
    start = date(start_year, 10, 1) if start_year == 2025 else date(2026, 1, 1)
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(2026, 5),
            payment_date=date(2026, 5, 27),
            ccnl_id=slug,
            level_code=level,
            seniority=new_hire(start_year),
            opening_state=PeriodState.zero(),
            events=(sickness_episode(start.isoformat(), start, date(2026, 5, 8)),),
            category=category,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return {
        i.item_id.rsplit("_", 1)[1]: i.amount
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def test_logistica_sedentary_holiday_top_up() -> None:
    """One holiday: daily target 56.36 less half-rate 28.18 = 28.18 extra."""
    assert _may("logistica-trasporto-confetra", "4", WorkerCategory.OPERAIO) == {
        "abs": Decimal("507.13"),
        "inps": Decimal("338.05"),
        "intg": Decimal("28.18"),
    }


def test_logistica_travelling_holiday_top_up() -> None:
    """One holiday: daily target 49.94 less half-rate 24.97 = 24.97 extra."""
    assert _may(
        "logistica-trasporto-confetra-viaggiante", "I110", WorkerCategory.OPERAIO
    ) == {
        "abs": Decimal("449.44"),
        "inps": Decimal("299.60"),
        "intg": Decimal("24.97"),
    }


def test_cinema_sickness_only_holiday_top_up() -> None:
    """Seven paid days: 341.57 / 7 = 48.80; 170.79 + 24.40 = 195.19."""
    assert _may(
        "esercizi-cinematografici-anec",
        "2",
        WorkerCategory.IMPIEGATO,
        start_year=2025,
    ) == {"abs": Decimal("341.57"), "intg": Decimal("195.19")}


def test_confapi_excluded_national_holiday_is_not_topped_up() -> None:
    """May 1 is art. 32(a): eight days at 528.97, INPS 352.61; no top-up."""
    assert _may("metalmeccanico-confapi", "3", WorkerCategory.OPERAIO) == {
        "abs": Decimal("528.97"),
        "inps": Decimal("352.61"),
    }
