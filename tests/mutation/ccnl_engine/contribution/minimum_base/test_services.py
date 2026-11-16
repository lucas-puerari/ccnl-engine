"""Minimum INPS base of a run by qualifica, through the period calculation.

INPS circ. 6/2026 allegato 1, Tabella A: the daily minimum of a qualifica
other than the 58.13 of D.L. 463/1983 art. 7 c. 1 (Agricoltura: impiegato
67.84, dirigente 128.65, operaio 51.70, kept by art. 7 c. 5 from the
adjustment to 58.13).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.contribution.minimum_base.services import ISSUE_CODE
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.inputs import ContributableHours, WeeklyHours
from ccnl_engine.employment.fixed_term.inputs import FixedTerm, NaspiExclusion
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_OPERAI = "operai-agricoli-florovivaisti"


def _run(ccnl: str, level: str, **kwargs: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=ccnl,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(10)),
            opening_state=PeriodState.zero(),
            tfr_treasury_fund=False,
            **kwargs,  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _minimum(result: PeriodResult) -> tuple[object, object]:
    (decision,) = (d for d in result.decisions if d.capability == "inps_employee")
    return decision.inputs["base"], decision.inputs.get("minimum_base_reason")


def test_operaio_agricolo_is_raised_to_51_70() -> None:
    """Area3, March 2026: 991.85 is raised to 26 x 51.70 = 1,344.20."""
    result = _run(_OPERAI, "Area3", category=WorkerCategory.OPERAIO)
    assert _minimum(result) == (Decimal(1344), "raised_to_minimum")


def test_operaio_agricolo_above_51_70_keeps_the_pay() -> None:
    """Area1, March 2026: 1,458.61 is above 1,344.20 though below 1,511.38."""
    result = _run(_OPERAI, "Area1", category=WorkerCategory.OPERAIO)
    assert _minimum(result) == (Decimal(1459), "above_minimum")


def test_part_time_operaio_takes_the_hourly_8_94() -> None:
    """20 of 39 hours: 8.94 x 20 x 26 / 6 = 774.80, the 58.13 of par. 5."""
    result = _run(
        _OPERAI,
        "Area3",
        category=WorkerCategory.OPERAIO,
        weekly_hours=WeeklyHours(Decimal(20)),
        full_time_weekly_hours=WeeklyHours(Decimal(39)),
    )
    assert _minimum(result) == (Decimal(775), "raised_to_minimum")


def test_apprentice_operaio_keeps_the_pay() -> None:
    """Art. 7 c. 5 excludes apprentices as such, whatever the category."""
    result = _run(
        _OPERAI,
        "Area1",
        category=WorkerCategory.OPERAIO,
        contract_type=Apprentice(months_elapsed=6),
    )
    assert _minimum(result) == (Decimal(992), "apprentice_excluded")


def test_unknown_category_of_the_operai_is_undetermined() -> None:
    """51.70 or 58.13: without the category the minimum cannot be fixed."""
    result = _run(_OPERAI, "Area3")
    assert _minimum(result) == (Decimal(992), "category_unknown")


def test_impiegato_agricolo_takes_67_84() -> None:
    """1,686.76 is raised to 26 x 67.84 = 1,763.84."""
    result = _run("impiegati-tecnici-agricoli", "1", category=WorkerCategory.IMPIEGATO)
    assert _minimum(result) == (Decimal(1764), "raised_to_minimum")


def _otd(presence_days: int | None) -> PeriodResult:
    return _run(
        _OPERAI,
        "Area2",
        category=WorkerCategory.OPERAIO,
        contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
        weekly_hours=WeeklyHours(Decimal(39)),
        full_time_weekly_hours=WeeklyHours(Decimal(39)),
        ordinary_hours_worked=ContributableHours(Decimal(100)),
        presence_days=presence_days,
    )


def test_otd_minimum_counts_the_days_of_presence() -> None:
    """100 hours over 25 days: 1,026.73 is raised to 25 x 51.70 = 1,292.50."""
    assert _minimum(_otd(25)) == (Decimal(1293), "raised_to_minimum")


def test_otd_without_days_names_the_fact() -> None:
    """Below 1,344.20 without the days the minimum misses presence_days."""
    result = _otd(None)
    (issue,) = (i for i in result.issues if i.code == ISSUE_CODE)
    assert _minimum(result) == (Decimal(1027), "presence_days_unknown")
    assert issue.fact == "presence_days"
