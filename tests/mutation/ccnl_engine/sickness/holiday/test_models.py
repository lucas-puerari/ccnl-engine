"""A national holiday falling in a sickness: the CCNL target of the day.

Studi professionali art. 124: the employer tops the INPS indemnity of a
festività in a sickness up to 100% of the pay.  A Studi impiegato of
level 3 sick from Monday 27 April to Friday 8 May 2026 is paid in May at
75% on days 4-20 (art. 117); Friday 1 May reaches 100%: the integration
of May rises by 25% of the daily quota, 459.41 / 7 = 65.63, by 16.41, from
114.85 to 131.26.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

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
from ccnl_engine.sickness.cumulation.rules import CcnlDay
from ccnl_engine.sickness.day.models import SickPayRules
from tests.integration.ccnl_engine.sickness.builders import sickness_episode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_MAY_1 = date(2026, 5, 1)


def _may(slug: str, level: str) -> dict[str, Decimal]:
    episode = sickness_episode("2026-04-27", date(2026, 4, 27), date(2026, 5, 8))
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(2026, 5),
            payment_date=date(2026, 5, 27),
            ccnl_id=slug,
            level_code=level,
            seniority=new_hire(),
            opening_state=PeriodState.zero(),
            events=(episode,),
            category=WorkerCategory.IMPIEGATO,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return {
        i.item_id.rsplit("_", 1)[1]: i.amount
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def test_the_holiday_of_studi_reaches_one_hundred_percent() -> None:
    """1 May at 100% instead of 75%: 114.85 + 16.41."""
    assert _may("studi-professionali-confprofessioni", "3") == {
        "abs": Decimal("459.41"),
        "inps": Decimal("229.71"),
        "intg": Decimal("131.26"),
    }


def _rules(*, holiday: bool) -> SickPayRules:
    rules = SimpleNamespace(
        holiday=SimpleNamespace(rate=Decimal(1)) if holiday else None
    )
    return SickPayRules(
        inps=cast("object", None),  # type: ignore[arg-type]
        inps_cover=True,
        ccnl=cast("object", rules),  # type: ignore[arg-type]
        holidays=frozenset({_MAY_1}),
    )


def _day(*, beyond: bool = False) -> CcnlDay:
    return CcnlDay(
        beyond_comporto=beyond, rate=Decimal("0.75"), carenza_rate=Decimal(0)
    )


def test_the_target_rises_only_on_a_holiday_within_the_comporto() -> None:
    """The holiday and its carenza reach 100%; other days and the comporto do not."""
    treatment = _rules(holiday=True)._with_holidays(lambda _i, _d: _day())
    assert treatment(5, _MAY_1) == CcnlDay(False, Decimal(1), Decimal(1))
    assert treatment(5, date(2026, 5, 4)) == _day()
    beyond = _rules(holiday=True)._with_holidays(lambda _i, _d: _day(beyond=True))
    assert beyond(5, _MAY_1) == _day(beyond=True)


def test_without_the_clause_the_treatment_is_unchanged() -> None:
    """No holiday rule: the treatment of the CCNL itself."""

    def plain(_index: int, _day_date: date) -> CcnlDay:
        return _day()

    assert _rules(holiday=False)._with_holidays(plain) is plain
