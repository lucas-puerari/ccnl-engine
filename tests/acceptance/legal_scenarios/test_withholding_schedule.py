"""Annual withholding must match the tax owed on the final taxable income.

Scenario: CCNL Cooperative Sociali, level D2, full year 2026, 13.5 monthly
payments (tredicesima plus half a quattordicesima), no other income, no
family deductions.  At the last run of the year the sostituto d'imposta must
perform the conguaglio (art. 23 c. 3 DPR 600/1973), so the IRPEF withheld
over the year equals the net IRPEF on the final annual taxable income.
The same holds for a part-year employment, whose deductions are
proportioned to its days.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import CompetenceYearPlan, CompetenceYearResult, Employment
from ccnl_engine.inputs import EmploymentPeriod
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    COOP_SOCIALI,
    EMPLOYER,
    ENGINE,
)
from tests.fixtures.normative_oracles.irpef_2026 import net_irpef

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")


def _coop_sociali_d2_year() -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(ccnl_slug=COOP_SOCIALI, level_code="D2"),
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

    D.L. 3/2020 art. 1 c. 1 and c. 1-bis: above 15,000 EUR the credit is due
    only when the listed deductions exceed the gross tax.  With 21,182.05 EUR
    the employment deduction of 2,534.04, even adding the 1,000 further
    deduction, stays below the gross tax of 4,871.87, so nothing is due at
    year end.

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
        pytest.param("Q", Decimal("4534.24"), id="second-bracket"),
        pytest.param("3", Decimal("2301.37"), id="first-bracket"),
    ],
)
def test_part_year_employment_withholds_the_tax_on_its_days(
    level_code: str, expected: Decimal
) -> None:
    """Commercio hired 15 March 2026, open-ended: 292 days of employment.

    The deductions proportioned to the days (art. 13 c. 1 TUIR, L. 207/2024
    art. 1 c. 6) must reach the conguaglio.  292 / 365 is exactly 0.8.

    March pays 14 of 26 daily quotas (16-21, 23-28, 30, 31 March are the
    Mondays to Saturdays employed), each pay component rounded on its own,
    so the year loses ``G - G_march`` of gross and that amount less 9.19%
    INPS of taxable against a full March:

    - Level Q: March 1,608.00 against 2,986.29, 1,378.29 less 126.66 INPS,
      final taxable 30,438.68 - 1,251.63 = 29,187.05.  Gross tax 6,440.00
      + 1,187.05 * 33% = 6,831.73; deduction (1,910 * 0.9460 + 65) * 0.8 =
      1,497.49; further deduction 800.00; net 4,534.24.
    - Level 3: March 1,068.25 against 1,983.91, 915.66 less 84.15 INPS,
      final taxable 20,221.90 - 831.51 = 19,390.39.  Gross tax 4,459.79;
      ratio 8,609.61 / 13,000 truncated 0.6622; deduction (1,910 + 1,190 *
      0.6622) * 0.8 = 2,698.02 * 0.8 = 2,158.42; no further deduction below
      20,000; net 2,301.37.

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
    """Metalmeccanico C3 hired 1 July 2026 withholds evenly over its 7 slots.

    The tredicesima of December pays 6/12 (July to December), so every run
    must project that rateo, not a full month.  With the projection equal
    to the final taxable income, each of the seven slots (July to December
    plus the tredicesima) withholds a seventh of the annual tax.

    Expected: ``net_irpef(final taxable, 184) / 7`` per run, within two
    cents of rounding; 184 days from 1 July to 31 December.

    Observed on 26 September 2026 before the rateo reached the projection:
    the runs of July to December projected 14,010.96 EUR instead of
    13,010.20 and withheld 319.57 each, leaving 89.39 for the tredicesima.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                employment_period=EmploymentPeriod(date(2026, 7, 1)),
            ),
            employer=EMPLOYER,
        )
    )
    final_taxable = year.period_results[-1].closing_state.cash.earnings.taxable
    share = net_irpef(final_taxable, 184) / 7

    assert len(year.period_results) == 7
    for run in year.period_results:
        assert abs(run.tax_computation.ordinary_tax - share) <= Decimal("0.02")
