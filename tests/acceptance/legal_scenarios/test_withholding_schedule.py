"""Annual withholding must match the tax owed on the final taxable income.

Scenario: CCNL Cooperative Sociali, level D2, full year 2026, 13.5 monthly
payments (tredicesima plus half a quattordicesima), no other income, no
family deductions.  At the last run of the year the sostituto d'imposta must
perform the conguaglio (art. 23 c. 3 DPR 600/1973), so the IRPEF withheld
over the year equals the net IRPEF on the final annual taxable income.
The same holds for a part-year employment, whose deductions are
proportioned to its days.  Before the conguaglio each run withholds on its
own pay (art. 23 c. 2 DPR 600/1973): a regular month on the brackets
divided by twelve less the deductions of the month (lett. a), an
additional month on the same brackets with no deduction (lett. b), and
the art. 12 TUIR deductions only from the month their conditions arise
(art. 12 c. 3 TUIR).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    Employment,
    PayrollRun,
)
from ccnl_engine.inputs import (
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    COOP_SOCIALI,
    EMPLOYER,
    ENGINE,
)
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.explicit_facts import CONCIA_D2, FACTS, competence_year
from tests.fixtures.normative_oracles.family_2026 import spouse_deduction
from tests.fixtures.normative_oracles.irpef_2026 import net_irpef
from tests.fixtures.normative_oracles.withholding_2026 import (
    extra_month_withholding,
    regular_month_withholding,
)

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")


def _coop_sociali_d2_year() -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=COOP_SOCIALI, level_code="D2", contract_type=Permanent()
            ),
            employer=EMPLOYER,
        )
    )


def test_fractional_extra_months_withhold_the_annual_tax() -> None:
    """Sum of per-run ordinary IRPEF equals the oracle on the final taxable.

    Expected: ``net_irpef(final taxable)``.  With the final taxable of
    21,182.05 EUR the oracle gives 1,337.83 EUR (derivation in
    ``test_irpef_net_oracle.test_first_bracket_with_further_deduction``).

    Before the withholding schedule was split from the equivalent months,
    the engine withheld 1,833.32 (26 September 2026): 13 slots for 14 runs
    made the last run project the opening taxable 19,613.01, below the
    20,000 threshold of the further deduction.
    """
    year = _coop_sociali_d2_year()
    final_taxable = year.period_results[-1].closing_state.cash.earnings.taxable
    withheld = sum(
        (r.tax_computation.ordinary_tax for r in year.period_results), Decimal(0)
    )

    assert abs(withheld - net_irpef(final_taxable)) <= _CENT


def test_fractional_extra_months_settle_trattamento_integrativo() -> None:
    """Net trattamento integrativo over the year is zero.

    D.L. 3/2020 art. 1 c. 1, second period: above 15,000 EUR the credit is
    due only when the listed deductions (art. 12 and art. 13 c. 1 TUIR, no
    family deduction is computed here) exceed the gross tax.  With 21,182.05
    EUR the employment deduction of 2,534.04 stays below the gross tax of
    4,871.87, so nothing is due at year end.

    Before the withholding schedule was split from the equivalent months,
    the engine credited 171.43 in the fourteenth run and recovered seven
    instalments of 21.43, leaving 21.42 (26 September 2026).
    """
    year = _coop_sociali_d2_year()
    net_credit = sum(
        (r.tax_computation.trattamento_integrativo for r in year.period_results),
        Decimal(0),
    )

    assert net_credit == Decimal(0)


@pytest.mark.parametrize(
    ("level_code", "expected"),
    [
        pytest.param("Q", Decimal("4461.19"), id="second-bracket"),
        pytest.param("3", Decimal("2264.44"), id="first-bracket"),
    ],
)
def test_part_year_employment_withholds_the_tax_on_its_days(
    level_code: str, expected: Decimal
) -> None:
    """Commercio hired 15 March 2026, open-ended: 292 days of employment.

    The deductions proportioned to the days (art. 13 c. 1 TUIR, L. 207/2024
    art. 1 c. 6) must reach the conguaglio.  292 / 365 is exactly 0.8.

    March pays 14 of 26 daily quotas (16-21, 23-28, 30, 31 March are the
    Mondays to Saturdays employed), each pay component rounded on its own.
    The employer has 50 employees: the worker pays 9.19% IVS and 0.57% of
    FIS (0.27%) and CIGS (0.30%) on the pay of each run to the whole euro,
    each share rounded on its own (INPS circ. 117/2022 all. 1 and 208/2001;
    D.Lgs. 148/2015 artt. 23 c. 1-bis, 29 c. 8):

    - Level Q: runs of 1,608.00, 2,986.29 seven times, 995.43 (June
      fourteenth), 3,047.05 twice and 2,539.22 (thirteenth): 32,140.78 of
      gross, 3,136.65 of INPS, final taxable 29,004.13.  Gross tax 6,440.00
      + 1,004.13 * 33% = 6,771.36; deduction (1,910 * 0.9543 + 65) * 0.8 =
      1,510.17; further deduction 800.00; net 4,461.19.
    - Level 3: runs of 1,068.25, 1,983.91 seven times, 661.31, 2,024.38
      twice and 1,686.99: 21,352.68 of gross, 2,084.00 of INPS, final
      taxable 19,268.68.  Gross tax 4,431.80; ratio 8,731.32 / 13,000
      truncated 0.6716; deduction (1,910 + 1,190 * 0.6716) * 0.8 =
      2,167.36; no further deduction below 20,000; net 2,264.44.

    Observed on 26 September 2026 before the days reached the tax
    computation: full-year deductions on a 292-day employment.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=COMMERCIO,
                level_code=level_code,
                employment_period=EmploymentPeriod(date(2026, 3, 15)),
                contract_type=Permanent(),
            ),
            employer=EMPLOYER,
        )
    )
    final_taxable = year.period_results[-1].closing_state.cash.earnings.taxable
    withheld = sum(
        (r.tax_computation.ordinary_tax for r in year.period_results), Decimal(0)
    )

    assert net_irpef(final_taxable, 292) == expected
    assert abs(withheld - expected) <= _CENT


def test_mid_year_hire_projects_the_tredicesima_it_will_accrue() -> None:
    """Metalmeccanico C3 hired 1 July 2026: 184 days, 7 slots.

    The tredicesima of December pays 6/12 (July to December), so July
    projects that rateo, not a full month: 2,001.61 (2,211.43 less 203.19
    IVS and 6.63 CIGS on the 2,211 of base, INPS circ. 208/2001) + five
    months and half a month to come, 11,057.15 + 1,105.72 = 12,162.87,
    less 9.49% INPS 1,154.26: 13,010.22.  Observed on 26
    September 2026 before the rateo reached the projection: 14,010.96.

    Each regular month withholds under art. 23 c. 2 lett. a) DPR 600/1973:
    23% of 2,001.61 = 460.37, less the art. 13 deduction of the 184 days
    (1,955 x 184 / 365 = 985.53) times the days of the month over 184: 31
    days give 166.04 and 294.33 withheld, 30 days 160.68 and 299.69.  The
    tredicesima settles the year (art. 23 c. 3): the IRPEF withheld is the
    net IRPEF of the final taxable for 184 days.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                employment_period=EmploymentPeriod(date(2026, 7, 1)),
                contract_type=Permanent(),
            ),
            employer=EMPLOYER,
        )
    )
    runs = year.period_results
    (july_projection,) = (
        d.inputs["taxable_income"]
        for d in runs[0].decisions
        if d.capability == "trattamento_integrativo"
    )
    final_taxable = runs[-1].closing_state.cash.earnings.taxable
    withheld = sum((r.tax_computation.ordinary_tax for r in runs), Decimal(0))

    assert len(runs) == 7
    assert july_projection == Decimal("13010.22")
    for run, days in zip(runs[:6], (31, 31, 30, 31, 30, 31), strict=True):
        assert run.tax_computation.ordinary_tax == regular_month_withholding(
            Decimal("2001.61"), Decimal("13010.22"), days, employment_days=184
        )
    assert runs[0].tax_computation.ordinary_tax == Decimal("294.33")
    assert runs[2].tax_computation.ordinary_tax == Decimal("299.69")
    assert abs(withheld - net_irpef(final_taxable, 184)) <= _CENT


def test_fourteenth_withholds_on_monthly_brackets() -> None:
    """Commercio level 4, hired 1 January 2026: the June quattordicesima.

    The fourteenth pays 6/12 of the month (January to June of the July-June
    window): 1,783.75 / 2 = 891.88, INPS base 892 (whole euro, INPS circ.
    208/2001).  The employer has 50 employees: INPS 9.19% = 81.97 plus FIS
    and CIGS 0.57% = 5.08, taxable 804.83.  It is under 28,000 / 12 =
    2,333.33, so lett. b) withholds 23% of it with no deduction: 185.11.
    The June regular run pays 1,783.75 less 163.95 and 10.17 of INPS on
    1,784, 1,609.63 of taxable (23% = 370.21), and takes the deductions of
    its 30 days on the projected 9,657.78 + 13,378.13 x 0.9024 = 21,730.20:
    art. 13 1,910 + 1,190 x 0.4822 = 2,483.82, times 30/365 = 204.15, and
    the ulteriore detrazione 1,000 x 30/365 = 82.19 (lett. a): 83.87.
    Observed on 6 October 2026 before this rule: 129.91 on the fourteenth,
    the share of a regular month.
    """
    employment = replace(CONCIA_D2, category=None, ccnl_slug=COMMERCIO, level_code="4")
    year = ENGINE.calculate_competence_year(competence_year(employment=employment))
    runs = {r.run: r for r in year.period_results}
    fourteenth = runs[PayrollRun.fourteenth(2026, 6)]
    regular = runs[PayrollRun.regular(2026, 6)]
    taxable = fourteenth.period_gross - sum(
        (
            e.amount
            for e in fourteenth.ledger_entries
            if e.account == "employee_contributions"
        ),
        Decimal(0),
    )
    withheld = fourteenth.tax_computation.ordinary_tax

    assert taxable == Decimal("804.83")
    assert withheld == extra_month_withholding(taxable) == Decimal("185.11")
    assert regular.tax_computation.ordinary_tax == regular_month_withholding(
        Decimal("1609.63"), Decimal("21730.20"), 30
    )
    assert regular.tax_computation.ordinary_tax == Decimal("83.87")


def _concia_d2_with(family: FamilyComposition) -> dict[PayrollRun, Decimal]:
    plan = replace(
        competence_year(), default_facts=replace(FACTS, family_composition=family)
    )
    year = ENGINE.calculate_competence_year(plan)
    return {
        r.run: r.tax_computation.ordinary_tax
        for r in year.period_results
        if r.run is not None
    }


def test_spouse_from_july_does_not_lower_january() -> None:
    """A spouse dependent from 15 July is deducted from July, not before.

    Art. 12 c. 3 TUIR: the family deductions "sono rapportate a mese e
    competono dal mese in cui si sono verificate"; art. 23 c. 2 lett. a)
    DPR 600/1973 applies them to the pay of the period.  January withholds
    the same with or without the spouse; July withholds one month of the
    spouse deduction less: 690 / 12 = 57.50 (art. 12 c. 1 lett. a) n. 2,
    reddito complessivo between 15,000 and 40,000: Concia D2 projects
    2,052.32 x 13 less 194.77 x 13 of INPS = 24,148.15, see
    ``normative_oracles.payslips.concia_d2_2026``).

    Observed on 6 October 2026, when the annual tax was spread over the
    slots: the spouse lowered the January withholding of Metalmeccanico C3
    from 202.10 to 175.56.
    """
    spouse = declared_dependent(
        DependentRelationship.SPOUSE, dependent_from=date(2026, 7, 15)
    )
    alone = _concia_d2_with(FamilyComposition())
    married = _concia_d2_with(FamilyComposition(dependents=(spouse,)))
    january, july = PayrollRun.regular(2026, 1), PayrollRun.regular(2026, 7)

    assert married[january] == alone[january]
    assert alone[july] - married[july] == spouse_deduction(Decimal("24148.15"), 1)
    assert alone[july] - married[july] == Decimal("57.50")
