"""The ratei of an extra month accrued by the end of a run's month."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.extra_month.schedule.models import ExtraMonthKind

__all__ = ["ExtraMonthProgress"]


@dataclass(frozen=True)
class ExtraMonthProgress:
    """The ratei of one extra month a payslip prints as maturati.

    Attributes:
        kind: Which extra month (tredicesima, quattordicesima).
        payment_year: Year the extra month of the window is paid in.
        months: Ratei accrued in the window by the end of the run's month,
            0 to 12 (whole months, plus the days of a day-based rule).
        fraction: Share of a monthly pay those ratei are worth.
    """

    kind: ExtraMonthKind
    payment_year: int
    months: Decimal
    fraction: Decimal
