"""P0 blocker counterexamples: xfail tests that must fail until the bugs are fixed.

Each test is marked ``xfail(strict=True)``: it MUST fail with the current engine.
When the underlying bug is fixed the mark must be removed and the expected value
must be verified against the normative source.

P0-1a: quattordicesima accrual uses ``regular_periods_closed/12`` instead of the
        entitlement window, so a full-year worker receives 50% of the quattordicesima
        when it is paid at month 6.
P0-1b: ``calculate_year`` with ``calendar=None`` converts ``additional_months=13.5``
        to ``int(13)``, suppressing the half-quattordicesima (CCNL Cooperative Sociali).
P0-2:  Six ``EmploymentFacts`` fields (seniority_months, roles, category,
        full_time_weekly_hours, started_on, ended_on) are not forwarded to
        ``PeriodCalculationRequest``; all variation is silently discarded.
P0-3:  Trattamento integrativo recovery does not hold a fixed installment plan;
        each period recomputes the residual and divides again, producing geometrically
        decreasing deductions instead of eight equal installments.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmploymentFacts,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    PayrollYearRequest,
)
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.period import PeriodState

_engine = PayrollEngine.bundled()

# ---------------------------------------------------------------------------
# P0-1a — quattordicesima accrual ratio wrong when paid at month 6
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1a: accrual uses regular_periods_closed/12=0.5 for June quattordicesima "
        "instead of 6/6=1.0 (full entitlement window Jan-Jun)"
    ),
)
def test_p0_1a_quattordicesima_full_at_june() -> None:
    """Commercio level 4: June quattordicesima must equal the monthly gross.

    For a worker employed for the full accrual window (January through June), the
    June quattordicesima should represent 100% of the extra month, not 50%.
    The expected value is 1783.75 EUR (the regular monthly gross at level 4).
    """
    calendar = WorkCalendar(
        year=2026,
        extra_months=(
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH, name="tredicesima", payment_month=12
            ),
            ExtraMonthSchedule(
                kind=ExtraMonthKind.FOURTEENTH,
                name="quattordicesima",
                payment_month=6,
            ),
        ),
    )
    result = _engine.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            calendar=calendar,
            employment_facts=EmploymentFacts(num_employees=50),
        )
    )
    fourteenth = next(
        r
        for r in result.period_results
        if r.run is not None and r.run.run_kind == "fourteenth"
    )
    assert fourteenth.period_gross == Decimal("1783.75"), (
        f"Expected 1783.75 (full quattordicesima), got {fourteenth.period_gross}"
    )


# ---------------------------------------------------------------------------
# P0-1b — additional_months=13.5 truncated to int(13) by calculate_year
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-1b: calculate_year converts additional_months=13.5 to int(13), "
        "suppressing the half-quattordicesima; annual gross is 22461.79 not 23325.71"
    ),
)
def test_p0_1b_cooperative_sociali_13_5_months() -> None:
    """Cooperative Sociali D2: annual_gross must equal 1727.83 * 13.5 = 23325.71.

    The CCNL declares additional_months=13.5.  The internal calculate_year call
    with calendar=None converts this to int(13), dropping the half-quattordicesima
    and producing 22461.79 (= 1727.83 * 13) instead.
    """
    result = calculate_year(
        2026,
        "cooperative-sociali.json",
        "D2",
        num_employees=50,
    )
    assert result.annual_gross == Decimal("23325.71"), (
        f"Expected 23325.71 (13.5 months), got {result.annual_gross}"
    )


# ---------------------------------------------------------------------------
# P0-2 — EmploymentFacts fields silently dropped by facade
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-2: seniority_months, roles, category, full_time_weekly_hours, "
        "started_on and ended_on are not forwarded to PeriodCalculationRequest; "
        "all variation is silently discarded"
    ),
)
def test_p0_2_seniority_months_has_effect() -> None:
    """Metalmeccanico C3: 60 months seniority must produce a higher gross than zero.

    The EmploymentFacts API accepts seniority_months but the facade never copies
    it into PeriodCalculationRequest.  Both calls currently return 2158.26.
    """
    run = PayrollRun.regular(year=2026, month=1)
    payment = date(2026, 1, 28)
    base = _engine.calculate(
        PayrollRequest(
            run=run,
            payment_date=payment,
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(num_employees=50),
        )
    )
    with_seniority = _engine.calculate(
        PayrollRequest(
            run=run,
            payment_date=payment,
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(
                num_employees=50,
                seniority_months=60,
                roles=frozenset({"caposquadra"}),
                category="operaio",
                weekly_hours=20,
                full_time_weekly_hours=40,
            ),
        )
    )
    assert with_seniority.period_gross != base.period_gross, (
        f"Expected seniority to change gross (base={base.period_gross}), "
        f"but both returned {with_seniority.period_gross}"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-2: weekly_hours=20 / full_time_weekly_hours=40 must halve the gross; "
        "facade drops full_time_weekly_hours so part-time ratio is never applied"
    ),
)
def test_p0_2_part_time_half_gross() -> None:
    """Metalmeccanico C3: 50% part-time must produce half the full-time gross."""
    run = PayrollRun.regular(year=2026, month=1)
    payment = date(2026, 1, 28)
    full_time = _engine.calculate(
        PayrollRequest(
            run=run,
            payment_date=payment,
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(num_employees=50),
        )
    )
    part_time = _engine.calculate(
        PayrollRequest(
            run=run,
            payment_date=payment,
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(
                num_employees=50,
                weekly_hours=20,
                full_time_weekly_hours=40,
            ),
        )
    )
    expected = full_time.period_gross * Decimal("0.5")
    assert part_time.period_gross == expected, (
        f"Expected 50% part-time gross={expected}, got {part_time.period_gross}"
    )


# ---------------------------------------------------------------------------
# P0-3 — Trattamento integrativo recovery installments decrease geometrically
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P0-3: recovery plan recomputes residual/8 each period instead of "
        "holding a fixed installment; second installment is -98.44 instead of -112.50"
    ),
)
def test_p0_3_recovery_installments_are_equal() -> None:
    """Eight recovery periods must each deduct the same 112.50 EUR installment.

    Starting state: credit_recognized_ytd=900 (worker received 900 EUR of
    trattamento integrativo that must be recovered in 8 equal installments of
    112.50 EUR each, per D.L. 3/2020 art. 1 co. 3).

    The current engine recomputes residual/8 each period, producing a decreasing
    geometric sequence: -112.50, -98.44, -86.13, ... instead of eight equal
    installments of -112.50.
    """
    state = PeriodState(
        regular_periods_closed=1,
        tax_withholding_periods_closed=1,
        credit_recognized_ytd=Decimal(900),
        credit_recovered_ytd=Decimal(0),
    )
    installments: list[Decimal] = []
    for month in range(2, 10):
        result = _engine.calculate(
            PayrollRequest(
                run=PayrollRun.regular(year=2026, month=month),
                payment_date=date(2026, month, 28),
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                employment_facts=EmploymentFacts(num_employees=50),
                opening_state=state,
            )
        )
        installments.append(result.tax_computation.trattamento_integrativo)
        state = result.closing_state

    expected_installment = Decimal("-112.50")
    for i, inst in enumerate(installments, start=1):
        assert inst == expected_installment, (
            f"Installment {i}: expected {expected_installment}, got {inst}; "
            f"all installments: {installments}"
        )
    assert sum(installments) == Decimal(-900), (
        f"Total recovery must be -900; got {sum(installments)}"
    )
