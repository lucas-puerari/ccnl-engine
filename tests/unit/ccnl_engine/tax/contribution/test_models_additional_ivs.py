"""The rule of the additional 1% IVS: rate and its two thresholds."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.tax.contribution.models_additional_ivs import AdditionalIvsRule

_RULE = {
    "rate": "0.01",
    "annual_threshold": "56224.00",
    "monthly_threshold": "4685.00",
}


def test_holds_the_thresholds_as_published() -> None:
    """Circ. INPS 6/2026 par. 5: 56,224.00 a year, 4,685.00 a month."""
    rule = AdditionalIvsRule.model_validate(_RULE)

    assert (rule.rate, rule.annual_threshold, rule.monthly_threshold) == (
        Decimal("0.01"),
        Decimal("56224.00"),
        Decimal("4685.00"),
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rate", "-0.01"),
        ("annual_threshold", "0"),
        ("monthly_threshold", "-1"),
        ("monthly_threshold", "56224.01"),
    ],
)
def test_rejects_an_impossible_rule(field: str, value: str) -> None:
    """A negative rate, a non-positive threshold, a month above the year."""
    with pytest.raises(ValidationError):
        AdditionalIvsRule.model_validate(_RULE | {field: value})
