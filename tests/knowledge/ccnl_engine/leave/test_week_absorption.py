"""The permits a shorter full-time week absorbs (Commercio, Terziario, DMO).

"b) 39 ore settimanali. Si realizza attraverso l'assorbimento di 36 ore di
permesso retribuito di cui al terzo comma dell'art. 158"; "c) 38 ore
settimanali [...] 72 ore di permesso retribuito delle quali 16 al primo comma
dell'art. 158 e 56 al terzo comma". A firm of 10: 56 hours of ROL, 32 of ex
festività on a 40-hour week; the balances hold twelfths of the yearly hours.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _permits(slug: str, week: int | None) -> dict[LeaveBucket, Decimal]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=slug,
            level_code="4" if slug == "commercio-confcommercio" else "IV",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2020, 1, 1)),
            full_time_weekly_hours=None if week is None else WeeklyHours(Decimal(week)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return {
        b.bucket: b.accrued_twelfths
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is not LeaveBucket.FERIE
    }


@pytest.mark.parametrize(
    "slug",
    ["commercio-confcommercio", "terziario-confesercenti", "dmo-federdistribuzione"],
)
@pytest.mark.parametrize(
    ("week", "rol", "ex_festivita"),
    [(None, "56", "32"), (40, "56", "32"), (39, "20", "32"), (38, "0", "16")],
)
def test_the_week_absorbs_its_permits(
    slug: str, week: int | None, rol: str, ex_festivita: str
) -> None:
    """39 hours: 36 of ROL; 38 hours: 56 of ROL and 16 of ex festività."""
    assert _permits(slug, week) == {
        LeaveBucket.ROL: Decimal(rol),
        LeaveBucket.EX_FESTIVITA: Decimal(ex_festivita),
    }
