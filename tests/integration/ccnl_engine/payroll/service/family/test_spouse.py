"""Spouse deduction of art. 12 c. 1 lett. a and b TUIR on the 2026 bundle.

Every expected value is computed by hand from the text quoted in
:mod:`tests.fixtures.normative_oracles.family_2026`, twelve months, full share:
each frontier of lett. a and of the five bands of lett. b is checked one
cent below, on and one cent above.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.family import Dependent, DependentRelationship
from ccnl_engine.payroll.service.family.spouse import spouse_annual, spouse_deduction
from ccnl_engine.tax.service.tax_optional_loaders import load_family_deduction_rules
from tests.fixtures.normative_oracles import family_2026

_D = Decimal
_RULES = load_family_deduction_rules(2026)
_SPOUSE = Dependent(relationship=DependentRelationship.SPOUSE)

#: (reddito complessivo, deduction, derivation)
_FRONTIERS = [
    ("0", "0.00", "ratio R/15,000 = 0: not due (c. 4)"),
    ("1", "800.00", "1/15,000 = 0.0000666 -> 0.0000; 800 - 0"),
    ("7500", "745.00", "0.5; 800 - 55"),
    ("14999.99", "690.01", "0.99999933 -> 0.9999; 800 - 109.989 = 690.011"),
    ("15000", "690.00", "ratio 1: 690 (c. 4)"),
    ("15000.01", "690.00", "flat band, number 2)"),
    ("29000", "690.00", "not above 29,000: no increase"),
    ("29000.01", "700.00", "band 1): + 10"),
    ("29199.99", "700.00", "band 1)"),
    ("29200", "700.00", "band 1), upper limit included"),
    ("29200.01", "710.00", "band 2): + 20"),
    ("34699.99", "710.00", "band 2)"),
    ("34700", "710.00", "band 2), upper limit included"),
    ("34700.01", "720.00", "band 3): + 30"),
    ("34999.99", "720.00", "band 3)"),
    ("35000", "720.00", "band 3), upper limit included"),
    ("35000.01", "710.00", "band 4): + 20"),
    ("35099.99", "710.00", "band 4)"),
    ("35100", "710.00", "band 4), upper limit included"),
    ("35100.01", "700.00", "band 5): + 10"),
    ("35199.99", "700.00", "band 5)"),
    ("35200", "700.00", "band 5), upper limit included"),
    ("35200.01", "690.00", "no band"),
    ("39999.99", "690.00", "flat band"),
    ("40000", "690.00", "flat band, upper limit included"),
    ("40000.01", "689.93", "39,999.99/40,000 = 0.99999975 -> 0.9999; 689.931"),
    ("50001", "517.43", "29,999/40,000 = 0.749975 -> 0.7499; 517.431"),
    ("60000", "345.00", "0.5; 690 x 0.5"),
    ("79999.99", "0.00", "0.01/40,000 = 0.00000025 -> 0.0000"),
    ("80000", "0.00", "ratio 0: not due (c. 4)"),
    ("80000.01", "0.00", "above 80,000: no number of lett. a applies"),
]


@pytest.mark.parametrize(
    ("income", "expected", "derivation"), _FRONTIERS, ids=[f[0] for f in _FRONTIERS]
)
def test_frontier(income: str, expected: str, derivation: str) -> None:
    """The full-year deduction at each frontier, cent below and above."""
    deduction = spouse_deduction(_SPOUSE, _D(income), _RULES)
    assert deduction.amount == _D(expected), derivation
    assert deduction.months == 12


@pytest.mark.parametrize(("income", "expected", "_"), _FRONTIERS)
def test_frontier_matches_the_independent_oracle(
    income: str, expected: str, _: str
) -> None:
    """The hand-computed table agrees with the oracle written from the text."""
    assert family_2026.spouse_deduction(_D(income)) == _D(expected)


def test_untruncated_ratio_would_differ() -> None:
    """Without c. 4 the 50,001 case would give 690 x 0.749975 = 517.48."""
    assert spouse_annual(_D(50001), _RULES) == _D("517.4310")


@pytest.mark.parametrize(
    ("start", "end", "months", "expected"),
    [
        # married on 15 June: June to December, 710 x 7 / 12 = 414.1666...
        (date(2026, 6, 15), None, 7, "414.17"),
        # separated on 10 March: January to March, 710 x 3 / 12 = 177.50
        (None, date(2026, 3, 10), 3, "177.50"),
        # one day in the year still counts its month: 710 / 12 = 59.1666...
        (date(2026, 12, 31), None, 1, "59.17"),
    ],
)
def test_dependency_starting_or_ending_mid_year(
    start: date | None, end: date | None, months: int, expected: str
) -> None:
    """Reddito complessivo 30,000 (band 2): 710 a year, by the months (c. 3)."""
    spouse = Dependent(
        relationship=DependentRelationship.SPOUSE,
        dependent_from=start,
        dependent_until=end,
    )
    deduction = spouse_deduction(spouse, _D(30000), _RULES)
    assert deduction.months == months
    assert deduction.amount == _D(expected)
    assert family_2026.spouse_deduction(_D(30000), months) == _D(expected)


@pytest.mark.parametrize(
    "spouse",
    [
        Dependent(relationship=DependentRelationship.SPOUSE, own_income=_D("2840.52")),
        Dependent(
            relationship=DependentRelationship.SPOUSE, residency_eligibility=False
        ),
    ],
    ids=["own-income-above-limit", "not-resident"],
)
def test_spouse_not_dependent(spouse: Dependent) -> None:
    """Own income above 2,840.51 (c. 2) or c. 2-bis: no month is due."""
    deduction = spouse_deduction(spouse, _D(30000), _RULES)
    assert deduction.months == 0
    assert deduction.amount == _D(0)


def test_own_income_on_the_limit_is_dependent() -> None:
    """The limit itself qualifies: "non superiore a 2.840,51 euro"."""
    spouse = Dependent(
        relationship=DependentRelationship.SPOUSE, own_income=_D("2840.51")
    )
    assert spouse_deduction(spouse, _D(30000), _RULES).amount == _D(710)
