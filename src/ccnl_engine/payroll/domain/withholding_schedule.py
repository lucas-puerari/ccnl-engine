"""Withholding schedule of a tax year: the payments it holds and the conguaglio.

The IRPEF projection and the year-end conguaglio (art. 23 c. 3 DPR
600/1973) run on the payments of the tax year: the tax still due is spread
over the payments not yet made, and the payment after which none is left
settles the balance on the final taxable income.  A tax year counts the
payments made in it, whatever their competence (TUIR art. 51 c. 1): a
December paid after 12 January takes a slot of the next tax year.

Positions are read by identity, never by count: a slot is paid when the
tax cash state holds a payment of its run, and the conguaglio is the
payment that leaves no other slot of the schedule unpaid.  The order in
which the payments are computed therefore does not move the conguaglio,
and a payment made after the conguaglio (a late payment the schedule did
not plan) settles the year again on the new totals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import PayrollRunCount
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping

    from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind

__all__ = ["WithholdingPosition", "WithholdingSchedule", "WithholdingSlot"]

_ONE = Decimal(1)
_FEATURE = "withholding_schedule"


@dataclass(frozen=True)
class WithholdingSlot:
    """One IRPEF withholding slot: a payment and the share of pay it carries.

    Attributes:
        payment: The payment that takes the slot: its run and date.
        pay_fraction: Share of one regular monthly pay the run carries at full
            accrual: ``1`` for a regular month or a full extra month, the
            contractual fraction for a partial one (``0.5`` for half a
            quattordicesima).  Used to project the recurring pay of future
            slots; never to count them.
    """

    payment: PaymentId
    pay_fraction: Decimal = field(default_factory=lambda: _ONE)

    def __post_init__(self) -> None:  # noqa: D105
        if not self.payment.run_id.kind.consumes_withholding_slot:
            msg = f"run {self.payment.run_id} does not consume a withholding slot"
            raise ValueError(msg)
        if not Decimal(0) < self.pay_fraction <= _ONE:
            msg = f"pay_fraction must be in (0, 1]; got {self.pay_fraction}"
            raise ValueError(msg)

    @property
    def run(self) -> PayrollRun:
        """The run the slot pays."""
        return PayrollRun.of(self.payment.run_id)


@dataclass(frozen=True)
class WithholdingPosition:
    """Where one payment stands in the withholding schedule of its tax year.

    Attributes:
        slots: Number of slots of the schedule.
        remaining: Slots not yet paid, the current payment's included; at
            least 1.  The tax still due is divided by it.
        upcoming: Slots still to pay after the current payment, in plan
            order.
        settles: Whether the payment settles the conguaglio: it takes a slot
            and leaves no other slot of the schedule unpaid.
    """

    slots: int
    remaining: int
    upcoming: tuple[WithholdingSlot, ...]
    settles: bool


@dataclass(frozen=True)
class WithholdingSchedule:
    """Withholding slots of a tax year: one per payment that takes a slot.

    Every payment but an adjustment run takes a slot; the number of slots
    has no maximum.  The slots are in plan order, normally the order of the
    payment dates; the last slot is the planned conguaglio.

    Attributes:
        year: The tax year.
        slots: Slots of the tax year, at least one, each of a different run
            and of a payment of tax year :attr:`year`.

    Raises:
        InvalidInputError: When there is no slot, two slots pay the same
            run, or a payment belongs to another tax year.
    """

    year: int
    slots: tuple[WithholdingSlot, ...]

    def __post_init__(self) -> None:  # noqa: D105
        if not self.slots:
            msg = "a withholding schedule needs at least one payment"
            raise InvalidInputError(msg, feature=_FEATURE)
        seen: set[tuple[int, int, RunKind, int]] = set()
        for slot in self.slots:
            payment = slot.payment
            if payment.run_id.payment_key in seen:
                msg = f"run '{payment.run_id}' is paid twice in the schedule"
                raise InvalidInputError(msg, feature=_FEATURE)
            seen.add(payment.run_id.payment_key)
            if payment.tax_year != self.year:
                msg = (
                    f"payment '{payment}' belongs to tax year {payment.tax_year}, "
                    f"not to the withholding schedule of {self.year}"
                )
                raise InvalidInputError(msg, feature=_FEATURE)

    @classmethod
    def of_payments(
        cls,
        year: int,
        payments: Iterable[PaymentId],
        fractions: Mapping[str, Decimal],
    ) -> WithholdingSchedule:
        """Build the schedule of the payments of a tax year.

        Args:
            year: The tax year.
            payments: Payments of the tax year in plan order; those that
                take no slot (adjustment runs) are left out.
            fractions: ``max_fraction`` of each extra-month run kind, by
                run kind value; a run kind not in it carries ``1``.

        Returns:
            One slot per payment that takes one.
        """
        return cls(
            year=year,
            slots=tuple(
                WithholdingSlot(p, fractions.get(p.run_id.kind.value, _ONE))
                for p in payments
                if p.run_id.kind.consumes_withholding_slot
            ),
        )

    @property
    def run_count(self) -> PayrollRunCount:
        """Number of payments holding a withholding slot."""
        return PayrollRunCount(len(self.slots))

    @property
    def conguaglio(self) -> PaymentId:
        """The planned conguaglio: the payment of the last slot."""
        return self.slots[-1].payment

    def position(
        self, payment: PaymentId, paid: Collection[PayrollRunId]
    ) -> WithholdingPosition:
        """Return where ``payment`` stands, given the runs already paid.

        A payment that takes a slot leaves unpaid the slots of the other
        runs not in ``paid`` (an extra month matched by kind and year,
        whatever its month): it settles the conguaglio when there is none.
        An adjustment run takes no slot: it stands before the first unpaid
        slot and never settles the conguaglio.

        Args:
            payment: The payment being computed.
            paid: Runs already paid in the tax year.

        Returns:
            The position of ``payment``.
        """
        settled = {r.payment_key for r in paid} | {payment.run_id.payment_key}
        unpaid = tuple(
            s for s in self.slots if s.payment.run_id.payment_key not in settled
        )
        if payment.run_id.kind.consumes_withholding_slot:
            return WithholdingPosition(
                slots=len(self.slots),
                remaining=1 + len(unpaid),
                upcoming=unpaid,
                settles=not unpaid,
            )
        return WithholdingPosition(
            slots=len(self.slots),
            remaining=max(1, len(unpaid)),
            upcoming=unpaid[1:],
            settles=False,
        )
