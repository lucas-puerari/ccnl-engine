"""State opening of a period with other-employer facts."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest


def stated_opening(self: PeriodCalculationRequest) -> PeriodState:
    """Return the opening state with the stated base of other employers.

    Returns:
        ``opening_state``, with the INPS base of other employments of
        ``current_year`` when it is of the competence year.
    """
    year, facts = self.period_id.year, self.current_year
    if facts is None or facts.tax_year != year:
        return self.opening_state
    accrual = self.opening_state.accrual
    base = accrual.inps_base(year).stating_other_employers(
        facts.other_employment_inps_base
    )
    return replace(self.opening_state, accrual=accrual.with_inps_base(base))
