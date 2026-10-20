"""Leave balances: twelfths accrued, leave taken oldest first, settlement."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.types import LeaveBucket

_FERIE = LeaveBucket.FERIE


def _ferie(year: int, accrued: int, taken: int = 0) -> LeaveBalance:
    return LeaveBalance(_FERIE, year, Decimal(accrued), Decimal(taken))


def test_balance_in_days_from_twelfths() -> None:
    """Ten months of 26 days are 260 twelfths: 21.67 days, 11.67 left after 10."""
    balance = _ferie(2026, 260, 120)
    accrued, left = Decimal(260) / 12, Decimal(140) / 12

    assert balance.accrued == accrued
    assert balance.taken == Decimal(10)
    assert balance.residual == left
    assert balance.paid == 0


def test_settled_balance_has_no_residual() -> None:
    """The residual of a settled balance is what was paid."""
    balance = LeaveBalance(_FERIE, 2026, Decimal(260), Decimal(120), settled=True)

    assert balance.residual == 0
    assert balance.residual_twelfths == 0
    paid = Decimal(140) / 12
    assert balance.paid == paid


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"bucket": "annual"}, "LeaveBalance.bucket"),
        ({"year": 1800}, "LeaveBalance.year"),
        ({"accrued_twelfths": Decimal(-1)}, "LeaveBalance.accrued_twelfths"),
        ({"taken_twelfths": 1}, "LeaveBalance.taken_twelfths"),
        ({"settled": 1}, "LeaveBalance.settled"),
        ({"exact": None}, "LeaveBalance.exact"),
    ],
)
def test_invalid_balance_is_rejected(kwargs: dict[str, object], field: str) -> None:
    """An unknown bucket, an implausible year, a negative or non-decimal amount."""
    values: dict[str, object] = {
        "bucket": "ferie",
        "year": 2026,
        "accrued_twelfths": Decimal(0),
        "taken_twelfths": Decimal(0),
        **kwargs,
    }
    with pytest.raises(InvalidInputError) as caught:
        LeaveBalance(**values)  # type: ignore[arg-type]
    assert caught.value.field == field


def test_bucket_is_parsed_from_its_value() -> None:
    """A bucket given by its value becomes the member."""
    balance = LeaveBalance("rol", 2026, Decimal(0), Decimal(0))  # type: ignore[arg-type]

    assert balance.bucket is LeaveBucket.ROL


@pytest.mark.parametrize(
    "balances",
    [
        (_ferie(2026, 1), _ferie(2026, 2)),
        (_ferie(2027, 1), _ferie(2026, 2)),
        (LeaveBalance(LeaveBucket.ROL, 2026, Decimal(0), Decimal(0)), _ferie(2026, 1)),
    ],
)
def test_account_rejects_repeated_or_unordered_balances(
    balances: tuple[LeaveBalance, ...],
) -> None:
    """One balance per bucket and year, in bucket then year order."""
    with pytest.raises(InvalidInputError, match="one per bucket and year"):
        LeaveAccount(balances)


def test_account_rejects_a_non_bool_known() -> None:
    """``known`` is a bool."""
    with pytest.raises(InvalidInputError):
        LeaveAccount(known=None)  # type: ignore[arg-type]


def test_credit_adds_twelfths_and_keeps_the_worst_exactness() -> None:
    """A month credited inexactly leaves the balance inexact."""
    account = (
        LeaveAccount()
        .credited(_FERIE, 2026, Decimal(26), exact=True)
        .credited(_FERIE, 2026, Decimal(26), exact=False)
    )

    (balance,) = account.balances
    assert (balance.accrued_twelfths, balance.exact) == (Decimal(52), False)


def test_leave_is_taken_from_the_oldest_residual_first() -> None:
    """30 days in 2027: 26 from 2026 and 4 from 2027, which is overdrawn."""
    account = LeaveAccount((_ferie(2026, 312), _ferie(2027, 26)))

    taken = account.taken(_FERIE, 2027, Decimal(30))

    assert [(b.year, b.taken, b.residual) for b in taken.balances] == [
        (2026, Decimal(26), Decimal(0)),
        (2027, Decimal(4), Decimal(26) / 12 - 4),
    ]


def test_leave_taken_skips_balances_without_residual_or_later() -> None:
    """A spent year and a later year are not drawn from."""
    account = LeaveAccount((_ferie(2025, 12, 12), _ferie(2026, 0), _ferie(2027, 24)))

    taken = account.taken(_FERIE, 2026, Decimal(1))

    assert [b.taken for b in taken.balances] == [Decimal(1), Decimal(1), Decimal(0)]


def test_leave_covered_by_an_older_year_leaves_the_current_one() -> None:
    """One day in 2027 taken whole from the 2026 residual."""
    account = LeaveAccount((_ferie(2026, 312),)).taken(_FERIE, 2027, Decimal(1))

    assert [(b.year, b.taken) for b in account.balances] == [(2026, Decimal(1))]


def test_settlement_closes_every_balance() -> None:
    """After the settlement nothing is left and no leave can be taken."""
    account = LeaveAccount((_ferie(2026, 260, 120),)).settled()

    assert account.unsettled() == ()
    with pytest.raises(InvalidInputError, match="paid at the end of the employment"):
        account.taken(_FERIE, 2026, Decimal(1))


def test_empty_balance_of_an_unknown_year() -> None:
    """A bucket and year without a record is an empty balance."""
    assert LeaveAccount().balance(LeaveBucket.ROL, 2026) == LeaveBalance(
        LeaveBucket.ROL, 2026, Decimal(0), Decimal(0)
    )
