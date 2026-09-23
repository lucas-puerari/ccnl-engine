"""Regression suite for correctness bugs identified in REVIEW.md §3-5.

All tests are marked xfail(strict=True): they document the correct expected
behaviour and will become XPASS once the underlying bug is fixed.  That XPASS
causes CI to fail, prompting removal of the marker and confirming the fix.

Bugs covered (REVIEW.md §5):
  - bonus duplicated across extra month run
  - taxable_ytd diluted by additional_months divisor
  - domestic-work contributions silently zero
  - bilateral-fund employee amount added to inps_employee_ytd
  - AbsenceEvent(hours=240) accepted and produces negative gross
  - negative BonusEvent accepted without domain error
  - SickLeaveEvent(sick_days=0) raises ZeroDivisionError not InvalidInputError
  - waiting_period_days > sick_days accepted without domain error
  - addizionale 1% applied above the IVS massimale ceiling

Sources:
  INPS circ. 4/2026: massimale IVS 122,295 EUR; soglia +1% 56,224 EUR
  REVIEW.md §5: P0-1, P0-2, P0-4, P0-5, P0-6, P0-7
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BilateralFundEvent,
    BonusEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
    ccnl: str = _CCNL,
    level: str = _LEVEL,
) -> PeriodCalculationRequest:
    if opening is None:
        opening = PeriodState.zero()
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        opening_state=opening,
        events=events,  # type: ignore[arg-type]
    )


def _calendar_13() -> WorkCalendar:
    return WorkCalendar(
        year=_YEAR,
        extra_months=(
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=12,
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Bonus duplicated across extra month run
#
# calculate_year maps period_events by month number.  When December has two
# runs (regular + tredicesima), both receive period_events[12].  A 100 EUR
# bonus therefore inflates annual_gross by 200 instead of 100.
# Source: REVIEW.md §5, P0-1.
# ---------------------------------------------------------------------------


def test_bonus_not_duplicated_in_extra_run() -> None:
    """A December BonusEvent must increase annual_gross by exactly 100, not 200.

    Source: REVIEW.md §5, P0-1.  With a 13-run calendar and period_events[12]
    containing a 100 EUR bonus, annual_gross must equal baseline + 100.
    Expected: diff == Decimal("100.00").
    """
    calendar = _calendar_13()
    bonus = BonusEvent(event_date=date(_YEAR, 12, 15), amount=Decimal("100.00"))

    result_base = calculate_year(_YEAR, _CCNL, _LEVEL, calendar=calendar)
    result_with = calculate_year(
        _YEAR,
        _CCNL,
        _LEVEL,
        calendar=calendar,
        period_events={12: (bonus,)},
    )

    diff = result_with.annual_gross - result_base.annual_gross
    assert diff == Decimal("100.00"), (
        f"annual_gross delta from a 100 EUR December bonus must be 100.00; "
        f"got {diff}.  Bonus is currently applied to both the regular and "
        "tredicesima runs in December "
        "(calculate_year.py: events=effective_events.get(run.month, ()))."
    )


# ---------------------------------------------------------------------------
# taxable_ytd diluted by additional_months divisor
#
# _compute_amounts() sets period_taxable = taxable / additional_months and
# increments closing.taxable_ytd by that fraction.  A 1,000 EUR bonus whose
# INPS-net taxable is ~905.10 EUR therefore adds only ~69.62 EUR (905.10/13)
# to taxable_ytd instead of the full ~905.10.
# Source: REVIEW.md §5, P0-2.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "taxable_ytd inflated by double-INPS-deduction (REVIEW.md §4 P0-3): "
        "the event INPS is subtracted twice, giving 810.20 instead of 905.10.  "
        "Fix: deduct INPS once when building event_taxable."
    ),
)
def test_taxable_ytd_not_diluted_by_extra_months() -> None:
    """closing_state.taxable_ytd must increase by exactly 905.10 for a 1,000 EUR bonus.

    Source: REVIEW.md §4 (riproduzione numerica verificata).
    1,000 EUR bonus, employee INPS contribution 94.90 EUR (9.49%):
    event_taxable = 1,000.00 - 94.90 = 905.10.
    The current engine produces 810.20 due to a double-deduction of INPS
    inside event_taxable + actual_total_inps.
    """
    bonus = BonusEvent(event_date=date(_YEAR, 1, 15), amount=Decimal("1000.00"))

    result_base = calculate_period(_req(month=1))
    result_with = calculate_period(_req(month=1, events=(bonus,)))

    ytd_diff = (
        result_with.closing_state.taxable_ytd - result_base.closing_state.taxable_ytd
    )
    assert ytd_diff == Decimal("905.10"), (
        f"taxable_ytd increase from a 1,000 EUR bonus must be exactly 905.10 "
        f"(gross 1000 minus INPS 94.90); got {ytd_diff}."
    )


# ---------------------------------------------------------------------------
# Domestic-work contributions silently zero
#
# calculate_period routes domestic CCNLs through a zero-contribution path
# (PR #601 fix).  The result has period_gross > 0 but contribution_breakdown
# employee == employer == 0.  This is a silent incorrect result.
# Source: REVIEW.md §5, P0-4.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Domestic CCNL is routed through the zero-contribution path; "
        "contribution_breakdown.employee and .employer are both 0 instead of "
        "the correct per-hour flat contributions."
    ),
)
def test_domestic_contributions_nonzero() -> None:
    """Lavoro domestico must produce employee and employer INPS contributions > 0.

    Source: REVIEW.md §5, P0-4.  Expected: contribution_breakdown.employee > 0
    and contribution_breakdown.employer > 0.
    """
    result = calculate_period(
        _req(month=6, ccnl="lavoro-domestico-convivente.json", level="BS")
    )

    assert result.contribution_breakdown.employee > _ZERO, (
        f"Domestic worker employee contributions must be > 0; "
        f"got {result.contribution_breakdown.employee}.  "
        "Engine routes domestic CCNL through zero-contribution path."
    )
    assert result.contribution_breakdown.employer > _ZERO, (
        f"Domestic worker employer contributions must be > 0; "
        f"got {result.contribution_breakdown.employer}."
    )


# ---------------------------------------------------------------------------
# Bilateral-fund employee amount added to inps_employee_ytd
#
# BilateralFundEvent is posted to EMPLOYEE_CONTRIBUTIONS, which is also the
# account whose running total drives inps_employee_ytd.  The fund contribution
# is not an INPS amount and must not affect the INPS YTD counter.
# Source: REVIEW.md §5, P0-5.
# ---------------------------------------------------------------------------


def test_bilateral_fund_excluded_from_inps_employee_ytd() -> None:
    """BilateralFundEvent must not change inps_employee_ytd.

    Source: REVIEW.md §5, P0-5.  A 100 EUR bilateral fund contribution must not
    alter closing_state.inps_employee_ytd relative to the no-fund baseline.
    """
    fund = BilateralFundEvent(
        event_date=date(_YEAR, 1, 15),
        employee_amount=Decimal("100.00"),
        employer_amount=Decimal("100.00"),
    )

    result_base = calculate_period(_req(month=1))
    result_with = calculate_period(_req(month=1, events=(fund,)))

    base_ytd = result_base.closing_state.inps_employee_ytd
    with_ytd = result_with.closing_state.inps_employee_ytd
    assert with_ytd == base_ytd, (
        f"inps_employee_ytd with bilateral fund ({with_ytd}) must equal "
        f"baseline ({base_ytd}).  Fund employee amount currently posted to "
        "EMPLOYEE_CONTRIBUTIONS and counted toward inps_employee_ytd."
    )


# ---------------------------------------------------------------------------
# AbsenceEvent(hours=240) accepted and produces negative gross
#
# _check_event_date validates 0 < hours <= 240, so 240 passes the guard.
# A monthly period has at most ~184 working hours; 240 absent hours at a
# realistic rate exceeds the monthly gross and makes period_gross negative.
# Source: REVIEW.md §5, P0-6.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "AbsenceEvent(hours=240) passes the 0 < hours <= 240 guard but a "
        "full-time worker has only ~168-184 working hours per month; the deduction "
        "exceeds the monthly gross and period_gross becomes negative."
    ),
)
def test_absence_240h_does_not_produce_negative_gross() -> None:
    """AbsenceEvent(hours=240) must not result in a negative period_gross.

    Source: REVIEW.md §5, P0-6.  240 hours at 12.50 EUR/h = 3,000 EUR deduction
    against a monthly gross of ~1,500-2,500 EUR produces a negative result.
    Expected: period_gross >= 0.
    """
    absence = AbsenceEvent(
        event_date=date(_YEAR, 1, 15),
        hours=Decimal(240),
        hourly_rate=Decimal("12.50"),
    )
    result = calculate_period(_req(events=(absence,)))

    assert result.period_gross >= _ZERO, (
        f"period_gross with 240h absence must not be negative; "
        f"got {result.period_gross}.  The engine accepts 240h (= upper guard "
        "limit) even when that exceeds the period's working hours."
    )


# ---------------------------------------------------------------------------
# Negative BonusEvent accepted without domain error
#
# BonusEvent carries no invariants; a negative amount reduces the gross
# silently and can propagate to negative taxable income.
# Source: REVIEW.md §5, P0-6.
# ---------------------------------------------------------------------------


def test_negative_bonus_raises_invalid_input() -> None:
    """BonusEvent with a negative amount must raise InvalidInputError.

    Source: REVIEW.md §5, P0-6.  A -100 EUR bonus reduces gross and taxable
    income without any explicit deduction record.  Expected: InvalidInputError.
    """
    with pytest.raises(InvalidInputError):
        BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("-100.00"),
        )


# ---------------------------------------------------------------------------
# SickLeaveEvent(sick_days=0) raises ZeroDivisionError
#
# The carenza formula is amount - (amount / sick_days * waiting_period_days).
# When sick_days=0 this produces a bare ZeroDivisionError instead of a
# structured InvalidInputError.
# Source: REVIEW.md §5, P0-6, P0-7.
# ---------------------------------------------------------------------------


def test_sick_leave_zero_days_raises_invalid_input() -> None:
    """SickLeaveEvent with sick_days=0 must raise InvalidInputError.

    Source: REVIEW.md §5, P0-6/P0-7.  sick_days=0 is semantically invalid;
    the engine must reject it with a structured error before the formula runs.
    """
    with pytest.raises(InvalidInputError):
        SickLeaveEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("500.00"),
            sick_days=0,
            waiting_period_days=1,
        )


# ---------------------------------------------------------------------------
# waiting_period_days > sick_days not validated
#
# The docstring declares waiting_period_days must not exceed sick_days, but
# no runtime check enforces this.  The formula produces a nonsensical result
# (net < 0 when carenza > total).
# Source: REVIEW.md §5, P0-7.
# ---------------------------------------------------------------------------


def test_waiting_period_exceeds_sick_days_raises_invalid_input() -> None:
    """SickLeaveEvent with waiting_period_days > sick_days must raise InvalidInputError.

    Source: REVIEW.md §5, P0-7.  The docstring states this is invalid; the
    engine must enforce it with a structured domain error.
    """
    with pytest.raises(InvalidInputError):
        SickLeaveEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("500.00"),
            sick_days=2,
            waiting_period_days=3,
        )


# ---------------------------------------------------------------------------
# Addizionale 1% applied above the IVS massimale ceiling
#
# The +1% addizionale threshold (56,224 EUR) and the IVS massimale (122,295 EUR)
# are distinct limits.  When the YTD INPS base already exceeds the massimale,
# no IVS and no +1% should apply to the current period income.  The engine
# currently computes the +1% on the full period base regardless of whether
# the massimale has been reached.
# Source: REVIEW.md §5, P0-5; INPS circ. 4/2026.
# ---------------------------------------------------------------------------


def test_addizionale_zero_above_ivs_massimale() -> None:
    """addizionale_1pct must be 0 when inps_base_ytd exceeds the IVS massimale.

    Source: INPS circ. 4/2026.  massimale IVS 2026 = 122,295 EUR.  With
    inps_base_ytd=130,000 > 122,295, the period adds income above the ceiling
    where no INPS component (including the +1% addizionale) should apply.
    Expected: addizionale_1pct == 0.
    """
    opening = PeriodState(
        months_closed=11,
        inps_base_ytd=Decimal("130000.00"),  # > 122,295 IVS massimale 2026
    )
    result = calculate_period(_req(month=12, opening=opening))

    addizionale = next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct"
        ),
        _ZERO,
    )
    assert addizionale == _ZERO, (
        f"addizionale_1pct must be 0 when inps_base_ytd ({opening.inps_base_ytd}) "
        f"exceeds the IVS massimale (122,295 EUR, INPS circ. 4/2026); "
        f"got {addizionale}.  The +1% is currently not gated on the massimale."
    )
