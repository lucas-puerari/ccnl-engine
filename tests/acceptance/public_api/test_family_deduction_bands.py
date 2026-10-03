"""Art. 12 TUIR spouse deduction on the increase bands of lett. b).

The run is the last withholding run of the year, the tredicesima of
Metalmeccanico C3, so the annual taxable income is the opening balance plus
the run and nothing is projected.  The opening taxable is set so that the
year lands on the income of the case:

    opening taxable = income - taxable of the tredicesima (2,001.57)

with the tredicesima taxable from
:mod:`tests.fixtures.legal_examples.metalmeccanico_c3_2026`.  Employment
income is the only income, so it is the reddito complessivo.  Expected
deductions come from :mod:`tests.fixtures.legal_examples.family_2026`.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    Dependent,
    DependentRelationship,
    EmployerProfile,
    Employment,
    FamilyComposition,
    Headcount,
    OpeningBalances,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from tests.fixtures.legal_examples.family_2026 import (
    SPOUSE_BAND_EXAMPLES,
    spouse_deduction,
)
from tests.fixtures.legal_examples.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
    employee_taxable,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from tests.fixtures.legal_examples.family_2026 import IncomeBand

_ENGINE = PayrollEngine.bundled()
_SPOUSE = FamilyComposition(
    dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="the spouse deduction ignores the increase bands from 29,000 to 35,200",
)
@pytest.mark.parametrize(
    ("income", "band"),
    SPOUSE_BAND_EXAMPLES,
    ids=[str(income) for income, _ in SPOUSE_BAND_EXAMPLES],
)
def test_spouse_deduction_follows_increase_bands(
    income: Decimal, band: IncomeBand
) -> None:
    """A spouse dependent for twelve months, employment income only.

    Today the engine deducts 690 on every income of the flat band.
    """
    opening = OpeningBalances(
        tax_year=2026,
        regular_periods_closed=12,
        tax_withholding_periods_closed=12,
        taxable=income - employee_taxable(C3_MINIMUM_FROM_JUNE_2026),
    ).to_state()

    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(family_composition=_SPOUSE),
            opening_state=opening,
        )
    )

    annual_taxable = result.closing_state.ytd.earnings.taxable
    if not band.contains(annual_taxable):
        pytest.fail(f"annual taxable {annual_taxable} is outside the band {band}")
    (decision,) = [d for d in result.decisions if d.capability == "family_deductions"]
    assert decision.amount == spouse_deduction(income)
