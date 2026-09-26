"""Annual withholding must match the tax owed on the final taxable income.

Scenario: CCNL Cooperative Sociali, level D2, full year 2026, 13.5 monthly
payments (tredicesima plus half a quattordicesima), no other income, no
family deductions.  At the last run of the year the sostituto d'imposta must
perform the conguaglio (art. 23 c. 3 DPR 600/1973), so the IRPEF withheld
over the year equals the net IRPEF on the final annual taxable income.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import PayrollYearRequest, PayrollYearResult
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from tests.acceptance.legal_scenarios._support import COOP_SOCIALI, ENGINE
from tests.fixtures.legal_examples.irpef_2026 import net_irpef

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")


def _coop_sociali_d2_year() -> PayrollYearResult:
    return ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=COOP_SOCIALI,
            level_code="D2",
            calendar=WorkCalendar.from_additional_months(2026, Decimal("13.5")),
        )
    )


@pytest.mark.xfail(
    strict=True,
    reason="fractional extra months truncate withholding slots, so the year-end "
    "conguaglio does not reach the tax owed on the final taxable income",
)
def test_fractional_extra_months_withhold_the_annual_tax() -> None:
    """Sum of per-run ordinary IRPEF equals the oracle on the final taxable.

    Expected: ``net_irpef(final taxable)``.  With the final taxable of
    21,182.05 EUR the oracle gives 1,337.83 EUR (derivation in
    ``test_irpef_oracle.test_first_bracket_with_further_deduction``).

    Observed on 26 September 2026: 14 runs, annual gross 23,325.71, final
    taxable 21,182.05, IRPEF withheld 1,833.32, last run IRPEF 0.00.
    """
    year = _coop_sociali_d2_year()
    final_taxable = year.period_results[-1].closing_state.earnings.taxable
    withheld = sum(
        (r.tax_computation.ordinary_tax for r in year.period_results), Decimal(0)
    )

    assert abs(withheld - net_irpef(final_taxable)) <= _CENT


@pytest.mark.xfail(
    strict=True,
    reason="fractional extra months leave trattamento integrativo credited "
    "although the annual income makes it not due",
)
def test_fractional_extra_months_settle_trattamento_integrativo() -> None:
    """Net trattamento integrativo over the year is zero.

    D.L. 3/2020 art. 1 c. 1 and c. 1-bis: above 15,000 EUR the credit is due
    only when the listed deductions exceed the gross tax.  With 21,182.05 EUR
    the employment deduction of 2,534.04, even adding the 1,000 further
    deduction, stays below the gross tax of 4,871.87, so nothing is due at
    year end.

    Observed on 26 September 2026: 171.43 credited in the fourteenth run and
    seven recoveries of 21.43, net 21.42 left credited.
    """
    year = _coop_sociali_d2_year()
    net_credit = sum(
        (r.tax_computation.trattamento_integrativo for r in year.period_results),
        Decimal(0),
    )

    assert net_credit == Decimal(0)
