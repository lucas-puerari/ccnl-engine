"""Indemnity of the residual leave: paid at the CCNL basis, or not at all."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.event.total.handlers import _EventTotals
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.handlers import LeaveTerms
from ccnl_engine.leave.models import FerieAccrual, LeaveRules, LeaveTermination
from ccnl_engine.leave.permit.models import PermitHours, PermitRules
from ccnl_engine.leave.services import RunLeave, part_time_ratio
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
_ZERO = Decimal(0)

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


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
    assert settlement.decision.inputs == {
        "ferie_residual": Decimal(140) / 12,
        "ex_festivita_residual": Decimal(128) / 12,
        "ferie_divisor": Decimal(26),
        "ex_festivita_divisor": Decimal(168),
        "monthly_pay": Decimal("1783.75"),
    }
    assert [(i.quantity, i.source) for i in settlement.items] == [
        (Decimal(140) / 12, "residual ferie at termination, days"),
        (Decimal(128) / 12, "residual ex_festivita at termination, hours"),
    ]
    assert [e.policy_decision_id for e in settlement.entries] == [
        "it/leave/settlement"
    ] * 2


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


def test_the_indemnity_enters_the_bases_of_the_run() -> None:
    """The run totals take its bases, its decision, its issues and the account."""
    settlement = settle_leave(_account(), _terms())
    unknown = settle_leave(_account(known=False), _terms())
    earlier = CalculationIssue(
        code="earlier",
        message="an earlier issue of the run",
        status=CalculationStatus.PROVISIONAL,
        cause=IssueCause.CONDITION,
    )
    one = Decimal(1)
    totals = _EventTotals(
        inps_base=one,
        tfr_base=one,
        irpef_base=one,
        fringe_value=_ZERO,
        fringe_inps=_ZERO,
        fringe_irpef=_ZERO,
        substitute_base=_ZERO,
        issues=(earlier,),
    )
    added = RunLeave(settlement.account, settlement).added_to(totals)

    assert unknown.issues
    assert (added.inps_base, added.tfr_base, added.irpef_base) == (
        one + settlement.inps_base,
        one + settlement.tfr_base,
        one + settlement.irpef_base,
    )
    assert added.decisions == (settlement.decision,)
    assert added.issues == (earlier,)
    assert RunLeave(unknown.account, unknown).added_to(totals).issues == (
        earlier,
        *unknown.issues,
    )
    assert added.leave is settlement.account


@pytest.mark.parametrize(
    ("weekly", "full", "ratio"),
    [(20, 40, Decimal("0.5")), (None, 40, None), (20, None, None), (40, 40, None)],
)
def test_the_part_time_ratio(
    weekly: int | None, full: int | None, ratio: Decimal | None
) -> None:
    """Weekly over full-time hours, only below one and with both stated."""
    request = SimpleNamespace(
        weekly_hours=None if weekly is None else SimpleNamespace(value=weekly),
        full_time_weekly_hours=None if full is None else SimpleNamespace(value=full),
    )

    assert part_time_ratio(cast("RunContext", SimpleNamespace(request=request))) == (
        ratio
    )


def test_the_decision_cites_the_ccnl_basis() -> None:
    """Commercio: the clause of the indemnity is the source of the decision."""
    work = load_ccnl("commercio-confcommercio").work_rules
    assert work is not None
    rules = work.leave_rules
    assert rules is not None
    assert rules.termination is not None
    assert rules.termination.provenance is not None
    settlement = settle_leave(_account(), _terms(rules=rules))

    assert settlement.decision.source == rules.termination.provenance.location


def test_the_residuals_of_every_year_are_paid_together() -> None:
    """Ferie left of 2025 and of 2026: one item for both."""
    account = LeaveAccount((
        LeaveBalance(LeaveBucket.FERIE, 2025, Decimal(120), Decimal(60)),
        LeaveBalance(LeaveBucket.FERIE, 2026, Decimal(120), Decimal(60)),
    ))
    settlement = settle_leave(account, _terms())

    assert [i.quantity for i in settlement.items] == [Decimal(10)]


def test_a_permit_used_up_needs_no_hourly_basis() -> None:
    """No hourly divisor, but no permit hour left: the ferie are paid."""
    account = LeaveAccount((
        LeaveBalance(LeaveBucket.FERIE, 2026, Decimal(260), Decimal(120)),
        LeaveBalance(LeaveBucket.EX_FESTIVITA, 2026, Decimal(320), Decimal(320)),
    ))
    settlement = settle_leave(account, _terms(divisor=None))

    assert settlement.decision.reason_code == "residual_leave_paid"
