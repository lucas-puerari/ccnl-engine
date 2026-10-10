"""The FIS rate cut of art. 29 c. 8-bis D.Lgs. 148/2015.

An employer with up to five employees that has not applied for the assegno
di integrazione salariale for twenty-four months pays the FIS rate of 0.50%
cut by 40%: 0.30%, of which 0.10% by the worker (art. 33 c. 1).  Against
the full shares of the INPS table (0.33% and 0.17%) the cut is 0.13% and
0.07%.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.tax.domain.contribution_rules import InpsRates
from ccnl_engine.tax.domain.fis_reduction import FisReduction, with_fis_reduction

_CUT = FisReduction(
    max_employees=5, employer_rate=Decimal("0.0013"), employee_rate=Decimal("0.0007")
)
_RATES = InpsRates(
    employee_rate=Decimal("0.0936"),
    employee_ivs_rate=Decimal("0.0919"),
    employer_rate=Decimal("0.2931"),
    employer_ivs_rate=Decimal("0.2381"),
    ceiling=None,
    employer_rate_by_category={WorkerCategory.OPERAIO: Decimal("0.3000")},
    fis_reduction=_CUT,
)


def test_a_reduced_employer_pays_the_cut_rates() -> None:
    """9.36% - 0.07% = 9.29% and 29.31% - 0.13% = 29.18%, by category too."""
    rates = with_fis_reduction(_RATES, reduced=True, headcount=5)

    assert rates.employee_rate == Decimal("0.0929")
    assert rates.employer_rate == Decimal("0.2918")
    assert rates.employer_rate_by_category == {
        WorkerCategory.OPERAIO: Decimal("0.2987")
    }
    assert not rates.fis_reduction_open


@pytest.mark.parametrize(
    ("rates", "reduced", "headcount"),
    [
        (_RATES, False, 5),
        (_RATES, True, 6),
        (_RATES.model_copy(update={"fis_reduction": None}), True, 5),
    ],
    ids=["not-reduced", "above-five", "no-cut-in-the-sector"],
)
def test_the_full_rates_apply_without_the_cut(
    rates: InpsRates, reduced: bool, headcount: int
) -> None:
    """No cut for an employer that applied, above five, or without one."""
    assert with_fis_reduction(rates, reduced=reduced, headcount=headcount) == rates


def test_an_unknown_employer_is_charged_the_full_rates_and_flagged() -> None:
    """Without the fact the full rates apply and the rates say it is open."""
    rates = with_fis_reduction(_RATES, reduced=None, headcount=3)

    assert rates.employee_rate == _RATES.employee_rate
    assert rates.employer_rate == _RATES.employer_rate
    assert rates.fis_reduction_open
