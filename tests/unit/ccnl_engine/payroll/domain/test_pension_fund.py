"""Validation of the pension fund enrolment."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
from ccnl_engine.shared.domain.errors import InvalidInputError


def test_valid_enrolment() -> None:
    """A code, a rate in [0, 1] and the TFR choice are accepted."""
    enrolment = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=False)
    assert enrolment.fund_code == "ALIFOND"
    employment = Employment(ccnl_slug="x.json", level_code="1", pension_fund=enrolment)
    assert employment.pension_fund is enrolment


@pytest.mark.parametrize(
    ("code", "rate", "tfr", "message"),
    [
        (1, Decimal("0.01"), True, "fund_code must be a non-blank str"),
        ("ALIFOND", 0.01, True, "employee_rate must be a finite Decimal"),
        ("ALIFOND", Decimal("0.01"), "yes", "tfr_to_fund must be a bool"),
        ("", Decimal("0.01"), True, "must be a non-blank str"),
        ("ALIFOND", Decimal("-0.01"), True, ">= 0 and <= 1"),
        ("ALIFOND", Decimal("1.01"), True, ">= 0 and <= 1"),
        ("ALIFOND", Decimal("NaN"), True, ">= 0 and <= 1"),
    ],
)
def test_invalid_enrolment(
    code: object, rate: object, tfr: object, message: str
) -> None:
    """A wrong type, an empty code or a rate outside [0, 1] is rejected."""
    with pytest.raises(InvalidInputError, match=message):
        PensionFundEnrolment(code, rate, tfr)  # type: ignore[arg-type]


def test_employment_rejects_another_type() -> None:
    """Employment.pension_fund must be an enrolment or None."""
    with pytest.raises(InvalidInputError, match="pension_fund must be"):
        Employment(ccnl_slug="x.json", level_code="1", pension_fund="ALIFOND")  # type: ignore[arg-type]
