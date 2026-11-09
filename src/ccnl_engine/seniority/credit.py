"""Credit past apprenticeship to seniority-increment thresholds only."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import Apprentice

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.seniority.models import SeniorityIncrements


def credited_increment_months(
    months: int | None,
    rules: SeniorityIncrements,
    request: PeriodCalculationRequest,
) -> int | None:
    """Return completed whole months for integer increment thresholds.

    The fractional credit is kept exact until compared to a whole-month
    threshold: floor(service + apprenticeship * share) gives the same
    threshold result without prescribing how the CCNL rounds the credit.
    Other benefits still use the uncredited service months.

    Returns:
        Months applicable to increments: the service months alone when the
        duration is unknown (a lower bound, reported as provisional), and
        ``None`` only without the ordinary seniority fact.
    """
    if (
        months is None
        or rules.apprenticeship_credit_share is None
        or isinstance(request.contract_type, Apprentice)
    ):
        return months
    duration = (
        None if request.seniority is None else request.seniority.apprenticeship_months
    )
    if duration is None:
        return months
    total = Decimal(months) + Decimal(duration) * rules.apprenticeship_credit_share
    return int(total // 1)
