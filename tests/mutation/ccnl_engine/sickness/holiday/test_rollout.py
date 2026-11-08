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
    slug: str,
    level: str,
    start: date,
    holiday: date,
    patron: str | None = None,
) -> dict[str, Decimal]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), patron_saint_day=patron),
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


def test_stated_patron_day_tops_up_sickness_but_unknown_does_not() -> None:
    """Eight days at 65.63: first three pay 196.89 in waiting pay.

    Five INPS days pay about 26.25 each. Ordinary integration is 65.63;
    the patron day reaches the full 65.63 instead of the ordinary 75%,
    adding 16.40 (with a one-cent INPS allocation rounding difference).
    """
    first = date(2026, 3, 12)
    last = date(2026, 3, 19)
    ordinary = {
        "abs": Decimal("459.41"),
        "crnz": Decimal("196.89"),
        "inps": Decimal("131.26"),
        "intg": Decimal("65.63"),
    }
    assert (
        _holiday_case("studi-professionali-confprofessioni", "3", first, last)
        == ordinary
    )
    assert _holiday_case(
        "studi-professionali-confprofessioni", "3", first, last, "03-19"
    ) == {**ordinary, "inps": Decimal("131.27"), "intg": Decimal("82.03")}


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


def test_confcommercio_may_first_gross_holiday_pay() -> None:
    """May 1: gross quota 68.52, INPS 34.26, employer 34.26 = 68.52.

    Without the target the employer pays 13.43; using the net basis with
    rate one would pay 30.56, yielding only 64.82 combined.
    """
    assert _holiday_case(
        "commercio-confcommercio", "4", date(2026, 4, 27), date(2026, 5, 1)
    ) == {
        "abs": Decimal("68.52"),
        "inps": Decimal("34.26"),
        "intg": Decimal("34.26"),
    }


def test_confcommercio_holiday_splits_equal_rate_days() -> None:
    """June 1 pays 45.68 + 17.90 = 63.58 on the net basis.

    June 2 pays 45.68 + 22.85 = 68.53 gross, after the two-day
    137.05 deduction rounds once; both days have rate one.
    """
    assert _holiday_case(
        "commercio-confcommercio", "4", date(2026, 4, 1), date(2026, 6, 2)
    ) == {
        "abs": Decimal("137.05"),
        "inps": Decimal("91.36"),
        "intg": Decimal("40.75"),
    }


def test_confcommercio_holiday_calendar_excludes_october_fourth() -> None:
    """Art. 154 omits October 4 but includes May 1, 2026."""
    work = load_ccnl("commercio-confcommercio").work_rules
    assert work is not None
    assert work.sickness_rules is not None
    days = covered_holidays(work.sickness_rules, load_national_holidays(), 2026)
    assert date(2026, 5, 1) in days
    assert date(2026, 10, 4) not in days
