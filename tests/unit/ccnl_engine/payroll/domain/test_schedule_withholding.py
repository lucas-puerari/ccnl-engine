"""Unit tests for extra-month entitlement, run count and withholding schedule."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.extra_month_entitlement import ExtraMonthEntitlement
from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.schedule import (
    PayrollRunCount,
    PayrollSchedule,
    WithholdingSchedule,
    WithholdingSlot,
)
from ccnl_engine.payroll.service.tax_computation import compute_tax
from tests.helpers import make_year_rules

_YEAR = 2026
_FRACTIONAL = st.decimals(
    min_value=Decimal("13.01"),
    max_value=Decimal("13.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)


class TestExtraMonthEntitlement:
    """ExtraMonthEntitlement keeps equivalent months as a validated Decimal."""

    def test_of_preserves_fraction(self) -> None:
        """of() converts through str and keeps the fractional part."""
        assert ExtraMonthEntitlement.of(Decimal("13.5")).value == Decimal("13.5")
        assert ExtraMonthEntitlement.of(14).value == Decimal(14)

    def test_non_decimal_rejected(self) -> None:
        """A float value is rejected instead of being coerced."""
        with pytest.raises(TypeError, match="Decimal"):
            ExtraMonthEntitlement(13.5)  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", ["11.99", "NaN", "-Infinity"])
    def test_below_twelve_or_not_finite_rejected(self, value: str) -> None:
        """Below 12, or not a finite number, raises ValueError."""
        with pytest.raises(ValueError, match="minimum"):
            ExtraMonthEntitlement(Decimal(value))

    def test_above_fourteen_rejected(self) -> None:
        """Above 14 raises ValueError."""
        with pytest.raises(ValueError, match="maximum"):
            ExtraMonthEntitlement(Decimal("14.01"))


class TestCalendarEntitlement:
    """WorkCalendar exposes and accepts the entitlement."""

    def test_calendar_entitlement_sums_fractions(self) -> None:
        """Tredicesima plus half quattordicesima gives 13.5."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        assert cal.entitlement == ExtraMonthEntitlement(Decimal("13.5"))

    def test_from_additional_months_accepts_entitlement(self) -> None:
        """The factory accepts an ExtraMonthEntitlement directly."""
        cal = WorkCalendar.from_additional_months(
            _YEAR, ExtraMonthEntitlement(Decimal(14))
        )
        assert [s.kind for s in cal.extra_months] == [
            ExtraMonthKind.THIRTEENTH,
            ExtraMonthKind.FOURTEENTH,
        ]

    def test_partial_tredicesima_rejected(self) -> None:
        """A value between 12 and 13 is rejected, not silently dropped."""
        with pytest.raises(ValueError, match="partial tredicesima"):
            WorkCalendar.from_additional_months(_YEAR, Decimal("12.5"))


class TestPayrollRunCount:
    """PayrollRunCount is a positive int."""

    @pytest.mark.parametrize("value", [True, Decimal(14)])
    def test_non_int_rejected(self, value: object) -> None:
        """A bool or a Decimal is not a run count."""
        with pytest.raises(TypeError, match="int"):
            PayrollRunCount(value)  # type: ignore[arg-type]

    def test_zero_rejected(self) -> None:
        """At least one run."""
        with pytest.raises(ValueError, match=">= 1"):
            PayrollRunCount(0)

    def test_schedule_run_count(self) -> None:
        """PayrollSchedule reports its number of runs."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        assert PayrollSchedule.from_calendar(cal).run_count == PayrollRunCount(14)


class TestWithholdingSlot:
    """A slot belongs to a run that consumes withholding."""

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
            WithholdingSlot(run)

    @pytest.mark.parametrize("fraction", ["0", "1.01"])
    def test_pay_fraction_out_of_range_rejected(self, fraction: str) -> None:
        """pay_fraction must be in (0, 1]."""
        with pytest.raises(ValueError, match="pay_fraction"):
            WithholdingSlot(PayrollRun.regular(_YEAR, 1), Decimal(fraction))


class TestWithholdingSchedule:
    """WithholdingSchedule: one slot per payslip, in payment order."""

    def test_empty_rejected(self) -> None:
        """A schedule needs at least one slot."""
        with pytest.raises(ValueError, match="at least one slot"):
            WithholdingSchedule(year=_YEAR, slots=())

    def test_run_of_other_year_rejected(self) -> None:
        """Every slot run must belong to the schedule year."""
        slot = WithholdingSlot(PayrollRun.regular(_YEAR + 1, 1))
        with pytest.raises(ValueError, match="belongs to year"):
            WithholdingSchedule(year=_YEAR, slots=(slot,))

    def test_half_fourteenth_keeps_its_slot(self) -> None:
        """13.5 months: 14 slots, the June quattordicesima carrying 0.5."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        schedule = WithholdingSchedule.from_calendar(cal)
        assert schedule.run_count == PayrollRunCount(14)
        fourteenth = schedule.slots[6]
        assert fourteenth.run == PayrollRun.fourteenth(_YEAR, 6)
        assert fourteenth.pay_fraction == Decimal("0.5")
        assert schedule.slots[-1].run == PayrollRun.thirteenth(_YEAR, 12)
        assert schedule.slots[-1].pay_fraction == Decimal(1)

    def test_remaining_and_upcoming(self) -> None:
        """Remaining slots include the current one; upcoming ones exclude it."""
        schedule = WithholdingSchedule.from_calendar(WorkCalendar(year=_YEAR))
        assert schedule.remaining(0) == 12
        assert schedule.remaining(11) == 1
        assert schedule.remaining(12) == 1
        assert len(schedule.upcoming(0)) == 11
        assert schedule.upcoming(11) == ()


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
    schedule = WithholdingSchedule.from_calendar(cal)
    runs = PayrollSchedule.from_calendar(cal).runs

    assert schedule.run_count == PayrollRunCount(14)
    assert tuple(s.run for s in schedule.slots) == runs
    assert cal.entitlement.value == entitlement
    fractions = {s.run.run_kind: s.pay_fraction for s in schedule.slots}
    assert fractions[RunKind.FOURTEENTH] == entitlement - 13

    rules = make_year_rules()
    taxable = Decimal(25000)
    last = compute_tax(
        taxable, rules, withholding_schedule=schedule, slots_closed=13
    ).computation
    before_last = compute_tax(
        taxable, rules, withholding_schedule=schedule, slots_closed=12
    ).computation
    assert last.ordinary_tax == last.withholding_due
    assert before_last.ordinary_tax < before_last.withholding_due
