"""FEDERDAT art. 89: the ferie of a guard by rota (25, 23 or 22 days).

"25 giorni di lavoro quando si applica il sistema 5 + 1 [...] 23 giorni di
lavoro quando si applica il sistema 6 + 1 + 1 [...] 22 giorni di lavoro
quando si applica il sistema 5 + 2" (CCNL 9 luglio 2026, p. 45).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.rota.inputs import Rota
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.models import LeaveEntitlementTier
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.rota.rules import with_rota

_GPG = "vigilanza-privata-federdat-gpg"


@pytest.mark.parametrize(
    ("rota", "days"),
    [
        (None, "25"),
        (Rota.FIVE_ONE, "25"),
        (Rota.SIX_ONE_ONE, "23"),
        (Rota.FIVE_TWO, "22"),
    ],
)
def test_the_ferie_of_the_rota(rota: Rota | None, days: str) -> None:
    """The days of a year of the rota; the 25 of 5+1 when unstated."""
    leave = with_rota(load_ccnl(_GPG), rota).work_rules.leave_rules  # type: ignore[union-attr]
    assert leave is not None
    assert leave.default_annual_days == Decimal(days)


def test_a_ccnl_without_rota_days_is_unchanged() -> None:
    """A CCNL that sets no days by rota keeps its own."""
    ccnl = load_ccnl("commercio-confcommercio")

    assert with_rota(ccnl, Rota.SIX_ONE_ONE) is ccnl


def test_rota_days_exclude_seniority_tiers() -> None:
    """Days by rota and seniority tiers are two rules of the same days."""
    leave = load_ccnl(_GPG).work_rules.leave_rules  # type: ignore[union-attr]
    assert leave is not None
    tier = LeaveEntitlementTier(service_months_min=0, annual_days=Decimal(25))
    with pytest.raises(ValidationError, match="rota_annual_days"):
        leave.model_validate({**leave.model_dump(), "entitlement_tiers": [tier]})


@pytest.mark.parametrize(
    ("rota", "twelfths"),
    [
        (None, "25"),
        (Rota.FIVE_ONE, "25"),
        (Rota.SIX_ONE_ONE, "23"),
        (Rota.FIVE_TWO, "22"),
    ],
)
def test_a_month_accrues_a_twelfth_of_the_rota(
    rota: Rota | None, twelfths: str
) -> None:
    """Art. 89: one month earns 25/12, 23/12 or 22/12 days (25, 23 or 22 twelfths)."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=_GPG,
            level_code="IV",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
            rota=rota,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (ferie,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is LeaveBucket.FERIE
    ]

    assert ferie.accrued_twelfths == Decimal(twelfths)
