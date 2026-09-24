"""Employment context and temporal domain types for the period-first engine."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

__all__ = ["EffectiveDateContext"]


@dataclass(frozen=True)
class EffectiveDateContext:
    """Temporal context for one payroll period calculation.

    Attributes:
        period_start: First calendar day of the competence period.
        period_end: Last calendar day of the competence period.
        payment_date: Date on which the payslip is paid.
    """

    period_start: date
    period_end: date
    payment_date: date

    @classmethod
    def from_period(
        cls, year: int, month: int, payment_date: date
    ) -> EffectiveDateContext:
        """Build from competence year, month and payment date.

        Returns:
            An :class:`EffectiveDateContext` with start and end of the month.
        """
        _, last_day = calendar.monthrange(year, month)
        return cls(
            period_start=date(year, month, 1),
            period_end=date(year, month, last_day),
            payment_date=payment_date,
        )

    def contains(self, event_date: date) -> bool:
        """Return True when *event_date* falls within the competence period.

        Returns:
            True if period_start <= event_date <= period_end.
        """
        return self.period_start <= event_date <= self.period_end
