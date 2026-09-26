"""Employment context and temporal domain types for the period-first engine."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

__all__ = ["EffectiveDateContext", "TemporalContext"]


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


@dataclass(frozen=True)
class TemporalContext:
    """Explicit temporal references for each payroll computation axis.

    Groups the three temporal reference points used in payroll computation,
    making the axis assignment named and auditable rather than implicit.

    Attributes:
        competence: First day of the competence period.  Used for CCNL
            time-series lookups (base salary, seniority, allowances).
        fiscal_year: Calendar year for statutory rate tables (IRPEF brackets,
            INPS thresholds, fringe-benefit ceilings).
        payment: Date on which the payslip is paid.  Used for withholding
            timing and trattamento integrativo proration.
    """

    competence: date
    fiscal_year: int
    payment: date

    @classmethod
    def from_period(cls, year: int, month: int, payment_date: date) -> TemporalContext:
        """Build from competence year, month and payment date.

        Returns:
            A :class:`TemporalContext` with ``competence`` set to the first
            day of the period and ``fiscal_year`` equal to *year*.
        """
        return cls(
            competence=date(year, month, 1),
            fiscal_year=year,
            payment=payment_date,
        )
