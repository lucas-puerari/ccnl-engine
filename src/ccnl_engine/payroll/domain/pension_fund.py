"""Enrolment of the worker in the complementary pension fund of the CCNL."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.payroll.domain.request_checks import raise_on, type_error
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["PENSION_FEATURE", "PensionFundEnrolment"]

#: Feature reported by the errors of the pension fund enrolment.
PENSION_FEATURE = "pension_fund"

_ONE = Decimal(1)


@dataclass(frozen=True, slots=True)
class PensionFundEnrolment:
    """The worker's enrolment in a pension fund of the CCNL.

    Enrolment is voluntary (D.Lgs. 252/2005 art. 1 c. 2), so it is a fact
    of the employment, never derived from the CCNL.  The employer rate and
    its base come from the fund in ``CCNL.parameters.employer_funds``.

    Attributes:
        fund_code: Code of the fund in the CCNL data, e.g. ``"ALIFOND"``.
        employee_rate: Contribution the worker chose, as a fraction of the
            same base as the employer rate, e.g. ``Decimal("0.01")``.  It
            cannot be below the minimum of the CCNL when the bundle records
            one.
        tfr_to_fund: Whether the TFR accrued is paid to the fund
            (D.Lgs. 252/2005 art. 8 c. 1-2).  Required: the choice is the
            worker's, and it moves the TFR out of the company.

    Raises:
        InvalidInputError: When a field is not of its type, ``fund_code``
            is empty or ``employee_rate`` is outside [0, 1].
    """

    fund_code: str
    employee_rate: Decimal
    tfr_to_fund: bool

    def __post_init__(self) -> None:  # noqa: D105
        raise_on(
            type_error((
                ("fund_code", self.fund_code, str, False),
                ("employee_rate", self.employee_rate, Decimal, False),
                ("tfr_to_fund", self.tfr_to_fund, bool, False),
            )),
            PENSION_FEATURE,
        )
        if not self.fund_code:
            msg = "fund_code must not be empty"
            raise InvalidInputError(msg, feature=PENSION_FEATURE)
        rate = self.employee_rate
        if not rate.is_finite() or not Decimal(0) <= rate <= _ONE:
            msg = f"employee_rate must be in [0, 1]; got {rate}"
            raise InvalidInputError(msg, feature=PENSION_FEATURE)
