"""The ulteriore detrazione reads the reddito complessivo of the year.

L. 207/2024 art. 1 c. 6: the ulteriore detrazione is due to workers "che
hanno un reddito complessivo superiore a 20.000 euro" and falls to zero at
40,000 EUR; c. 9 counts in it the exempt share of the impatriati and
researcher regimes.  The withholding agent verifies it on the data the
worker communicates (AdE circ. 4/E/2025 par. 1.2).

Metalmeccanico C3 in January 2026: the year is projected at 25,394.74 of
employment income, so the ulteriore detrazione is due (1,000 x 31/365 =
84.93 in January).  15,000 EUR of other income bring the reddito
complessivo above 40,000: nothing is due.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from ccnl_engine import Employment, PeriodResult
from ccnl_engine.inputs import CurrentYearTaxFacts, Permanent
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=new_hire(),
    contract_type=Permanent(),
)


def _january(current_year: CurrentYearTaxFacts | None) -> PeriodResult:
    return regular_period(employment=_C3, current_year=current_year)


def _ulteriore(result: PeriodResult) -> Decimal:
    return sum(
        (
            c.amount
            for c in result.tax_computation.components
            if c.name == "ulteriore_detrazione"
        ),
        Decimal(0),
    )


_15K = Decimal(15000)


@pytest.mark.parametrize(
    "above",
    [
        replace(employment_only(), other_income=_15K),
        replace(employment_only(), exempt_regime_income=_15K),
        replace(employment_only(), other_employment_income=_15K),
    ],
    ids=["other_income", "exempt_regime_income", "other_employment_income"],
)
def test_income_beyond_the_employment_removes_it(above: CurrentYearTaxFacts) -> None:
    """25,394.74 + 15,000.00 exceeds 40,000: the ulteriore is not due."""
    alone = _january(employment_only())
    assert _ulteriore(alone) > 0
    assert _ulteriore(_january(above)) == 0


def test_unknown_income_is_a_missing_fact_while_it_is_due() -> None:
    """Without current_year the amount on this employment alone is flagged."""
    result = _january(None)
    assert _ulteriore(result) > 0
    assert "ulteriore_income_unknown" in {i.code for i in result.issues}
    assert "ulteriore_income_unknown" not in {
        i.code for i in _january(employment_only()).issues
    }
