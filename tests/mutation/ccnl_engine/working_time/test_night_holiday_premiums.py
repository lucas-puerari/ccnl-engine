"""Hand oracle: the premium of ordinary night work on a holiday, March 2026.

HolidayWorkKind.NIGHT_HOLIDAY pays the 'lavoro festivo notturno' row of
each CCNL on its hourly base over 173, 8 hours:

- Edilizia ANCE art. 19 n. 10: 50%, level 2, 1823.74 -> 42.17;
- Edilizia ANCE impiegati art. 54: 50%, level 3, 1982.05 -> 45.83;
- Metalmeccanico Confapi art. 29 row h: 60%, 55% for shift workers, level
  4, 2049.91 -> 56.88 and 52.14;
- Alimentari art. 31, vini-liquori impiegati: 65%, level 3, 2088.48 ->
  62.78.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.event.facade import HolidayWorkEvent, HolidayWorkKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_EVENT = HolidayWorkEvent(
    date(2026, 3, 19), hours=Decimal(8), kind=HolidayWorkKind.NIGHT_HOLIDAY
)


def _run(
    slug: str,
    level: str,
    roles: frozenset[str],
    subsector: str | None,
    category: WorkerCategory | None,
) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), subsector=subsector),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=slug,
            level_code=level,
            category=category,
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(
                HolidayWorkEvent(
                    _EVENT.event_date,
                    hours=_EVENT.hours,
                    kind=_EVENT.kind,
                    in_periodic_shift=False,
                )
                if slug == "edilizia-ance-impiegati"
                else _EVENT,
            ),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


@pytest.mark.parametrize(
    ("slug", "level", "roles", "subsector", "category", "band", "amount"),
    [
        (
            "edilizia-ance",
            "2",
            frozenset(),
            None,
            None,
            "ANCE_FESTIVO_NOTTURNO",
            "42.17",
        ),
        (
            "edilizia-ance-impiegati",
            "3",
            frozenset(),
            None,
            None,
            "ANCE_IMP_FESTIVO_NOTTURNO",
            "45.83",
        ),
        (
            "metalmeccanico-confapi",
            "4",
            frozenset(),
            None,
            None,
            "CONFAPI_NOTTURNO_FESTIVO",
            "56.88",
        ),
        (
            "metalmeccanico-confapi",
            "4",
            frozenset({"turnista"}),
            None,
            None,
            "CONFAPI_NOTTURNO_FESTIVO_TURNI",
            "52.14",
        ),
        (
            "alimentari-federalimentare",
            "3",
            frozenset(),
            "vini_liquori",
            WorkerCategory.IMPIEGATO,
            "ALIM_NOTTURNO_FESTIVO_VINI_LIQUORI_IMPIEGATI",
            "62.78",
        ),
    ],
)
def test_the_night_holiday_premium(
    slug: str,
    level: str,
    roles: frozenset[str],
    subsector: str | None,
    category: WorkerCategory | None,
    band: str,
    amount: str,
) -> None:
    """The 'festivo notturno' band of each CCNL, 8 hours."""
    (decision,) = (
        d
        for d in _run(slug, level, roles, subsector, category).decisions
        if d.capability == "holiday_work" and d.reason_code == "ccnl_supplement_applied"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))
