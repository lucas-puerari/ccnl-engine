"""Logistica and lavoro domestico against independent cost examples.

- Logistica, impiegati non viaggianti, January 2026: cost table of the
  Ministry of Labour (DD 135 of 19 December 2025, sha256
  91858281e9567597b56506c663222e985f2387b607e7e257e5cf23dc60b3b9b5, p. 9):
  level 3S with 3 scatti, minimo 23.644,44, EPA 360, scatti 892,44 and EDR
  120 a year.  The table applies INPS at 29.44%, the engine 29.36% above 50
  employees: the deviation is recorded in the review log.
- Lavoro domestico non convivente, level CS, 2026: the worked examples of
  money.it (sha256
  d0273281a532a089647d38f454f67442e86a670e51792426195da2650b2e7b3f): 8,30
  an hour; INPS 0,43 and 1,27 an hour up to 24 hours a week at an effective
  pay up to 9,61, 0,31 and 0,93 above 24 hours.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine import Employment, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    ContributableHours,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.pay_item.models import (
    BaseSalaryEarning,
    FixedAllowanceEarning,
    SeniorityEarning,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import EMPLOYER, regular_period

_CENT = Decimal("0.01")


def _monthly(annual: str) -> Decimal:
    return (Decimal(annual) / 12).quantize(_CENT, ROUND_HALF_UP)


def test_logistica_impiegato_3s_january_2026() -> None:
    """Minimo with EPA, scatti and EDR of the table."""
    result = regular_period(
        employment=Employment(
            ccnl_id="logistica-trasporto-confetra",
            level_code="3S",
            seniority=SeniorityFact.since(
                date(2020, 1, 1), SenioritySource.EMPLOYER_RECORDS
            ),
            pension_fund=NoPensionFund(),
            contract_type=Permanent(),
            category=WorkerCategory.IMPIEGATO,
        ),
        employer=replace(EMPLOYER, headcount=Headcount(51)),
        month=1,
    )
    items = result.pay_items
    (base,) = [i.amount for i in items if isinstance(i, BaseSalaryEarning)]
    (scatti,) = [i.amount for i in items if isinstance(i, SeniorityEarning)]
    (edr,) = [i.amount for i in items if isinstance(i, FixedAllowanceEarning)]

    assert base == _monthly("24004.44")
    assert scatti == _monthly("892.44")
    assert edr == _monthly("120.00")


@pytest.mark.parametrize(
    ("weekly", "hours", "worker", "employer"),
    [(20, 86, "0.43", "1.27"), (30, 130, "0.31", "0.93")],
)
def test_domestic_cs_contributions(
    weekly: int, hours: int, worker: str, employer: str
) -> None:
    """The hourly contributions of the guide, by weekly hours."""
    result = regular_period(
        employment=Employment(
            ccnl_id="lavoro-domestico-non-convivente",
            level_code="CS",
            seniority=new_hire(),
            contract_type=Permanent(),
            weekly_hours=WeeklyHours(Decimal(weekly)),
            full_time_weekly_hours=WeeklyHours(Decimal(40)),
        ),
        contributable_hours=ContributableHours(Decimal(hours)),
    )
    rates = {c.name: c.rate for c in result.contribution_breakdown.components}

    assert rates["domestic_employee_per_hour"] == Decimal(worker)
    assert rates["domestic_employer_per_hour"] == Decimal(employer)


def test_domestic_cs_hourly_minimum() -> None:
    """8,30 an hour: 40 hours a week over 52 weeks and 12 months."""
    result = regular_period(
        employment=Employment(
            ccnl_id="lavoro-domestico-non-convivente",
            level_code="CS",
            seniority=new_hire(),
            contract_type=Permanent(),
            weekly_hours=WeeklyHours(Decimal(40)),
            full_time_weekly_hours=WeeklyHours(Decimal(40)),
        ),
        contributable_hours=ContributableHours(Decimal(173)),
    )
    (base,) = [i.amount for i in result.pay_items if isinstance(i, BaseSalaryEarning)]

    assert base == (Decimal("8.30") * 40 * 52 / 12).quantize(_CENT, ROUND_HALF_UP)
