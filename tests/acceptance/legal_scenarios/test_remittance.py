"""F24 remittance of a run: IRPEF withheld, credits paid and credits recovered.

The withholding agent remits the IRPEF it withholds under 1001 and offsets
the credits it paid in the column "importi a credito compensati": 1701 for
the trattamento integrativo (ris. AdE 35/E/2020) and 1704 for the somma of
L. 207/2024 art. 1 c. 4 (ris. AdE 9/E/2025).  The IRPEF line is gross of
the credits: they are separate F24 lines, not a lower withholding.

Scenario: Portieri B5, 2026, 2025 employment income 25,000 EUR, 13 runs
(the CCNL grants the tredicesima only).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment
from ccnl_engine.inputs import PriorYearTaxFacts
from ccnl_engine.results import RemittanceColumn
from tests.acceptance.legal_scenarios._support import (
    EMPLOYER,
    ENGINE,
    regular_period,
    remitted,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_PORTIERI = "portieri-fabbricati-confedilizia.json"
_PRIOR = PriorYearTaxFacts(employment_income=Decimal("25000.00"))


def _account(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def test_run_reports_withholding_and_credits_on_separate_lines() -> None:
    """January: 1,200 / 13 = 92.31 of trattamento integrativo under 1701.

    D.L. 3/2020 art. 1 c. 1: 1,200 EUR a year, shared over the 13
    withholding slots of the year.  The 1001 line is the IRPEF withheld,
    not the IRPEF less the credit: the net pay adds the credits back.
    """
    result = regular_period(ccnl_slug=_PORTIERI, level_code="B5", prior_year=_PRIOR)
    lines = {
        (str(ln.account), ln.remittance_code): ln for ln in result.remittance_summary()
    }

    tratt = lines["credits", "1701"]
    assert tratt.amount == Decimal("92.31")
    assert tratt.column is RemittanceColumn.CREDIT
    irpef = lines["ordinary_tax", "1001"]
    assert irpef.column is RemittanceColumn.DEBIT
    assert irpef.amount == result.tax_computation.ordinary_tax
    assert result.period_net == (
        _account(result, "cash_earnings")
        - _account(result, "employee_contributions")
        - remitted(result, "1001")
        + remitted(result, "1701")
        + remitted(result, "1704")
    )


def test_year_offsets_the_whole_trattamento_under_1701() -> None:
    """The year offsets the 1,200 EUR of D.L. 3/2020 art. 1 c. 1 under 1701.

    The worker qualifies for the full amount: 13 runs of 1,264.51 EUR of
    CCNL pay less 9.19% employee INPS (116.21 a run) give a taxable income
    of 13 x 1,148.30 = 14,927.90 EUR, within the 15,000 EUR of c. 1.  The
    year summary is the sum of the run summaries, code by code.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(ccnl_slug=_PORTIERI, level_code="B5"),
            employer=EMPLOYER,
            prior_year=_PRIOR,
        )
    )
    totals = {
        (str(ln.account), ln.remittance_code): ln.amount
        for ln in year.remittance_summary()
    }

    assert totals["credits", "1701"] == Decimal("1200.00")
    for key, amount in totals.items():
        assert amount == sum(
            (
                ln.amount
                for r in year.period_results
                for ln in r.remittance_summary()
                if (str(ln.account), ln.remittance_code) == key
            ),
            Decimal(0),
        )
