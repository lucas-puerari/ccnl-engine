"""Equivalent months of pay per year granted by a CCNL.

The CCNL ``additional_months`` parameter is an :class:`ExtraMonthEntitlement`:
equivalent months of pay per year, possibly fractional (13.5).  It is not a
count of payslips; see :class:`~ccnl_engine.payroll.domain.schedule.PayrollRunCount`
and :class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

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


def _require_decimal(value: object) -> None:
    if not isinstance(value, Decimal):
        msg = f"additional_months must be a Decimal; got {type(value).__name__}"
        raise TypeError(msg)


@dataclass(frozen=True)
class ExtraMonthEntitlement:
    """Equivalent months of pay per year: 12 regular months plus extra months.

    The value is a :class:`~decimal.Decimal` and may be fractional: ``13.5``
    means a full tredicesima plus half a quattordicesima.  It says how much
    is paid, not how many payslips are issued; a fractional extra month is
    still paid in its own run.

    Attributes:
        value: Equivalent months, between 12 and 14 inclusive.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _require_decimal(self.value)
        if not self.value.is_finite() or self.value < MIN_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={self.value} is below the minimum "
                f"of 12; a CCNL must have at least 12 regular months"
            )
            raise ValueError(msg)
        if self.value > MAX_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={self.value} exceeds the maximum "
                f"supported value of {MAX_ADDITIONAL_MONTHS}; "
                f"only CCNL contracts with up to {MAX_ADDITIONAL_MONTHS} "
                f"months are supported"
            )
            raise ValueError(msg)

    @classmethod
    def of(cls, value: int | Decimal) -> ExtraMonthEntitlement:
        """Build an entitlement from a CCNL parameter value.

        Args:
            value: Equivalent months as ``int`` or ``Decimal``.  Converted
                through ``str`` so no binary rounding is introduced.

        Returns:
            The validated :class:`ExtraMonthEntitlement`.
        """
        return cls(Decimal(str(value)))
