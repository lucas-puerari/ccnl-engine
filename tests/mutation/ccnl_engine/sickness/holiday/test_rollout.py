"""Contract holiday targets in a period calculation, including excluded holidays."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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
from ccnl_engine.sickness.holiday.rules import covered_holidays
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


def test_logistica_holiday_is_not_topped_up_outside_its_section() -> None:
    """Art. 71 c. 5 is of the ex Magazzini Generali employers: no top-up."""
    assert _may("logistica-trasporto-confetra", "4", WorkerCategory.OPERAIO) == {
        "abs": Decimal("507.13"),
        "inps": Decimal("338.05"),
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


def _holiday_case(
    slug: str, level: str, start: date, holiday: date
) -> dict[str, Decimal]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(holiday.year, holiday.month),
            payment_date=date(holiday.year, holiday.month, 27),
            ccnl_id=slug,
            level_code=level,
            seniority=new_hire(start.year),
            opening_state=PeriodState.zero(),
            events=(sickness_episode(start.isoformat(), start, holiday),),
            category=WorkerCategory.OPERAIO,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return {
        i.item_id.rsplit("_", 1)[1]: i.amount
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def test_federmeccanica_target_covers_only_letter_b_national_holidays() -> None:
    """The 2027 Monday 4 October and letter a holidays are outside art. 9(b,c)."""
    work = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert work is not None
    rules = work.sickness_rules
    assert rules is not None
    days = covered_holidays(rules, load_national_holidays(), 2027)
    assert date(2027, 10, 4) not in days
    assert date(2027, 5, 1) not in days
    assert date(2027, 6, 2) not in days
    assert date(2026, 4, 25) not in days
    assert date(2026, 4, 6) in days
    assert date(2027, 1, 6) in days


def test_federmeccanica_may_first_is_excluded_from_holiday_top_up() -> None:
    """May 1, 2026 is letter a: 83.01 * 80% = 66.41 (55.33 + 11.08).

    A blanket target would instead pay 83.01 (integration 27.68).
    """
    assert _holiday_case(
        "metalmeccanico-federmeccanica", "C3", date(2025, 12, 1), date(2026, 5, 1)
    ) == {
        "abs": Decimal("83.01"),
        "inps": Decimal("55.33"),
        "intg": Decimal("11.08"),
    }


def test_federmeccanica_easter_monday_receives_holiday_top_up() -> None:
    """April 6, 2026 is letter b: 83.01 * 20% = 16.60 extra.

    The April integration increases from 71.98 to 88.58 with the target.
    """
    assert _holiday_case(
        "metalmeccanico-federmeccanica", "C3", date(2025, 12, 1), date(2026, 4, 6)
    ) == {
        "abs": Decimal("415.05"),
        "inps": Decimal("276.66"),
        "intg": Decimal("88.58"),
    }


def test_confcommercio_may_first_net_basis_cannot_meet_gross_holiday_pay() -> None:
    """May 1, 2026: 68.52 gross, INPS 34.26, existing integration 13.43.

    If rate 1 were encoded, grossed INPS = 34.26 / 0.9024333 = 37.96,
    integration = 68.52 - 37.96 = 30.56; total 64.82, not 68.52.
    Therefore the holiday target is deliberately absent; the gap remains.
    """
    assert _holiday_case(
        "commercio-confcommercio", "4", date(2026, 4, 27), date(2026, 5, 1)
    ) == {
        "abs": Decimal("68.52"),
        "inps": Decimal("34.26"),
        "intg": Decimal("13.43"),
    }
