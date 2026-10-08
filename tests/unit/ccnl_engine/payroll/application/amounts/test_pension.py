"""The base a fund applies its rates to."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.compensation import FundContributionBase
from ccnl_engine.payroll.application.amounts._pension import fund_base


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        (FundContributionBase.INPS_BASE, Decimal("3000.00")),
        (FundContributionBase.TFR_BASE, Decimal("2000.00")),
    ],
)
def test_fund_base(kind: FundContributionBase, expected: Decimal) -> None:
    """A 1000.00 bonus enters the INPS base of 3000.00, not the TFR base."""
    assert (
        fund_base(kind, inps_base=Decimal("3000.00"), tfr_base=Decimal("2000.00"))
        == expected
    )
