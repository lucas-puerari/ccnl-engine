"""Oracle cases of one regular period: INPS, IRPEF, TFR and period events.

Each case is verified against the computation chain; expected values are frozen
and must NOT be auto-updated from the engine.  A failing assertion means a
computation-affecting change was made without reviewing these oracle cases.

Source for values: hand-traced payroll computation chains and CCNL source data.
All monetary amounts in EUR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import FringeEvent, SickLeaveEvent
from ccnl_engine.inputs import (
    ContributableHours,
    FixedTerm,
    WeeklyHours,
)
from tests.fixtures.seniority import new_hire

engine = PayrollEngine.bundled()
_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=new_hire(),
)


# ---------------------------------------------------------------------------
# Baseline: INPS contributions (area: INPS)
# ---------------------------------------------------------------------------


def test_inps_contributions_metalmeccanico_c3() -> None:
    """Employee and employer INPS for metalmeccanico C3, January 2026."""
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    assert result.period_gross == Decimal("2158.26")
    assert result.contribution_breakdown.employee == Decimal("204.81")
    assert result.contribution_breakdown.employer == Decimal("658.27")


# ---------------------------------------------------------------------------
# IRPEF bracket tax (area: IRPEF)
# ---------------------------------------------------------------------------


def test_irpef_ordinary_tax_metalmeccanico_c3() -> None:
    """Ordinary IRPEF for metalmeccanico C3; 2026 bracket: 23% up to 28,000 EUR."""
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    tc = result.tax_computation
    assert tc.ordinary_tax == Decimal("202.10")
    assert result.period_net == Decimal("1751.35")


# ---------------------------------------------------------------------------
# TFR accrual (area: TFR)
# ---------------------------------------------------------------------------


def test_tfr_accrual_metalmeccanico_c3() -> None:
    """TFR accrual = gross / 13.5 per Art. 2120 c.c."""
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    tfr = next(i for i in result.pay_items if i.kind == "tfr_accrual_item")
    assert tfr.amount == Decimal("159.87")


# ---------------------------------------------------------------------------
# Domestico flat-rate INPS (area: domestico)
# ---------------------------------------------------------------------------


def test_domestic_inps_non_convivente() -> None:
    """Flat per-hour INPS contributions for domestic non-convivente worker, level B."""
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="lavoro-domestico-non-convivente.json",
                level_code="B",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(25),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(108))),
        )
    )
    assert result.period_gross == Decimal("1212.73")
    assert result.contribution_breakdown.employee == Decimal("33.48")
    assert result.contribution_breakdown.employer == Decimal("100.44")


# ---------------------------------------------------------------------------
# Fringe benefits within annual threshold (area: fringe)
# ---------------------------------------------------------------------------


def test_fringe_below_threshold_no_tax() -> None:
    """Fringe benefit within the 2026 annual threshold (1,000 EUR) is not taxed."""
    result_base = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    result_fringe = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(
                events=(FringeEvent(event_date=date(2026, 3, 1), amount=Decimal(100)),)
            ),
        )
    )
    assert result_fringe.period_net == result_base.period_net


# ---------------------------------------------------------------------------
# Malattia with sick leave integration (area: malattia)
# ---------------------------------------------------------------------------


def test_sickness_full_integration_metalmeccanico() -> None:
    """Metalmeccanico provides 100% sick pay; net is unchanged by a 5-day illness."""
    result_base = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    result_sick = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(
                events=(
                    SickLeaveEvent(
                        event_date=date(2026, 3, 10),
                        amount=Decimal(0),
                        sick_days=5,
                        waiting_period_days=0,
                    ),
                )
            ),
        )
    )
    assert result_sick.period_net == result_base.period_net
    assert result_sick.unpaid_absence_deduction == Decimal(0)


# ---------------------------------------------------------------------------
# NASpI addizionale on fixed-term contracts (area: regimi 2026)
# ---------------------------------------------------------------------------


def test_naspi_addizionale_fixed_term() -> None:
    """Fixed-term contract incurs NASpI addizionale; employer cost exceeds permanent."""
    result_permanent = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    result_fixed = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
                contract_type=FixedTerm(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    assert result_fixed.period_employer_cost > result_permanent.period_employer_cost
