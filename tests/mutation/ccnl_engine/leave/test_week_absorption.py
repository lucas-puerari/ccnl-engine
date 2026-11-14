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

_ROMAN = {"terziario-confesercenti", "dmo-federdistribuzione"}


def _permits(
    slug: str, week: int | None, subsector: str | None = None, headcount: int = 10
) -> dict[LeaveBucket, Decimal]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(headcount), subsector=subsector
            ),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=slug,
            level_code="IV" if slug in _ROMAN else "4",
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


@pytest.mark.parametrize(
    "slug",
    ["commercio-confcommercio", "terziario-confesercenti", "dmo-federdistribuzione"],
)
def test_a_supermarket_absorbs_72_hours_of_rol(slug: str) -> None:
    """Art. 134 (DMO 119): the 56 of the third comma and the 16 of the fourth.

    A firm of 20 has 72 hours of ROL: all absorbed, the ex festività kept.
    """
    assert _permits(slug, 38, "grande_distribuzione", 20) == {
        LeaveBucket.ROL: Decimal(0),
        LeaveBucket.EX_FESTIVITA: Decimal(32),
    }


def test_another_shop_of_a_firm_of_20_follows_art_133() -> None:
    """Art. 133 c): 56 of ROL and 16 of ex festività, 16 of ROL left."""
    assert _permits("commercio-confcommercio", 38, None, 20) == {
        LeaveBucket.ROL: Decimal(16),
        LeaveBucket.EX_FESTIVITA: Decimal(16),
    }


@pytest.mark.parametrize(
    ("subsector", "rol"), [(None, "104"), ("stabilimenti_balneari", "108")]
)
def test_the_stabilimenti_balneari_accrue_108_hours(
    subsector: str | None, rol: str
) -> None:
    """Turismo art. 111: 104 hours of reduction, 108 for the balneari (c. 2)."""
    accrued = _permits("turismo-federalberghi", None, subsector)

    assert accrued[LeaveBucket.ROL] == Decimal(rol)


@pytest.mark.parametrize(
    ("week", "rol", "ex_festivita"), [(40, "72", "32"), (38, "24", "0")]
)
def test_the_cooperative_38_hour_week_leaves_24_hours(
    week: int, rol: str, ex_festivita: str
) -> None:
    """ANCC Allegato 13 and art. 115: 38 hours absorb 80 of 104, 24 remain."""
    assert _permits("distribuzione-cooperativa-ancc", week) == {
        LeaveBucket.ROL: Decimal(rol),
        LeaveBucket.EX_FESTIVITA: Decimal(ex_festivita),
    }


def test_the_small_cooperative_has_66_hours_in_march_2026() -> None:
    """ANCC art. 147 (2024): 60 hours and 6 from April 2025; 6 more in April 2026."""
    assert _permits(
        "distribuzione-cooperativa-ancc", 40, subsector="piccola_impresa_minore"
    ) == {LeaveBucket.ROL: Decimal(34), LeaveBucket.EX_FESTIVITA: Decimal(32)}


def test_a_new_hire_of_a_small_cooperative_takes_the_hours_in_full() -> None:
    """No ramp in the small imprese minori: a hire of 2026 accrues 28 + 6 hours."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(10), subsector="piccola_impresa_minore"
            ),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="distribuzione-cooperativa-ancc",
            level_code="4",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
            full_time_weekly_hours=WeeklyHours(Decimal(40)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    rol = [
        b.accrued_twelfths
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is LeaveBucket.ROL
    ]
    assert rol == [Decimal(34)]
