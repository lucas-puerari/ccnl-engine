"""Federmeccanica art. 5: the 8 PAR hours of the steel shift workers, in money.

"Per gli stessi lavoratori turnisti addetti al settore siderurgico, tale
permesso di 8 ore è monetizzato [...]; la monetizzazione è corrisposta
insieme alla tredicesima mensilità al valore retributivo sul quale la stessa
è computata" (CCNL 5 febbraio 2021, PDF p. 155).  The run paying the
thirteenth pays 8 hours over the divisor 173 of that thirteenth.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId

_SLUG = "metalmeccanico-federmeccanica"


def _run(
    subsector: str | None,
    shifts: bool | None,
    *,
    thirteenth: bool = True,
    period: EmploymentPeriod | None = None,
    month: int = 12,
) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), subsector=subsector),
            period_id=PeriodId(year=2026, month=month),
            payment_date=date(2026, month, 28),
            ccnl_id=_SLUG,
            level_code="C3",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            qualifying_shifts=shifts,
            employment_period=period,
            run=PayrollRun.thirteenth(2026, 12) if thirteenth else None,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _paid(result: PeriodResult) -> Decimal | None:
    found = [
        i.amount for i in result.pay_items if i.item_id.startswith("permit_monetised_")
    ]
    return found[0] if found else None


def _extra_gross(result: PeriodResult) -> Decimal:
    (amount,) = (
        i.amount for i in result.pay_items if i.item_id.startswith("base_salary_")
    )
    return amount


def test_the_thirteenth_of_a_steel_shift_worker_pays_8_hours() -> None:
    """8 / 173 of the thirteenth paid: 8 x 2211.43 / 173 = 102.26."""
    result = _run("steel", True)
    expected = (Decimal(8) * _extra_gross(result) / Decimal(173)).quantize(
        Decimal("0.01"), ROUND_HALF_UP
    )

    assert _paid(result) == expected == Decimal("102.26")


@pytest.mark.parametrize(
    ("subsector", "shifts"),
    [("steel", False), ("general", True), ("general", False)],
)
def test_other_workers_take_no_money(subsector: str, shifts: bool) -> None:
    """A day worker of steel, or a shift worker outside steel."""
    assert _paid(_run(subsector, shifts)) is None


@pytest.mark.parametrize(
    ("subsector", "shifts"), [("steel", None), (None, True), (None, None)]
)
def test_unstated_facts_pay_no_hours(
    subsector: str | None, shifts: bool | None
) -> None:
    """A pending fact: nothing is paid until the rotation and sector are known."""
    assert _paid(_run(subsector, shifts)) is None


def test_a_regular_month_pays_nothing_and_accrues_no_leave() -> None:
    """The hours are money, never leave: the PAR stays at 124."""
    result = _run("steel", True, thirteenth=False, month=3)

    assert _paid(result) is None
    (rol,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is LeaveBucket.ROL
    ]
    assert rol.accrued_twelfths == Decimal(124)


def test_the_ratei_at_the_termination_carry_the_hours() -> None:
    """A leaver of 30 June: the ratei of the thirteenth and their 8 hours."""
    period = EmploymentPeriod(date(2020, 1, 1), date(2026, 6, 30))
    result = _run("steel", True, thirteenth=False, period=period, month=6)

    paid = _paid(result)
    assert paid is not None
    assert paid > 0
