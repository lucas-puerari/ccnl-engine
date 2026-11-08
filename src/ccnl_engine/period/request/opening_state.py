"""The opening INPS base from a stated current-year other-employment fact."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.balance.models import PeriodState
    from ccnl_engine.period.requests import PeriodCalculationRequest


def stated_opening(request: PeriodCalculationRequest) -> PeriodState:
    """Return the opening state with the stated base of other employers.

    Returns:
        ``opening_state``, with the INPS base of other employments of
        ``current_year`` when it is of the competence year.
    """
    year, facts = request.period_id.year, request.current_year
    if facts is None or facts.tax_year != year:
        return request.opening_state
    accrual = request.opening_state.accrual
    base = accrual.inps_base(year).stating_other_employers(
        facts.other_employment_inps_base
    )
    return replace(request.opening_state, accrual=accrual.with_inps_base(base))
