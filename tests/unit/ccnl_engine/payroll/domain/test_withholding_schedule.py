"""The withholding schedule of a tax year: slots by payment, conguaglio by identity."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId, RunKind
from ccnl_engine.payroll.domain.schedule import PayrollRunCount, PayrollSchedule
from ccnl_engine.payroll.domain.withholding_schedule import (
    WithholdingSchedule,
    WithholdingSlot,
)
from ccnl_engine.payroll.service.tax_computation import compute_tax
from tests.fixtures.withholding import calendar_schedule, paid_on_day
from tests.helpers import make_year_rules

_YEAR = 2026
_FRACTIONAL = st.decimals(
    min_value=Decimal("13.01"),
    max_value=Decimal("13.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
_LATE_DECEMBER = PaymentId(PayrollRunId.parse("2025-12-regular"), date(2026, 1, 13))


def _ids(*texts: str) -> frozenset[PayrollRunId]:
    return frozenset(PayrollRunId.parse(t) for t in texts)


class TestWithholdingSlot:
    """A slot belongs to a payment that consumes withholding."""

    def test_run_kind_slot_rule(self) -> None:
        """Only an adjustment run does not consume a slot."""
        assert not RunKind.ADJUSTMENT.consumes_withholding_slot
        assert all(
            k.consumes_withholding_slot for k in RunKind if k is not RunKind.ADJUSTMENT
        )

    def test_adjustment_run_rejected(self) -> None:
        """An adjustment run cannot hold a slot."""
        run = PayrollRun(run_kind=RunKind.ADJUSTMENT, month=12, year=_YEAR)
        with pytest.raises(ValueError, match="does not consume"):
            WithholdingSlot(paid_on_day(run))

    @pytest.mark.parametrize("fraction", ["0", "1.01"])
    def test_pay_fraction_out_of_range_rejected(self, fraction: str) -> None:
        """pay_fraction must be in (0, 1]."""
        with pytest.raises(ValueError, match="pay_fraction"):
            WithholdingSlot(
                paid_on_day(PayrollRun.regular(_YEAR, 1)), Decimal(fraction)
            )

    def test_run_of_the_slot(self) -> None:
        """The slot names the run its payment settles."""
        slot = WithholdingSlot(_LATE_DECEMBER)
        assert slot.run == PayrollRun.regular(_YEAR - 1, 12)


class TestWithholdingSchedule:
    """One slot per payment of the tax year, whatever its competence."""

    def test_empty_rejected(self) -> None:
        """A schedule needs at least one payment."""
        with pytest.raises(InvalidInputError, match="at least one payment"):
            WithholdingSchedule(year=_YEAR, slots=())

    def test_payment_of_another_tax_year_rejected(self) -> None:
        """December 2025 paid on 13 January 2026 is not a payment of 2025."""
        with pytest.raises(InvalidInputError, match="belongs to tax year 2026"):
            WithholdingSchedule(
                year=_YEAR - 1, slots=(WithholdingSlot(_LATE_DECEMBER),)
            )

    def test_run_paid_twice_rejected(self) -> None:
        """A run is paid once."""
        slot = WithholdingSlot(paid_on_day(PayrollRun.regular(_YEAR, 1)))
        with pytest.raises(InvalidInputError, match="paid twice"):
            WithholdingSchedule(year=_YEAR, slots=(slot, slot))

    def test_adjustment_payments_take_no_slot(self) -> None:
        """of_payments leaves out the payments that take no slot."""
        adjustment = paid_on_day(PayrollRun(RunKind.ADJUSTMENT, 3, _YEAR))
        january = paid_on_day(PayrollRun.regular(_YEAR, 1))
        schedule = WithholdingSchedule.of_payments(_YEAR, (january, adjustment), {})
        assert schedule.run_count == PayrollRunCount(1)
        assert schedule.conguaglio == january

    def test_late_december_takes_the_first_slot(self) -> None:
        """A late December of the previous year is a payment of the year."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal(14))
        schedule = calendar_schedule(cal, before=(_LATE_DECEMBER,))
        assert schedule.run_count == PayrollRunCount(15)
        assert schedule.slots[0].payment == _LATE_DECEMBER
        assert schedule.conguaglio.run_id == PayrollRunId.parse("2026-12-thirteenth")

    def test_half_fourteenth_keeps_its_slot(self) -> None:
        """13.5 months: 14 slots, the June quattordicesima carrying 0.5."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        schedule = calendar_schedule(cal)
        fourteenth = schedule.slots[6]
        assert fourteenth.run == PayrollRun.fourteenth(_YEAR, 6)
        assert fourteenth.pay_fraction == Decimal("0.5")
        assert schedule.slots[-1].pay_fraction == Decimal(1)


class TestPosition:
    """Positions are read from the runs paid, never from a count."""

    _SCHEDULE = calendar_schedule(WorkCalendar(year=_YEAR))

    def test_first_payment_leaves_the_others_unpaid(self) -> None:
        """January: twelve slots remain, eleven come after it."""
        position = self._SCHEDULE.position(self._SCHEDULE.slots[0].payment, ())
        assert (position.slots, position.remaining) == (12, 12)
        assert len(position.upcoming) == 11
        assert not position.settles

    def test_last_unpaid_payment_settles_whatever_its_place(self) -> None:
        """March paid last, after the rest of the year, settles the conguaglio."""
        march = self._SCHEDULE.slots[2].payment
        paid = frozenset(s.payment.run_id for s in self._SCHEDULE.slots) - {
            march.run_id
        }
        position = self._SCHEDULE.position(march, paid)
        assert (position.remaining, position.upcoming, position.settles) == (
            1,
            (),
            True,
        )

    def test_a_payment_outside_the_schedule_settles_when_nothing_is_left(
        self,
    ) -> None:
        """A late payment after the conguaglio settles the year again."""
        paid = frozenset(s.payment.run_id for s in self._SCHEDULE.slots)
        assert self._SCHEDULE.position(_LATE_DECEMBER, paid).settles

    def test_adjustment_stands_before_the_first_unpaid_slot(self) -> None:
        """An adjustment run takes no slot and never settles."""
        adjustment = paid_on_day(PayrollRun(RunKind.ADJUSTMENT, 3, _YEAR))
        position = self._SCHEDULE.position(
            adjustment, _ids("2026-01-regular", "2026-02-regular")
        )
        assert (position.remaining, len(position.upcoming)) == (10, 9)
        assert not position.settles
        everything = frozenset(s.payment.run_id for s in self._SCHEDULE.slots)
        last = self._SCHEDULE.position(adjustment, everything)
        assert (last.remaining, last.settles) == (1, False)


@given(entitlement=_FRACTIONAL)
def test_fractional_entitlement_does_not_truncate_withholding_slots(
    entitlement: Decimal,
) -> None:
    """A fractional entitlement does not truncate withholding slots.

    For any entitlement strictly between 13 and 14 the year issues 14
    payslips, the withholding schedule has one slot per payslip, the
    fraction survives on the last extra month, and the conguaglio settles
    the whole balance only on the fourteenth slot.
    """
    cal = WorkCalendar.from_additional_months(_YEAR, entitlement)
    schedule = calendar_schedule(cal)
    runs = PayrollSchedule.from_calendar(cal).runs

    assert schedule.run_count == PayrollRunCount(14)
    assert tuple(s.run for s in schedule.slots) == runs
    fractions = {s.run.run_kind: s.pay_fraction for s in schedule.slots}
    assert fractions[RunKind.FOURTEENTH] == entitlement - 13

    rules = make_year_rules()
    taxable = Decimal(25000)
    paid = frozenset(s.payment.run_id for s in schedule.slots[:13])
    last = schedule.position(schedule.slots[13].payment, paid)
    before = schedule.position(schedule.slots[12].payment, paid - {runs[12].identifier})
    on_last = compute_tax(taxable, rules, remaining_slots=last.remaining).computation
    on_before = compute_tax(
        taxable, rules, remaining_slots=before.remaining
    ).computation
    assert on_last.ordinary_tax == on_last.withholding_due
    assert on_before.ordinary_tax < on_before.withholding_due
