"""Regression tests for P0-1 — extra-month rateo uses payment month, not accrual.

All tests are marked xfail(strict=True): they document the normatively correct
behaviour.  When PR fix/accrual-window-extra-month fixes the underlying algorithm
the tests turn XPASS, causing CI to fail and prompting removal of these markers.

Bug (REVIEW.md §3, P0-1):
  _apply_extra_month_policy() computes:

      rateo = Decimal(period_month) / Decimal(12)

  period_month is the calendar month in which the run is paid.  WorkCalendar
  schedules the quattordicesima in June by default, so a full-year employee
  automatically receives 6/12 of the entitlement instead of 12/12.

  The correct model: the rateo must derive from the accrual window (months of
  service during the reference period), not from the payment calendar date.

Acceptance criteria (REVIEW.md §3, P0-1):
  1. Changing only the payment month must not change the already-accrued gross.
  2. A full-year employee must receive 12/12 regardless of payment month.
  3. A six-month employee must receive 6/12 regardless of payment month.
  4. The Commercio level-4 full-year quattordicesima must not produce 891.88.

Sources:
  INPS circ. 154/2014: tredicesima matura nell'anno solare in costanza di rapporto.
  CCNL lavoro domestico art. 38: rateo pari ai mesi di servizio nella finestra.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun

_CCNL_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_LEVEL_C3 = "C3"
_CCNL_COMMERCIO = "commercio-confcommercio.json"
_LEVEL_4 = "4"
_YEAR = 2026


def _extra_month_req(
    ccnl: str,
    level: str,
    payment_month: int,
    run: PayrollRun,
    regular_periods_closed: int = 12,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=payment_month),
        payment_date=date(_YEAR, payment_month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        opening_state=PeriodState(
            regular_periods_closed=regular_periods_closed,
            tax_withholding_periods_closed=regular_periods_closed,
        ),
        run=run,
    )


# ---------------------------------------------------------------------------
# Acceptance criterion 1: payment month must not change accrued gross
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1: _apply_extra_month_policy uses period_month/12 so June "
        "tredicesima is half of December tredicesima for a full-year employee."
    ),
)
def test_full_year_tredicesima_same_gross_june_vs_december() -> None:
    """A full-year employee's tredicesima gross must be equal in June and December.

    Source: INPS circ. 154/2014 — tredicesima matura in costanza di rapporto.
    Payment month is irrelevant when the full accrual window has elapsed.
    Current buggy output: June 1105.72, December 2211.43.
    """
    gross_june = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
        )
    ).period_gross
    gross_december = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=12,
            run=PayrollRun.thirteenth(_YEAR, 12),
        )
    ).period_gross
    assert gross_june == gross_december, (
        f"Full-year tredicesima must not depend on payment month; "
        f"got June={gross_june}, December={gross_december}.  "
        "Fix: derive rateo from accrual window, not period_month."
    )


# ---------------------------------------------------------------------------
# Acceptance criterion 2: full-year employee receives 12/12
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1: June tredicesima is computed as 6/12 of monthly gross, "
        "not 12/12 as required for a full-year employee."
    ),
)
def test_full_year_tredicesima_equals_monthly_gross() -> None:
    """A full-year tredicesima must equal one regular monthly gross.

    Source: INPS circ. 154/2014.  The tredicesima rateo for an employee active
    for the full accrual window must be 12/12 = 1.0.
    Current buggy output when paid in June: 1105.72 (6/12 of 2211.43).
    """
    thirteenth_gross = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
        )
    ).period_gross

    regular_gross = calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=1),
            payment_date=date(_YEAR, 1, 28),
            ccnl_slug=_CCNL_METALMECCANICO,
            level_code=_LEVEL_C3,
            opening_state=PeriodState.zero(),
        )
    ).period_gross

    assert thirteenth_gross >= regular_gross * Decimal("0.99"), (
        f"Full-year tredicesima (≥ 12/12) must be ≈ one month's gross "
        f"({regular_gross}); got {thirteenth_gross}."
    )


# ---------------------------------------------------------------------------
# Acceptance criterion 3: six-month employee must receive 6/12 regardless of
# payment month
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1: rateo from payment month means June payment always gives 6/12 "
        "and December always gives 12/12, even for the same 6-month employee."
    ),
)
def test_six_month_employee_same_rateo_june_vs_december() -> None:
    """A six-month employee must get the same rateo whether paid in June or December.

    Source: CCNL lavoro domestico art. 38 — rateo pari ai mesi di servizio.
    Current behaviour: June payment => 6/12, December payment => 12/12,
    even when both employees have the same 6 months of service.
    """
    gross_june = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=6,
            run=PayrollRun.thirteenth(_YEAR, 6),
            regular_periods_closed=6,
        )
    ).period_gross
    gross_december = calculate_period(
        _extra_month_req(
            _CCNL_METALMECCANICO,
            _LEVEL_C3,
            payment_month=12,
            run=PayrollRun.thirteenth(_YEAR, 12),
            regular_periods_closed=6,
        )
    ).period_gross
    assert gross_june == gross_december, (
        f"Six-month employee's tredicesima must not depend on payment month; "
        f"got June={gross_june}, December={gross_december}."
    )


# ---------------------------------------------------------------------------
# Acceptance criterion 4: Commercio level-4 full-year quattordicesima
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1: Commercio level-4 quattordicesima paid in June produces 891.88 "
        "(6/12 of full entitlement) instead of the full accrued amount."
    ),
)
def test_commercio_level4_quatordicesima_full_year_not_half() -> None:
    """Commercio level-4 full-year quattordicesima in June must not be 891.88.

    Counterexample from REVIEW.md §2: the June run produces 891.88 against
    ~1818 for December, because period_month=6 triggers rateo 6/12.
    A full-year employee must receive the full entitlement.
    """
    gross_june = calculate_period(
        _extra_month_req(
            _CCNL_COMMERCIO,
            _LEVEL_4,
            payment_month=6,
            run=PayrollRun.fourteenth(_YEAR, 6),
        )
    ).period_gross
    gross_december = calculate_period(
        _extra_month_req(
            _CCNL_COMMERCIO,
            _LEVEL_4,
            payment_month=12,
            run=PayrollRun.fourteenth(_YEAR, 12),
        )
    ).period_gross
    assert gross_june == gross_december, (
        f"Full-year quattordicesima must be equal for June and December payment; "
        f"got June={gross_june} (≈891.88 buggy), December={gross_december}."
    )
