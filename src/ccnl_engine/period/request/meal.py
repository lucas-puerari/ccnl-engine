"""Validate declared days of a contractual meal benefit."""

from calendar import monthrange

from ccnl_engine.validators import require_int


def validate_meal_days(days: int | None, year: int, month: int) -> None:
    """Reject a non-integral count exceeding the competence month's days."""
    if days is not None:
        require_int(
            days,
            "PeriodCalculationRequest.meal_benefit_days",
            feature="period_request",
            minimum=0,
            maximum=monthrange(year, month)[1],
        )
