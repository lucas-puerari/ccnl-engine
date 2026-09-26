"""Oracle test cases with hardcoded expected values for P0/P1 regression coverage.

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
    Dependent,
    DependentRelationship,
    Employer,
    EmploymentFacts,
    FamilyComposition,
    FixedTerm,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    PayrollYearRequest,
)
from ccnl_engine.events import BonusEvent, FringeEvent, SickLeaveEvent

engine = PayrollEngine.bundled()


# ---------------------------------------------------------------------------
# Baseline: INPS contributions (area: INPS)
# ---------------------------------------------------------------------------


def test_inps_contributions_metalmeccanico_c3() -> None:
    """Employee and employer INPS for metalmeccanico C3, January 2026."""
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
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
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
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
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
        )
    )
    tfr = next(i for i in result.pay_items if i.kind == "tfr_accrual_item")
    assert tfr.amount == Decimal("159.87")


# ---------------------------------------------------------------------------
# Mensilità aggiuntive (area: tredicesima)
# ---------------------------------------------------------------------------


def test_tredicesima_commercio_level4() -> None:
    """Tredicesima for commercio level 4, computed via full-year run.

    The standard calendar is derived from the CCNL: tredicesima and
    quattordicesima, 14 runs.
    """
    yr = engine.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(50)),
        )
    )
    tredicesima = next(
        r
        for r in yr.period_results
        if r.run is not None and r.run.run_id == "2026-12-thirteenth"
    )
    assert tredicesima.period_gross == Decimal("1818.75")
    assert len(yr.period_results) == 14


# ---------------------------------------------------------------------------
# Addizionali regionali e comunali (area: addizionali)
# ---------------------------------------------------------------------------


def test_addizionali_emilia_romagna_modena() -> None:
    """Regional (ER) and municipal (Modena F257) surtax reduces net vs. no-surtax."""
    result_no_surtax = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
        )
    )
    result_surtax = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
            regione="ER",
            comune_belfiore="F257",
        )
    )
    assert result_no_surtax.period_net == Decimal("1751.35")
    assert result_surtax.period_net == Decimal("1746.66")
    assert result_surtax.period_net < result_no_surtax.period_net


# ---------------------------------------------------------------------------
# Domestico flat-rate INPS (area: domestico)
# ---------------------------------------------------------------------------


def test_domestic_inps_non_convivente() -> None:
    """Flat per-hour INPS contributions for domestic non-convivente worker, level B."""
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="lavoro-domestico-non-convivente.json",
            level_code="B",
            employment_facts=EmploymentFacts(
                weekly_hours=25,
                contributable_hours=Decimal(108),
            ),
            employer=Employer(headcount=Headcount(1)),
        )
    )
    assert result.period_gross == Decimal("1212.73")
    assert result.contribution_breakdown.employee == Decimal("33.48")
    assert result.contribution_breakdown.employer == Decimal("100.44")


# ---------------------------------------------------------------------------
# Fringe benefits within annual threshold (area: fringe)
# ---------------------------------------------------------------------------


def test_fringe_below_threshold_no_tax() -> None:
    """Fringe benefit within Art. 51 c. 3 annual threshold (580 EUR) is not taxed."""
    result_base = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
        )
    )
    result_fringe = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
            events=(FringeEvent(event_date=date(2026, 3, 1), amount=Decimal(100)),),
        )
    )
    assert result_fringe.period_net == result_base.period_net


# ---------------------------------------------------------------------------
# Malattia with sick leave integration (area: malattia)
# ---------------------------------------------------------------------------


def test_sickness_full_integration_metalmeccanico() -> None:
    """Metalmeccanico provides 100% sick pay; net is unchanged by a 5-day illness."""
    result_base = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
        )
    )
    result_sick = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
            events=(
                SickLeaveEvent(
                    event_date=date(2026, 3, 10),
                    amount=Decimal(0),
                    sick_days=5,
                    waiting_period_days=0,
                ),
            ),
        )
    )
    assert result_sick.period_net == result_base.period_net
    assert result_sick.unpaid_absence_deduction == Decimal(0)


# ---------------------------------------------------------------------------
# PdR (Premio di Risultato) substitute tax (area: PdR)
# ---------------------------------------------------------------------------


def test_pdr_productivity_bonus_separate_from_ordinary_irpef() -> None:
    """PdR bonus uses substitute-tax regime; net differs from ordinary-IRPEF path."""
    result_pdr = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
            events=(
                BonusEvent(
                    event_date=date(2026, 3, 1),
                    amount=Decimal(1000),
                    kind="productivity_bonus",
                    prior_income=Decimal(25000),
                ),
            ),
        )
    )
    result_ordinary = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(100)),
            events=(
                BonusEvent(
                    event_date=date(2026, 3, 1),
                    amount=Decimal(1000),
                    kind="bonus",
                    prior_income=None,
                ),
            ),
        )
    )
    assert result_pdr.period_gross == Decimal("3158.26")
    assert result_pdr.period_net == Decimal("2648.80")
    assert result_pdr.period_net > result_ordinary.period_net


# ---------------------------------------------------------------------------
# NASpI addizionale on fixed-term contracts (area: regimi 2026)
# ---------------------------------------------------------------------------


def test_naspi_addizionale_fixed_term() -> None:
    """Fixed-term contract incurs NASpI addizionale; employer cost exceeds permanent."""
    result_permanent = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(50)),
        )
    )
    result_fixed = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_facts=EmploymentFacts(
                contract_type=FixedTerm(),
            ),
            employer=Employer(headcount=Headcount(50)),
        )
    )
    assert result_fixed.period_employer_cost > result_permanent.period_employer_cost


# ---------------------------------------------------------------------------
# Family deductions Art. 12 TUIR (area: detrazioni familiari)
# ---------------------------------------------------------------------------


def test_family_deductions_increase_net() -> None:
    """Dependent spouse + children (Art. 12 TUIR) reduce IRPEF and raise net pay."""
    result_single = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(50)),
            regione="ER",
        )
    )
    result_family = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_facts=EmploymentFacts(),
            employer=Employer(headcount=Headcount(50)),
            regione="ER",
            family_composition=FamilyComposition(
                dependents=(
                    Dependent(relationship=DependentRelationship.SPOUSE),
                    Dependent(
                        relationship=DependentRelationship.CHILD,
                        birth_date=date(2015, 5, 10),
                    ),
                )
            ),
        )
    )
    assert result_single.period_net == Decimal("1489.92")
    assert result_family.period_net > result_single.period_net


# ---------------------------------------------------------------------------
# YTD state chaining (area: conguaglio / YTD)
# ---------------------------------------------------------------------------


def test_ytd_state_carries_irpef_forward() -> None:
    """Closing state from January carries YTD IRPEF withheld into February."""
    facts = EmploymentFacts()
    employer = Employer(headcount=Headcount(100))
    jan = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=facts,
            employer=employer,
        )
    )
    feb = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=2),
            payment_date=date(2026, 2, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=facts,
            employer=employer,
            opening_state=jan.closing_state,
        )
    )
    assert jan.closing_state.tax.irpef > Decimal(0)
    assert feb.closing_state.tax.irpef > jan.closing_state.tax.irpef
    assert feb.closing_state.regular_periods_closed == 2
