"""The permits of a year not taken: paid at its end or at the deadline (art. 158).

Commercio art. 158 (testo unico 2019, p. 156): "I permessi non fruiti entro
l'anno di maturazione decadranno e saranno pagati con la retribuzione di
fatto [...] in atto al momento della scadenza, oppure potranno essere fruiti
in epoca successiva e comunque non oltre il 30 giugno dell'anno successivo".
A hire of 1 January 2026 accrues no ROL for two years (the new-hire ramp)
and 32 hours of ex festività in 2026, 352 twelfths by the end of November.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_EX = LeaveBucket.EX_FESTIVITA


def _run(
    carryover: bool | None, period: PeriodId, *balances: LeaveBalance
) -> PeriodResult:
    opening = PeriodState.zero()
    opening = replace(
        opening, accrual=replace(opening.accrual, leave=LeaveAccount(balances))
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(10), permit_carryover=carryover
            ),
            period_id=period,
            payment_date=date(period.year, period.month, 27),
            ccnl_id="commercio-confcommercio",
            level_code="4",
            opening_state=opening,
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _paid(result: PeriodResult) -> dict[str, Decimal]:
    return {
        i.item_id.split("_")[1]: i.quantity
        for i in result.pay_items
        if i.item_id.startswith("leave_")
    }


def _balance(result: PeriodResult, year: int) -> LeaveBalance:
    (balance,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is _EX and b.year == year
    ]
    return balance


_NOVEMBER = LeaveBalance(_EX, 2026, Decimal(352), Decimal(0))


def test_paid_with_the_december_pay() -> None:
    """December accrues the last twelfth and pays the 32 hours of 2026."""
    december = _run(False, PeriodId(2026, 12), _NOVEMBER)

    assert _paid(december) == {"ex": Decimal(32)}
    assert _balance(december, 2026).settled
    (decision,) = [d for d in december.decisions if d.capability == "leave"]
    assert decision.rule.endswith("work_rules.leave_rules.permit_deadline")
    assert decision.source is not None
    assert decision.source.page == "156"
    assert decision.amount == sum(
        (i.amount for i in december.pay_items if i.item_id.startswith("leave_")),
        Decimal(0),
    )
    (item,) = [i for i in december.pay_items if i.item_id.startswith("leave_")]
    assert "at the deadline" in str(item.source)


@pytest.mark.parametrize("carryover", [True, None])
def test_december_pays_nothing_unless_the_year_ends_the_permits(
    carryover: bool | None,
) -> None:
    """Carried, or with the choice unknown, the December pay holds no permit."""
    december = _run(carryover, PeriodId(2026, 12), _NOVEMBER)

    assert not _paid(december)
    assert not _balance(december, 2026).settled


def test_carried_and_paid_with_the_june_pay() -> None:
    """Carried: the 2026 hours left after those taken by June are paid in June."""
    june = _run(
        True, PeriodId(2027, 6), LeaveBalance(_EX, 2026, Decimal(384), Decimal(120))
    )

    assert _paid(june) == {"ex": Decimal(22)}
    assert _balance(june, 2026).settled
    assert not _balance(june, 2027).settled


def test_an_unknown_choice_names_the_fact() -> None:
    """The run of December asks for EmployerProfile.permit_carryover."""
    december = _run(None, PeriodId(2026, 12), _NOVEMBER)

    assert "permit_carryover" in {b.detail for b in december.blockers}
    assert "permit_carryover" not in {
        b.detail for b in _run(None, PeriodId(2026, 11)).blockers
    }
