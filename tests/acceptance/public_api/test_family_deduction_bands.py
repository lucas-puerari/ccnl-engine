"""Art. 12 TUIR spouse deduction on the increase bands of lett. b).

The run is the last withholding run of the year, the tredicesima of
Metalmeccanico C3, so the annual taxable income is the opening balance plus
the run and nothing is projected.  The opening taxable is set so that the
year lands on the income of the case:

    opening taxable = income - taxable of the tredicesima (2,001.57)

with the tredicesima taxable from
:mod:`tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026`.  The worker
declares no income beyond this employment
(:meth:`~ccnl_engine.inputs.CurrentYearTaxFacts.employment_only`), so the
employment income of the year is the reddito complessivo.  Expected
deductions come from :mod:`tests.fixtures.normative_oracles.family_2026`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    DependentRelationship,
    FamilyComposition,
    InpsBaseYtd,
    OpeningBalances,
    Permanent,
)
from ccnl_engine.results import CalculationStatus
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.normative_oracles.family_2026 import (
    SPOUSE_BAND_EXAMPLES,
    spouse_deduction,
)
from tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
    employee_taxable,
)
from tests.fixtures.withholding import paid_before

if TYPE_CHECKING:
    from tests.fixtures.normative_oracles.family_2026 import IncomeBand

_ENGINE = PayrollEngine.bundled()
_SPOUSE = FamilyComposition(
    dependents=(declared_dependent(relationship=DependentRelationship.SPOUSE),)
)


@pytest.mark.parametrize(
    ("income", "band"),
    SPOUSE_BAND_EXAMPLES,
    ids=[str(income) for income, _ in SPOUSE_BAND_EXAMPLES],
)
def test_spouse_deduction_follows_increase_bands(
    income: Decimal, band: IncomeBand
) -> None:
    """A spouse dependent for twelve months, employment income only."""
    opening = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.thirteenth(2026, 12), day=18),
            taxable=income - employee_taxable(C3_MINIMUM_FROM_JUNE_2026),
            inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )

    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(family_composition=_SPOUSE),
            current_year=CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1)),
            opening_state=opening,
        )
    )

    annual_taxable = result.closing_state.cash.earnings.taxable
    if not band.contains(annual_taxable):
        pytest.fail(f"annual taxable {annual_taxable} is outside the band {band}")
    (decision,) = [d for d in result.decisions if d.capability == "family_deductions"]
    assert decision.amount == spouse_deduction(income)
    assert decision.status is CalculationStatus.FINAL
