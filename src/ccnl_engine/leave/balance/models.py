"""Balances of paid leave carried across runs and years.

Each bucket of leave (:class:`~ccnl_engine.leave.types.LeaveBucket`) has one
:class:`LeaveBalance` per year of accrual: the days or hours accrued, taken
and paid.  Both are kept in twelfths (the accrual is the yearly entitlement
of each month credited, summed) so that ten months of 26 days are exactly
260 twelfths, not ten roundings of 26/12, and a residual moved from one
year to another stays exact: the residual is divided by twelve and rounded
only when it is paid.  The :class:`LeaveAccount` of the employment
lives in the competence state
(:class:`~ccnl_engine.balance.competence.models.EmploymentAccrualState`),
carried unchanged across tax years.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import final

from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.validators import (
    parse_enum,
    require_bool,
    require_decimal,
    require_int,
)

__all__ = ["LeaveAccount", "LeaveBalance"]

_FEATURE = "leave"
_ZERO = Decimal(0)
_TWELVE = Decimal(12)
_ORDER = {bucket: index for index, bucket in enumerate(LeaveBucket)}


@final
@dataclass(frozen=True)
class LeaveBalance:
    """Leave of one bucket accrued in one year: accrued, taken and paid.

    Attributes:
        bucket: The bucket of leave.
        year: Calendar year the leave accrued in.
        accrued_twelfths: Twelve times the days or hours accrued: the
            yearly entitlement of each month credited, summed.
        taken_twelfths: Twelve times the days or hours taken against the
            balance.
        settled: Whether the residual was paid (at the end of the
            employment): a settled balance has no residual left.
        exact: Whether every month credited was computed from known facts
            and sourced rules; ``False`` when a month rests on an estimate
            (a month fraction the CCNL text does not rule on, an unknown
            seniority or hire date, an absence whose effect on the accrual
            is not stated).

    Raises:
        InvalidInputError: When a field is not of its type, the year is not
            plausible or an amount is negative.
    """

    bucket: LeaveBucket
    year: int
    accrued_twelfths: Decimal
    taken_twelfths: Decimal
    settled: bool = False
    exact: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        bucket = parse_enum(
            self.bucket, LeaveBucket, "LeaveBalance.bucket", feature=_FEATURE
        )
        object.__setattr__(self, "bucket", bucket)
        require_int(
            self.year, "LeaveBalance.year", feature=_FEATURE, minimum=1900, maximum=2999
        )
        for name in ("accrued_twelfths", "taken_twelfths"):
            require_decimal(
                getattr(self, name),
                f"LeaveBalance.{name}",
                feature=_FEATURE,
                minimum=_ZERO,
            )
        require_bool(self.settled, "LeaveBalance.settled", feature=_FEATURE)
        require_bool(self.exact, "LeaveBalance.exact", feature=_FEATURE)

    @property
    def accrued(self) -> Decimal:
        """Days or hours accrued: :attr:`accrued_twelfths` over twelve."""
        return self.accrued_twelfths / _TWELVE

    @property
    def taken(self) -> Decimal:
        """Days or hours taken: :attr:`taken_twelfths` over twelve."""
        return self.taken_twelfths / _TWELVE

    @property
    def residual_twelfths(self) -> Decimal:
        """Twelve times the residual, zero once settled; negative when overdrawn."""
        if self.settled:
            return _ZERO
        return self.accrued_twelfths - self.taken_twelfths

    @property
    def residual(self) -> Decimal:
        """Days or hours left: accrued less taken, zero once paid."""
        return self.residual_twelfths / _TWELVE

    @property
    def paid(self) -> Decimal:
        """Days or hours paid at the settlement, zero before it."""
        if not self.settled:
            return _ZERO
        return (self.accrued_twelfths - self.taken_twelfths) / _TWELVE


@final
@dataclass(frozen=True)
class LeaveAccount:
    """Leave balances of an employment, one per bucket and year of accrual.

    Attributes:
        balances: The balances, in bucket order then year order, at most
            one per bucket and year.
        known: Whether the balances hold every day and hour of leave of the
            employment: ``False`` for balances imported without the leave
            of the previous provider, which leaves the residual paid at the
            end of the employment unknown.

    Raises:
        InvalidInputError: When a balance is not a :class:`LeaveBalance`,
            two share a bucket and a year, or they are out of order.
    """

    balances: tuple[LeaveBalance, ...] = ()
    known: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        path = "LeaveAccount.balances"
        balances = tuple_of(
            self.balances,
            path,
            items_of_type(LeaveBalance, feature=_FEATURE),
            feature=_FEATURE,
        )
        keys = [_key(b) for b in balances]
        if keys != sorted(set(keys)):
            msg = (
                "leave balances must be one per bucket and year, in bucket then "
                "year order"
            )
            raise InvalidInputError(msg, field=path, feature=_FEATURE)
        object.__setattr__(self, "balances", balances)
        require_bool(self.known, "LeaveAccount.known", feature=_FEATURE)

    def balance(self, bucket: LeaveBucket, year: int) -> LeaveBalance:
        """Return the balance of ``bucket`` accrued in ``year``.

        Returns:
            The balance, empty when none is recorded.
        """
        return next(
            (b for b in self.balances if b.bucket is bucket and b.year == year),
            LeaveBalance(bucket, year, _ZERO, _ZERO),
        )

    def with_balances(self, *changed: LeaveBalance) -> LeaveAccount:
        """Return the account with ``changed`` in place of their bucket and year.

        Returns:
            A new account, its balances in order.
        """
        replaced = {_key(b): b for b in (*self.balances, *changed)}
        return replace(self, balances=tuple(replaced[k] for k in sorted(replaced)))

    def credited(
        self, bucket: LeaveBucket, year: int, twelfths: Decimal, *, exact: bool
    ) -> LeaveAccount:
        """Return the account with ``twelfths`` accrued on ``bucket`` in ``year``.

        Returns:
            A new account; the balance turns inexact with an inexact month.
        """
        current = self.balance(bucket, year)
        return self.with_balances(
            replace(
                current,
                accrued_twelfths=current.accrued_twelfths + twelfths,
                exact=current.exact and exact,
            )
        )

    def taken(self, bucket: LeaveBucket, year: int, quantity: Decimal) -> LeaveAccount:
        """Return the account with ``quantity`` of ``bucket`` taken in ``year``.

        The leave is taken from the oldest balance with a residual first,
        up to it; what is left is taken from the balance of ``year``, which
        is overdrawn when it holds less (leave granted in advance).

        Returns:
            A new account.

        Raises:
            InvalidInputError: When every balance of ``bucket`` was settled
                at the end of the employment: no leave is taken after it.
        """
        own = [b for b in self.balances if b.bucket is bucket]
        if own and all(b.settled for b in own):
            msg = f"the {bucket} leave was paid at the end of the employment"
            raise InvalidInputError(msg, field="LeaveTakenEvent", feature=_FEATURE)
        left = quantity * _TWELVE
        changed: list[LeaveBalance] = []
        for item in own:
            room = item.residual_twelfths
            if item.year >= year or left <= _ZERO or room <= _ZERO:
                continue
            used = min(room, left)
            changed.append(replace(item, taken_twelfths=item.taken_twelfths + used))
            left -= used
        account = self.with_balances(*changed)
        if left > _ZERO:
            current = account.balance(bucket, year)
            account = account.with_balances(
                replace(current, taken_twelfths=current.taken_twelfths + left)
            )
        return account

    def settled(self) -> LeaveAccount:
        """Return the account with every balance settled.

        Returns:
            A new account whose balances have no residual left.
        """
        return self.with_balances(*(replace(b, settled=True) for b in self.balances))

    def unsettled(self) -> tuple[LeaveBalance, ...]:
        """Return the balances not yet settled.

        Returns:
            The balances whose residual is still due, in order.
        """
        return tuple(b for b in self.balances if not b.settled)


def _key(balance: LeaveBalance) -> tuple[int, int]:
    return (_ORDER[balance.bucket], balance.year)
