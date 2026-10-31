"""Indemnity of the residual leave: paid at the CCNL basis, or not at all."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.handlers import LeaveTerms
from ccnl_engine.leave.models import FerieAccrual, LeaveRules, LeaveTermination
from ccnl_engine.leave.permit.models import PermitHours, PermitRules
from ccnl_engine.leave.settlement.services import SettlementTerms, settle_leave
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.pay_item.facade import CompetencePeriod
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.pay_item.policies import PolicyContext

_PERMIT = PermitRules(
    bucket=LeaveBucket.EX_FESTIVITA, annual_hours=(PermitHours(hours=Decimal(32)),)
)
_RULES = LeaveRules(
    default_annual_days=Decimal(26),
    ferie_accrual=FerieAccrual(),
    permits=(_PERMIT,),
    termination=LeaveTermination(ferie_divisor=Decimal(26), permits_hourly=True),
)
_RESOLVER = load_policy_resolver()


def _terms(
    rules: LeaveRules | None = _RULES,
    divisor: Decimal | None = Decimal(168),
    ratio: Decimal | None = None,
) -> SettlementTerms:
    return SettlementTerms(
        leave=LeaveTerms(rules, "ccnl/x", "1"),
        monthly_pay=Decimal("1783.75"),
        hourly_divisor=divisor,
        part_time_ratio=ratio,
        competence_period=CompetencePeriod(year=2026, month=10),
        payment_date=date(2026, 10, 27),
        tag="2026-10-regular",
        resolver=_RESOLVER,
        context=PolicyContext(year=2026, as_of=date(2026, 10, 1)),
    )


def _account(*, exact: bool = True, known: bool = True) -> LeaveAccount:
    return LeaveAccount(
        (
            LeaveBalance(LeaveBucket.FERIE, 2026, Decimal(260), Decimal(120)),
            LeaveBalance(
                LeaveBucket.EX_FESTIVITA, 2026, Decimal(320), Decimal(192), exact=exact
            ),
        ),
        known=known,
    )


def test_residual_is_paid_and_settled() -> None:
    """140/12 days at 1,783.75 / 26 and 128/12 hours at 1,783.75 / 168."""
    settlement = settle_leave(_account(), _terms())

    assert [i.amount for i in settlement.items] == [
        Decimal("800.40"),
        Decimal("113.25"),
    ]
    assert settlement.decision.status is CalculationStatus.FINAL
    assert settlement.decision.amount == Decimal("913.65")
    assert settlement.inps_base == settlement.tfr_base == settlement.irpef_base
    assert settlement.account.unsettled() == ()
    assert len(settlement.entries) == 2


def test_part_time_permits_are_paid_at_the_full_time_hourly_quota() -> None:
    """A half-time worker's hour is worth the full-time pay over 168."""
    settlement = settle_leave(_account(), _terms(ratio=Decimal("0.5")))

    assert settlement.items[1].amount == Decimal("226.51")


_DAILY = _RULES.model_copy(
    update={
        "permits": (_PERMIT.model_copy(update={"day_hours": Decimal(8)}),),
        "termination": LeaveTermination(
            ferie_divisor=Decimal(26), permits_hourly=False
        ),
    }
)


@pytest.mark.parametrize(
    ("ratio", "amount"), [(None, Decimal("91.47")), (Decimal("0.5"), Decimal("182.95"))]
)
def test_permits_paid_by_the_day_need_no_hourly_divisor(
    ratio: Decimal | None, amount: Decimal
) -> None:
    """128/12 hours are 1.3333 days of 8 hours at the full-time pay over 26.

    Full time: 10.6667 x 1,783.75 / (26 x 8) = 91.47; half time: the hours
    were accrued at half, the day is the full-time one, 1,783.75 / 0.5.
    """
    settlement = settle_leave(
        _account(), _terms(rules=_DAILY, divisor=None, ratio=ratio)
    )

    assert settlement.decision.reason_code == "residual_leave_paid"
    assert settlement.items[1].amount == amount


def test_inexact_balance_gives_a_provisional_payment() -> None:
    """A balance resting on an estimate is paid, provisionally."""
    decision = settle_leave(_account(exact=False), _terms()).decision

    assert (decision.status, decision.reason_code) == (
        CalculationStatus.PROVISIONAL,
        "residual_leave_estimated",
    )


def test_nothing_left_is_a_final_zero() -> None:
    """A settled account pays nothing, finally."""
    settlement = settle_leave(_account().settled(), _terms())

    assert settlement.items == ()
    assert (settlement.decision.reason_code, settlement.decision.amount) == (
        "no_residual_leave",
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("account", "terms", "reason"),
    [
        (_account(), _terms(rules=None), "leave_accrual_not_modelled"),
        (_account(known=False), _terms(), "leave_history_unknown"),
        (
            LeaveAccount((
                LeaveBalance(LeaveBucket.FERIE, 2026, Decimal(0), Decimal(12)),
            )),
            _terms(),
            "leave_taken_beyond_accrual",
        ),
        (
            _account(),
            _terms(rules=_RULES.model_copy(update={"termination": None})),
            "termination_basis_not_sourced",
        ),
        (_account(), _terms(divisor=None), "permit_basis_not_sourced"),
        (
            _account(),
            _terms(
                rules=_RULES.model_copy(
                    update={
                        "termination": LeaveTermination(
                            ferie_divisor=Decimal(26), permits_hourly=False
                        )
                    }
                )
            ),
            "permit_basis_not_sourced",
        ),
    ],
)
def test_residual_without_a_basis_is_not_paid(
    account: LeaveAccount, terms: SettlementTerms, reason: str
) -> None:
    """No accrual, no history, an overdraft or no basis: incomplete, nothing paid."""
    settlement = settle_leave(account, terms)

    assert settlement.items == ()
    assert settlement.account == account
    assert (settlement.decision.status, settlement.decision.reason_code) == (
        CalculationStatus.INCOMPLETE,
        reason,
    )
    assert bool(settlement.issues) is (reason == "leave_history_unknown")
