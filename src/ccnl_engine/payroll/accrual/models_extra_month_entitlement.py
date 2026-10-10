"""Equivalent months of pay per year granted by a CCNL.

The CCNL ``additional_months`` parameter is an :class:`ExtraMonthEntitlement`:
equivalent months of pay per year, possibly fractional (13.5).  It is not a
count of payslips; see
:class:`~ccnl_engine.payroll.year.models_schedule.PayrollRunCount`
and :class:`~ccnl_engine.payroll.year.models_schedule.WithholdingSchedule`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.validation import reject, require_decimal

__all__ = [
    "MAX_ADDITIONAL_MONTHS",
    "MIN_ADDITIONAL_MONTHS",
    "ExtraMonthEntitlement",
]

#: Most equivalent months a supported CCNL grants: tredicesima and
#: quattordicesima.
MAX_ADDITIONAL_MONTHS = Decimal(14)
#: The twelve regular months every CCNL pays.
MIN_ADDITIONAL_MONTHS = Decimal(12)

_FEATURE = "calendar"


@dataclass(frozen=True)
class ExtraMonthEntitlement:
    """Equivalent months of pay per year: 12 regular months plus extra months.

    The value is a :class:`~decimal.Decimal` and may be fractional: ``13.5``
    means a full tredicesima plus half a quattordicesima.  It says how much
    is paid, not how many payslips are issued; a fractional extra month is
    still paid in its own run.

    Attributes:
        value: Equivalent months, between 12 and 14 inclusive.

    Raises:
        InvalidInputError: When ``value`` is not a finite Decimal between
            12 and 14.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_decimal(
            self.value,
            "additional_months",
            feature=_FEATURE,
            minimum=MIN_ADDITIONAL_MONTHS,
            maximum=MAX_ADDITIONAL_MONTHS,
        )

    @classmethod
    def of(cls, value: int | Decimal) -> ExtraMonthEntitlement:
        """Build an entitlement from a CCNL parameter value.

        Args:
            value: Equivalent months as ``int`` or ``Decimal``.  Converted
                through ``str`` so no binary rounding is introduced.

        Returns:
            The validated :class:`ExtraMonthEntitlement`.
        """
        if isinstance(value, bool) or not isinstance(value, int | Decimal):
            reject("additional_months", "an int or a Decimal", value, feature=_FEATURE)
        return cls(Decimal(str(value)))
