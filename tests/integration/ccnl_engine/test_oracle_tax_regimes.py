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
    DependentRelationship,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    WorkerCategory,
)
from ccnl_engine.results import CalculationStatus
from tests.integration.ccnl_engine.payroll.family.builders_dependents import (
    declared_dependent,
)
from tests.integration.ccnl_engine.payroll.taxation.builders_imported_surtax import (
    opening_with_2025_surtax,
)
from tests.integration.ccnl_engine.payroll.taxation.builders_prior_year import (
    RENEWAL_WAIVED,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

engine = PayrollEngine.bundled()
_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    category=WorkerCategory.IMPIEGATO,
    seniority=new_hire(),
    tfr_treasury_fund=False,
    pension_fund=NoPensionFund(),
    contract_type=Permanent(),
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
    the conguaglio, so 1,777.09 - 40.00 = 1,737.09.  The net without surtax
    is derived in ``test_oracle_period.test_irpef_ordinary_tax_metalmeccanico_c3``:
    2,158.26 - 204.79 INPS - 176.38 IRPEF.  The renewal regime on the minimo
    is waived so that the status shows the surtax alone.
    """
    result_no_surtax = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(100)
            ),
        )
    )
    result_surtax = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_C3,
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(100)
            ),
            facts=PeriodFacts(regione="IT-45", comune_belfiore="F257"),
            opening_state=opening_with_2025_surtax("IT-45", "F257"),
            prior_year=RENEWAL_WAIVED,
            current_year=employment_only(),
        )
    )
    assert result_no_surtax.period_net == Decimal("1777.09")
    assert result_surtax.period_net == Decimal("1737.09")
    assert result_surtax.assurance.calculation is CalculationStatus.FINAL


# ---------------------------------------------------------------------------
# PdR (Premio di Risultato) substitute tax (area: PdR)
# ---------------------------------------------------------------------------


def test_pdr_productivity_bonus_separate_from_ordinary_irpef() -> None:
    """PdR bonus uses substitute-tax regime; net differs from ordinary-IRPEF path.

    The PdR of 1,000 pays INPS but stays out of the IRPEF base: the month
    taxable is 2,158.26 - 299.69 (9.19% + 0.30% of the 3,158 of base, the
    3,158.26 to the whole euro, each rounded) = 1,858.57, taxed 23% = 427.47
    under art. 23 c. 2 lett. a) DPR 600/1973.  No opening state, so the year
    projects 12 more slots at 2,158.26 less 9.49% INPS: 1,858.57 +
    25,899.12 - 2,457.83 = 25,299.86.  Art. 13:
    1,910 + 1,190 * 0.2077 + 65 = 2,222.16, times 31/365 = 188.73;
    ulteriore detrazione 1,000 * 31/365 = 84.93; IRPEF 427.47 - 188.73 -
    84.93 = 153.81.  Substitute tax 1% of 1,000 = 10.00 (L. 199/2025 art.
    1 c. 9, the 2026 rate of the bundle's PdR rule).  Net 3,158.26 -
    299.69 - 153.81 - 10.00 = 2,694.76.
    """
    result_pdr = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=_C3,
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(100)
            ),
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
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(100)
            ),
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
    assert result_pdr.period_net == Decimal("2694.76")
    assert result_pdr.period_net > result_ordinary.period_net


# ---------------------------------------------------------------------------
# Family deductions Art. 12 TUIR (area: detrazioni familiari)
# ---------------------------------------------------------------------------


def test_family_deductions_increase_net() -> None:
    """Dependent spouse + children (Art. 12 TUIR) reduce IRPEF and raise net pay.

    Single, January (art. 23 c. 2 lett. a) DPR 600/1973): gross 1,783.75;
    with 50 employees, on the 1,784 of base (INPS circ. 208/2001), INPS
    9.19% = 163.95 plus FIS and CIGS 0.57% = 10.17, taxable 1,609.63 taxed
    23% = 370.21.  The year projects 13 more slots net of 9.76% INPS:
    1,609.63 + 23,188.75 x 0.9024 = 22,535.16.  Art. 13: 1,910 + 1,190 *
    0.4203 = 2,410.16, times 31/365 = 204.70; ulteriore detrazione 84.93;
    IRPEF 370.21 - 204.70 - 84.93 = 80.58, net 1,783.75 - 174.12 - 80.58 =
    1,529.05.
    """
    result_single = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(50)
            ),
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
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(50)
            ),
            facts=PeriodFacts(
                regione="IT-45",
                family_composition=FamilyComposition(
                    dependents=(
                        declared_dependent(relationship=DependentRelationship.SPOUSE),
                        declared_dependent(
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
    # January withholds none: the net is the one without surtax, 1,529.05.
    assert result_single.period_net == Decimal("1529.05")
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
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(
                provincial_pay_element=False, headcount=Headcount(50)
            ),
            facts=PeriodFacts(
                family_composition=FamilyComposition(
                    dependents=(
                        declared_dependent(relationship=DependentRelationship.SPOUSE),
                    )
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
