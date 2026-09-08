"""Unit tests for compute_absence_deduction service function."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.ccnl import AbsenceRules, DailyDivisorMethod
from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays
from ccnl_engine.engine.payroll.service.absence import compute_absence_deduction

_ZERO = Decimal(0)
_GROSS_MONTHLY = Decimal("2000.00")
_HOURLY_RATE = Decimal("11.56")  # ~2000/173


class TestComputeAbsenceDeductionBy26:
    """compute_absence_deduction with by_26 divisor method."""

    def test_zero_days_returns_zero(self) -> None:
        """Zero unpaid days → zero deduction (early return path)."""
        rules = AbsenceRules(daily_divisor_method=DailyDivisorMethod.BY_26)
        result = compute_absence_deduction(
            absence_input=AbsenceDays(unpaid_days=_ZERO),
            absence_rules=rules,
            gross_monthly=_GROSS_MONTHLY,
            hourly_rate=_HOURLY_RATE,
        )
        assert result == _ZERO

    def test_one_day_by_26(self) -> None:
        """One absent day: deduction = round(gross_monthly / 26)."""
        rules = AbsenceRules(daily_divisor_method=DailyDivisorMethod.BY_26)
        result = compute_absence_deduction(
            absence_input=AbsenceDays(unpaid_days=Decimal(1)),
            absence_rules=rules,
            gross_monthly=_GROSS_MONTHLY,
            hourly_rate=_HOURLY_RATE,
        )
        # 2000 / 26 = 76.923... → 76.92
        assert result == Decimal("76.92")

    def test_multiple_days_by_26(self) -> None:
        """Three absent days: deduction = round(gross/26) * 3."""
        rules = AbsenceRules(daily_divisor_method=DailyDivisorMethod.BY_26)
        result = compute_absence_deduction(
            absence_input=AbsenceDays(unpaid_days=Decimal(3)),
            absence_rules=rules,
            gross_monthly=_GROSS_MONTHLY,
            hourly_rate=_HOURLY_RATE,
        )
        # 76.92 * 3 = 230.76
        assert result == Decimal("230.76")


class TestComputeAbsenceDeductionByHourly:
    """compute_absence_deduction with by_hourly divisor method."""

    def test_one_day_by_hourly(self) -> None:
        """One absent day: deduction = round(hourly_rate * daily_hours)."""
        rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_HOURLY,
            daily_hours=Decimal(8),
        )
        result = compute_absence_deduction(
            absence_input=AbsenceDays(unpaid_days=Decimal(1)),
            absence_rules=rules,
            gross_monthly=_GROSS_MONTHLY,
            hourly_rate=_HOURLY_RATE,
        )
        # 11.56 * 8 = 92.48
        assert result == Decimal("92.48")

    def test_daily_hours_none_raises(self) -> None:
        """by_hourly with daily_hours=None raises ValueError."""
        rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_HOURLY,
            daily_hours=None,
        )
        with pytest.raises(ValueError, match="daily_hours is required"):
            compute_absence_deduction(
                absence_input=AbsenceDays(unpaid_days=Decimal(1)),
                absence_rules=rules,
                gross_monthly=_GROSS_MONTHLY,
                hourly_rate=_HOURLY_RATE,
            )

    def test_daily_hours_zero_raises(self) -> None:
        """by_hourly with daily_hours=0 raises ValueError."""
        rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_HOURLY,
            daily_hours=_ZERO,
        )
        with pytest.raises(ValueError, match="daily_hours must be > 0"):
            compute_absence_deduction(
                absence_input=AbsenceDays(unpaid_days=Decimal(1)),
                absence_rules=rules,
                gross_monthly=_GROSS_MONTHLY,
                hourly_rate=_HOURLY_RATE,
            )
