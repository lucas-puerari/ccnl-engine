"""Employment context and temporal domain types for the period-first engine."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.seniority import LevelCategory
    from ccnl_engine.engine.payroll.domain.employment import (
        Apprentice,
        FixedTerm,
        Permanent,
    )

__all__ = ["EffectiveDateContext", "EmploymentFacts"]


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
class EmploymentFacts:
    """Employment facts consumed by the period-first payroll computation.

    Holds only the fields needed for the current calculation pipeline.
    Additional fields (part-time ratio, TFR choices, individual agreements)
    are added in later PRs as their computation chains are wired.

    Attributes:
        contract_type: Employment contract discriminant.  Drives INPS rate
            selection (Apprentice → reduced rates; FixedTerm → NASpI
            addizionale; Permanent → standard rates).
        category: Worker's CCNL category (operaio / impiegato / quadro /
            dirigente) as declared on the CCNL level.  None when the level
            carries no category annotation.
    """

    contract_type: Permanent | FixedTerm | Apprentice
    category: LevelCategory | None = None
