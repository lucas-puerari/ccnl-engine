"""Enrolment of the worker in the complementary pension fund of the CCNL."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.shared.domain.validation import (
    require_bool,
    require_decimal,
    require_str,
)

__all__ = ["PENSION_FEATURE", "PensionFundEnrolment"]

#: Feature reported by the errors of the pension fund enrolment.
PENSION_FEATURE = "pension_fund"

_ZERO = Decimal(0)
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
        owner = "PensionFundEnrolment"
        require_str(
            self.fund_code,
            f"{owner}.fund_code",
            feature=PENSION_FEATURE,
            non_blank=True,
        )
        require_decimal(
            self.employee_rate,
            f"{owner}.employee_rate",
            feature=PENSION_FEATURE,
            minimum=_ZERO,
            maximum=_ONE,
        )
        require_bool(self.tfr_to_fund, f"{owner}.tfr_to_fund", feature=PENSION_FEATURE)
