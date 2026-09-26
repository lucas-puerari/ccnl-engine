"""Exact regression tests for bugs verified in REVIEW.md §4.

All bugs are currently present on main.  Tests marked xfail(strict=True)
document the correct expected behaviour and become XPASS once fixed.
Tests without xfail assert behaviour that must already pass (the bug is
already reproducible as an accepted-input failure).

Bugs covered:
  - Regular December and tredicesima produce identical gross and ledger IDs.
  - Annual ledger (13 runs) has duplicate entry IDs (60 unique out of 65).
  - OvertimeEvent with negative hours accepted without error.
  - SickLeaveEvent with negative amount accepted without error.
  - SickLeaveEvent with negative waiting_period_days accepted without error.
  - WelfareEvent with negative amount accepted without error.
  - FringeEvent with negative amount accepted without error.
  - BilateralFundEvent with negative employee_amount accepted without error.
  - NightShiftEvent with negative supplement_amount accepted without error.
  - HolidayWorkEvent with negative supplement_amount accepted without error.
  - WorkCalendar.from_additional_months with unsupported count silently accepts.

Source: REVIEW.md §4 (riproduzione numerica verificata), §5 P0-7.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from tests.helpers import year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
# igiene-ambientale D1 has EDR and INDEMN_INT allowances with months_per_year=12,
# so they are included in regular monthly runs but excluded from the tredicesima.
_CCNL_WITH_ALLOWANCES = "igiene-ambientale-utilitalia.json"
_LEVEL_WITH_ALLOWANCES = "D1"


# ---------------------------------------------------------------------------
# Run identity: regular December vs tredicesima
# ---------------------------------------------------------------------------


def test_regular_december_and_tredicesima_have_different_gross() -> None:
    """Regular December run and tredicesima must produce different period_gross.

    Uses igiene-ambientale D1 which carries EDR and INDEMN_INT allowances
    with months_per_year=12.  Those allowances are included in the regular
    December run but excluded from the tredicesima (months_per_year < 13).

    Uses calculate_period directly (not calculate_year) because the D1 salary
    table starts 2026-02-01, so January would raise a gap error in calculate_year.
    """
    pid = PeriodId(year=2026, month=12)
    state = PeriodState(
        ytd=TaxYearState(regular_periods_closed=11, tax_withholding_periods_closed=11)
    )
    regular = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=pid,
            payment_date=date(2026, 12, 28),
            ccnl_slug=_CCNL_WITH_ALLOWANCES,
            level_code=_LEVEL_WITH_ALLOWANCES,
            opening_state=state,
        )
    )
    thirteenth = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=pid,
            payment_date=date(2026, 12, 28),
            ccnl_slug=_CCNL_WITH_ALLOWANCES,
            level_code=_LEVEL_WITH_ALLOWANCES,
            opening_state=state,
            run=PayrollRun.thirteenth(2026, 12),
        )
    )
    regular_gross = regular.period_gross
    extra_gross = thirteenth.period_gross
    assert regular_gross != extra_gross, (
        f"Regular December gross ({regular_gross}) must differ from tredicesima "
        f"gross ({extra_gross}); they are identical, allowance filtering not applied."
    )
    # Tredicesima must be smaller than regular December (no EDR or INDEMN_INT).
    assert extra_gross < regular_gross, (
        f"Tredicesima ({extra_gross}) must be less than "
        f"regular December ({regular_gross})"
    )


def test_regular_december_and_tredicesima_have_distinct_ledger_ids() -> None:
    """Ledger entry IDs must be unique across all runs in a year.

    Source: REVIEW.md §4.  With 13 runs the year produces 65 entries, but only
    60 distinct IDs because the two December runs share entry IDs.
    """
    result = calculate_year(year_input(_YEAR, _CCNL, _LEVEL))

    all_ids = [e.entry_id for r in result.period_results for e in r.ledger_entries]
    unique_ids = set(all_ids)

    assert len(all_ids) == len(unique_ids), (
        f"All {len(all_ids)} ledger entry IDs must be unique; "
        f"found only {len(unique_ids)} distinct IDs."
    )


# ---------------------------------------------------------------------------
# Negative events accepted without error
# ---------------------------------------------------------------------------


def test_overtime_negative_hours_raises() -> None:
    """OvertimeEvent with negative hours must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        OvertimeEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(-2),
            hourly_rate=Decimal("15.00"),
        )


def test_overtime_negative_rate_raises() -> None:
    """OvertimeEvent with negative hourly_rate must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        OvertimeEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(2),
            hourly_rate=Decimal("-15.00"),
        )


def test_sick_leave_negative_amount_raises() -> None:
    """SickLeaveEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        SickLeaveEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
            sick_days=3,
        )


def test_sick_leave_negative_waiting_period_raises() -> None:
    """SickLeaveEvent with negative waiting_period_days must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        SickLeaveEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("500.00"),
            sick_days=3,
            waiting_period_days=-1,
        )


def test_night_shift_negative_supplement_raises() -> None:
    """NightShiftEvent with negative supplement_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("-100.00"),
        )


def test_holiday_work_negative_supplement_raises() -> None:
    """HolidayWorkEvent with negative supplement_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        HolidayWorkEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("-100.00"),
        )


def test_welfare_negative_amount_raises() -> None:
    """WelfareEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        WelfareEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
        )


def test_fringe_negative_amount_raises() -> None:
    """FringeEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        FringeEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
        )


def test_bilateral_fund_negative_employee_amount_raises() -> None:
    """BilateralFundEvent with negative employee_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        BilateralFundEvent(
            event_date=date(_YEAR, 1, 15),
            employee_amount=Decimal("-100.00"),
            employer_amount=Decimal("100.00"),
        )


def test_bilateral_fund_negative_employer_amount_raises() -> None:
    """BilateralFundEvent with negative employer_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        BilateralFundEvent(
            event_date=date(_YEAR, 1, 15),
            employee_amount=Decimal("100.00"),
            employer_amount=Decimal("-100.00"),
        )


def test_overtime_zero_multiplier_raises() -> None:
    """OvertimeEvent with multiplier=0 must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        OvertimeEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(2),
            hourly_rate=Decimal("15.00"),
            multiplier=Decimal(0),
        )


def test_absence_negative_hourly_rate_raises() -> None:
    """AbsenceEvent with negative hourly_rate must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        AbsenceEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(8),
            hourly_rate=Decimal("-12.00"),
        )


def test_absence_end_date_before_event_date_raises() -> None:
    """AbsenceEvent with end_date < event_date must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        AbsenceEvent(
            event_date=date(_YEAR, 1, 20),
            hours=Decimal(8),
            hourly_rate=Decimal("12.00"),
            end_date=date(_YEAR, 1, 15),
        )


def test_arrears_negative_amount_raises() -> None:
    """ArrearsEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        ArrearsEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-500.00"),
            separate_tax_rate=Decimal("0.23"),
        )


def test_arrears_tax_rate_above_one_raises() -> None:
    """ArrearsEvent with separate_tax_rate > 1 must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        ArrearsEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("500.00"),
            separate_tax_rate=Decimal("1.5"),
        )


def test_termination_tfr_negative_amount_raises() -> None:
    """TerminationTFREvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        TerminationTFREvent(
            event_date=date(_YEAR, 12, 31),
            amount=Decimal("-1000.00"),
            separate_tax_rate=Decimal("0.23"),
        )


def test_termination_tfr_negative_tax_rate_raises() -> None:
    """TerminationTFREvent with negative separate_tax_rate raises InvalidInputError."""
    with pytest.raises(InvalidInputError):
        TerminationTFREvent(
            event_date=date(_YEAR, 12, 31),
            amount=Decimal("1000.00"),
            separate_tax_rate=Decimal("-0.5"),
        )


# ---------------------------------------------------------------------------
# WorkCalendar.from_additional_months with unsupported count
# ---------------------------------------------------------------------------


def test_from_additional_months_unsupported_count_raises_explicitly() -> None:
    """from_additional_months(2026, 16) must raise ValueError explicitly."""
    with pytest.raises(ValueError, match="additional_months"):
        WorkCalendar.from_additional_months(2026, 16)
