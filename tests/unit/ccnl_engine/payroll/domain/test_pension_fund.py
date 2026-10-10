"""Validation of the pension fund enrolment."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employment import Employment, Permanent
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment


def test_valid_enrolment() -> None:
    """A code, a rate in [0, 1] and the TFR choice are accepted."""
    enrolment = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=False)
    assert enrolment.fund_code == "ALIFOND"
    employment = Employment(
        ccnl_slug="x.json",
        level_code="1",
        pension_fund=enrolment,
        contract_type=Permanent(),
    )
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
        ("ALIFOND", Decimal(0), False, "confers the TFR alone"),
    ],
)
def test_invalid_enrolment(
    code: object, rate: object, tfr: object, message: str
) -> None:
    """A wrong type, an empty code, a rate outside [0, 1] or none at all."""
    with pytest.raises(InvalidInputError, match=message):
        PensionFundEnrolment(code, rate, tfr)  # type: ignore[arg-type]


def test_employment_rejects_another_type() -> None:
    """Employment.pension_fund must be an enrolment or None."""
    with pytest.raises(InvalidInputError, match="pension_fund must be"):
        Employment(
            ccnl_slug="x.json",
            level_code="1",
            pension_fund="ALIFOND",  # type: ignore[arg-type]
            contract_type=Permanent(),
        )


def test_conversion_date_needs_the_conversion() -> None:
    """A request date without the option states nothing to convert."""
    with pytest.raises(InvalidInputError, match="needs seniority_to_fund"):
        PensionFundEnrolment(
            "PREVIAMBIENTE",
            Decimal("0.013"),
            tfr_to_fund=True,
            seniority_converted_on=date(2024, 3, 1),
        )
