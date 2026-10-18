"""Prior-year facts: the amounts they state are non-negative decimals."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts


def test_pay_above_ccnl_defaults_to_unknown() -> None:
    """Left out, the pay above the CCNL is not known, not zero."""
    assert PriorYearTaxFacts().pay_above_ccnl is None
    assert PriorYearTaxFacts(pay_above_ccnl=Decimal(0)).pay_above_ccnl == 0


@pytest.mark.parametrize("value", [Decimal(-1), Decimal("NaN"), 150])
def test_pay_above_ccnl_must_be_a_non_negative_decimal(value: object) -> None:
    """A negative, non-finite or non-Decimal amount is rejected."""
    with pytest.raises(InvalidInputError, match="pay_above_ccnl"):
        PriorYearTaxFacts(pay_above_ccnl=value)  # type: ignore[arg-type]
