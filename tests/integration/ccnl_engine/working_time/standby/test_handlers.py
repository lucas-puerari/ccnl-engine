"""Standby pay (reperibilità) at the CCNL rates of the worker's level.

Federmeccanica, Sez. Quarta Titolo III art. 6 and the IPCA verbali of 12 June
2025 and 16 June 2026 (rates read on the signed page images): from 1 June
2026 a C3 worker earns 7.00 for 16 hours on a working day, 10.98 for 24 hours
on a rest day, 45.98 a week of 6 days; the hourly rate is 7.00 / 16; 5.00
for each call with an intervention; no TFR (art. 2120 c. 2 c.c.).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.validity.rules import SeriesGapError
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.facade import BonusEvent, StandbyEvent, StandbyKind
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_METAL = "metalmeccanico-federmeccanica.json"


def _run(
    *events: object, month: int = 7, level: str = "C3", ccnl: str = _METAL
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=month),
            payment_date=date(2026, month, 27),
            ccnl_slug=ccnl,
            level_code=level,
            opening_state=PeriodState.zero(),
            events=tuple(events),  # type: ignore[arg-type]
        )
    )


def _account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def _standby(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == "standby_earning"),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("kind", "quantity", "calls", "level", "month", "amount"),
    [
        (StandbyKind.WORKED_DAY, "3", 0, "C3", 7, "21.00"),  # 3 x 7.00
        (StandbyKind.REST_DAY, "2", 1, "C3", 7, "26.96"),  # 2 x 10.98 + 5.00
        (StandbyKind.WEEK, "1", 0, "B1", 7, "53.38"),
        (StandbyKind.HOURS, "8", 0, "D1", 7, "2.94"),  # 8 x 5.87 / 16 = 2.935
        (StandbyKind.WEEK_HOLIDAY_REST_DAY, "1", 0, "A1", 7, "59.27"),
        (StandbyKind.HOLIDAY, "1", 0, "C1", 5, "9.37"),  # June 2025 rate
    ],
    ids=["days", "rest_days_and_a_call", "week", "hours", "week_holiday", "2025"],
)
def test_rate_of_the_band(
    kind: StandbyKind,
    quantity: str,
    calls: int,
    level: str,
    month: int,
    amount: str,
) -> None:
    """The rate of the level's band in force on the event date applies."""
    event = StandbyEvent(date(2026, month, 3), kind, Decimal(quantity), calls)
    result = _run(event, month=month, level=level)

    assert _standby(result) == Decimal(amount)
    (decision,) = (d for d in result.decisions if d.capability == "standby")
    assert decision.amount == Decimal(amount)
    assert reconcile(result, PeriodState.zero()).ok


def test_standby_is_income_without_tfr() -> None:
    """Taxed and contributory like a bonus of the same amount, out of the TFR base."""
    event = StandbyEvent(date(2026, 7, 3), StandbyKind.WEEK, Decimal(1))
    standby = _run(event)
    same = _run(BonusEvent(date(2026, 7, 3), Decimal("45.98"), kind="contract_renewal"))

    assert _account(standby, AccountKind.EMPLOYEE_CONTRIBUTIONS) == _account(
        same, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    # A renewal increment is out of the TFR base too: the accrual is the
    # same, both lowered by the 0.50% of L. 297/1982 on the larger INPS base.
    assert _account(standby, AccountKind.TFR_ACCRUAL) == _account(
        same, AccountKind.TFR_ACCRUAL
    )


def test_ccnl_without_rates_fails_closed() -> None:
    """A CCNL without standby rates rejects the event."""
    event = StandbyEvent(date(2026, 7, 3), StandbyKind.WEEK, Decimal(1))
    with pytest.raises(MissingRuleError, match="no standby rates"):
        _run(event, level="4", ccnl="commercio-confcommercio.json")


def test_rates_before_june_2025_are_a_declared_gap() -> None:
    """The 2021 table and the 2022-2024 updates are not extracted: a gap."""
    work = load_ccnl(_METAL).work_rules
    assert work is not None
    assert work.standby_rules is not None
    series = work.standby_rules.bands[0].rates.week
    with pytest.raises(SeriesGapError):
        series.value_at(date(2024, 7, 1))


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"quantity": Decimal(0)}, "quantity"),
        ({"calls": -1}, "calls"),
        ({"kind": "monthly"}, "kind"),
    ],
)
def test_invalid_events_are_rejected(kwargs: dict[str, object], field: str) -> None:
    """Quantity above 0, calls at least 0, a known unit."""
    fields: dict[str, object] = {
        "event_date": date(2026, 7, 3),
        "kind": StandbyKind.WEEK,
        "quantity": Decimal(1),
    }
    fields.update(kwargs)
    with pytest.raises(InvalidInputError, match=field):
        StandbyEvent(**fields)  # type: ignore[arg-type]
