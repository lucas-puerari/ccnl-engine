"""Oracle cases of the tax regimes: surtaxes, PdR substitute tax, family deductions.

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
from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
    PriorYearTaxFacts,
)
from ccnl_engine.results import CalculationStatus
from tests.fixtures.current_year import employment_only
from tests.fixtures.imported_surtax import opening_with_2025_surtax
from tests.fixtures.seniority import new_hire

engine = PayrollEngine.bundled()
_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=new_hire(),
    tfr_treasury_fund=False,
)


# ---------------------------------------------------------------------------
# Addizionali regionali e comunali (area: addizionali)
# ---------------------------------------------------------------------------


def test_addizionali_emilia_romagna_modena() -> None:
    """January withholds the first installments of the 2025 surtax.

    The 2025 conguaglio determined 330.00 of regional surtax and 110.00 of
    municipal saldo (imported, stated by the test), each withheld in eleven
    installments from January (D.Lgs. 446/1997 art. 50 c. 4, D.Lgs.
    360/1998 art. 1 c. 5): 30.00 + 10.00 = 40.00 in January.  The 2026
    acconto (45.00) starts in March, and the 2026 surtax is determined at
    the conguaglio, so 1,751.35 - 40.00 = 1,711.35.
    """
    result_no_surtax = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
        )
    )
    result_surtax = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(regione="IT-45", comune_belfiore="F257"),
            opening_state=opening_with_2025_surtax("IT-45", "F257"),
        )
    )
    assert result_no_surtax.period_net == Decimal("1751.35")
    assert result_surtax.period_net == Decimal("1711.35")
    assert result_surtax.assurance.calculation is CalculationStatus.FINAL


# ---------------------------------------------------------------------------
# PdR (Premio di Risultato) substitute tax (area: PdR)
# ---------------------------------------------------------------------------


def test_pdr_productivity_bonus_separate_from_ordinary_irpef() -> None:
    """PdR bonus uses substitute-tax regime; net differs from ordinary-IRPEF path."""
    result_pdr = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(
                events=(
                    BonusEvent(
                        event_date=date(2026, 3, 1),
                        amount=Decimal(1000),
                        kind="productivity_bonus",
                    ),
                )
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(25000)),
        )
    )
    result_ordinary = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(
                events=(
                    BonusEvent(
                        event_date=date(2026, 3, 1),
                        amount=Decimal(1000),
                        kind="bonus",
                    ),
                )
            ),
        )
    )
    assert result_pdr.period_gross == Decimal("3158.26")
    assert result_pdr.period_net == Decimal("2648.80")
    assert result_pdr.period_net > result_ordinary.period_net


# ---------------------------------------------------------------------------
# Family deductions Art. 12 TUIR (area: detrazioni familiari)
# ---------------------------------------------------------------------------


def test_family_deductions_increase_net() -> None:
    """Dependent spouse + children (Art. 12 TUIR) reduce IRPEF and raise net pay."""
    result_single = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-45"),
        )
    )
    result_family = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(
                regione="IT-45",
                family_composition=FamilyComposition(
                    dependents=(
                        Dependent(relationship=DependentRelationship.SPOUSE),
                        Dependent(
                            relationship=DependentRelationship.CHILD,
                            birth_date=date(2015, 5, 10),
                        ),
                    )
                ),
            ),
            current_year=employment_only(),
        )
    )
    # The 2026 regional surtax is determined at the conguaglio and withheld
    # in 2027 (D.Lgs. 446/1997 art. 50 c. 4); with no 2025 surtax to carry,
    # January withholds none: the net is the one without surtax, 1,489.92.
    assert result_single.period_net == Decimal("1489.92")
    assert result_family.period_net > result_single.period_net


def test_spouse_deduction_flat_band() -> None:
    """A dependent spouse is worth 690 a year between 15,001 and 29,000 of income.

    Art. 12 c. 1 lett. a) n. 2 TUIR: the deduction is a flat 690 for income
    above 15,000 and up to 40,000; the increases of lett. b) start above
    29,000. Metalmeccanico C2 projects about 24,300 of taxable income, the
    only income of the worker.
    """
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=9),
            payment_date=date(2026, 9, 27),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C2",
                seniority=new_hire(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(
                family_composition=FamilyComposition(
                    dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
                ),
            ),
            current_year=employment_only(),
        )
    )
    family = [
        item.amount
        for item in result.tax_computation.components
        if item.name == "family_deductions"
    ]
    assert family == [Decimal("690.00")]
