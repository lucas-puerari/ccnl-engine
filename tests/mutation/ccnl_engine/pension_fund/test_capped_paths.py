"""The extra deduction of D.Lgs. 252/2005 art. 8 c. 6 is a declared residual.

A run whose contributions exceed the deduction cap left traverses the
limitation: a worker first employed from 2007 might deduct more.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.pension_fund.rules import PensionContribution
from ccnl_engine.pension_fund.services import EXTRA_DEDUCTION_LIMITATION, capped_paths


def _contribution(deductible: str) -> PensionContribution:
    return PensionContribution(
        terms=None,
        base=Decimal(0),
        employer=Decimal("60.00"),
        employee=Decimal("40.00"),
        solidarity=Decimal("6.00"),
        deductible=Decimal(deductible),
        contractual=Decimal(0),
    )


@pytest.mark.parametrize(
    ("deductible", "paths"),
    [("100.00", set()), ("99.99", {EXTRA_DEDUCTION_LIMITATION})],
)
def test_only_a_capped_run_traverses_it(deductible: str, paths: set[str]) -> None:
    """All of 100.00 deducted: nothing; one cent short: the limitation."""
    assert capped_paths(_contribution(deductible)) == paths


def test_a_worker_not_enrolled_traverses_nothing() -> None:
    """No contributions, no cap."""
    assert capped_paths(None) == frozenset()
