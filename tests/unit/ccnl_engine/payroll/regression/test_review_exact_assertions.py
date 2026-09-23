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
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import ExtraMonthSchedule, WorkCalendar
from ccnl_engine.payroll.domain.events import (
    BilateralFundEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


def _calendar_13() -> WorkCalendar:
    return WorkCalendar(
        year=_YEAR,
        extra_months=(ExtraMonthSchedule(name="tredicesima", payment_month=12),),
    )


# ---------------------------------------------------------------------------
# Run identity: regular December vs tredicesima
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REVIEW.md §4: regular December and tredicesima produce identical gross "
        "(2,211.43) because calculate_year passes the same PeriodId(2026, 12) to "
        "both runs and the compensation model ignores run_kind.  "
        "Fix: RunCompensationPolicy must select components by kind."
    ),
)
def test_regular_december_and_tredicesima_have_different_gross() -> None:
    """Regular December run and tredicesima must produce different period_gross.

    Source: REVIEW.md §4.  Both currently produce 2,211.43.
    The tredicesima gross must reflect accrued ratei, not a copy of the
    regular monthly compensation.
    """
    result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=_calendar_13())
    dec_results = [r for r in result.period_results if r.period_id.month == 12]

    assert len(dec_results) == 2, (
        f"Expected 2 December runs (regular + tredicesima); got {len(dec_results)}"
    )
    regular_gross = dec_results[0].period_gross
    extra_gross = dec_results[1].period_gross
    assert regular_gross != extra_gross, (
        f"Regular December gross ({regular_gross}) must differ from tredicesima "
        f"gross ({extra_gross}); both are identical."
    )


def test_regular_december_and_tredicesima_have_distinct_ledger_ids() -> None:
    """Ledger entry IDs must be unique across all runs in a year.

    Source: REVIEW.md §4.  With 13 runs the year produces 65 entries, but only
    60 distinct IDs because the two December runs share entry IDs.
    """
    result = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=_calendar_13())

    all_ids = [e.entry_id for r in result.period_results for e in r.ledger_entries]
    unique_ids = set(all_ids)

    assert len(all_ids) == len(unique_ids), (
        f"All {len(all_ids)} ledger entry IDs must be unique; "
        f"found only {len(unique_ids)} distinct IDs."
    )


# ---------------------------------------------------------------------------
# Negative events accepted without error
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: OvertimeEvent does not validate hours or hourly_rate.",
)
def test_overtime_negative_hours_raises() -> None:
    """OvertimeEvent with negative hours must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        OvertimeEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(-2),
            hourly_rate=Decimal("15.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: OvertimeEvent does not validate hourly_rate.",
)
def test_overtime_negative_rate_raises() -> None:
    """OvertimeEvent with negative hourly_rate must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        OvertimeEvent(
            event_date=date(_YEAR, 1, 15),
            hours=Decimal(2),
            hourly_rate=Decimal("-15.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: SickLeaveEvent does not validate amount sign.",
)
def test_sick_leave_negative_amount_raises() -> None:
    """SickLeaveEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        SickLeaveEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
            sick_days=3,
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REVIEW.md §5 P0-7: SickLeaveEvent does not validate waiting_period_days < 0."
    ),
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


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: NightShiftEvent does not validate supplement_amount.",
)
def test_night_shift_negative_supplement_raises() -> None:
    """NightShiftEvent with negative supplement_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("-100.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: HolidayWorkEvent does not validate supplement_amount.",
)
def test_holiday_work_negative_supplement_raises() -> None:
    """HolidayWorkEvent with negative supplement_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        HolidayWorkEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("-100.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: WelfareEvent does not validate amount sign.",
)
def test_welfare_negative_amount_raises() -> None:
    """WelfareEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        WelfareEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason="REVIEW.md §5 P0-7: FringeEvent does not validate amount sign.",
)
def test_fringe_negative_amount_raises() -> None:
    """FringeEvent with negative amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        FringeEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REVIEW.md §5 P0-7: BilateralFundEvent does not validate employee_amount sign."
    ),
)
def test_bilateral_fund_negative_employee_amount_raises() -> None:
    """BilateralFundEvent with negative employee_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        BilateralFundEvent(
            event_date=date(_YEAR, 1, 15),
            employee_amount=Decimal("-100.00"),
            employer_amount=Decimal("100.00"),
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REVIEW.md §5 P0-7: BilateralFundEvent does not validate employer_amount sign."
    ),
)
def test_bilateral_fund_negative_employer_amount_raises() -> None:
    """BilateralFundEvent with negative employer_amount must raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        BilateralFundEvent(
            event_date=date(_YEAR, 1, 15),
            employee_amount=Decimal("100.00"),
            employer_amount=Decimal("-100.00"),
        )


# ---------------------------------------------------------------------------
# WorkCalendar.from_additional_months with unsupported count
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REVIEW.md §4: WorkCalendar.from_additional_months(2026, 16) fails "
        "indirectly (ValueError: duplicate name 'quindicesima') instead of "
        "raising an explicit error for an unsupported additional_months value.  "
        "Fix: validate additional_months <= 14 before building schedules."
    ),
)
def test_from_additional_months_unsupported_count_raises_explicitly() -> None:
    """from_additional_months(2026, 16) must raise ValueError explicitly.

    Source: REVIEW.md §4.  Currently fails with a duplicate-name ValueError
    deep inside WorkCalendar.__post_init__ rather than a clear domain error.
    """
    with pytest.raises(ValueError, match="additional_months"):
        WorkCalendar.from_additional_months(2026, 16)
