"""Domestic-sector INPS rate selection (colf/badanti hourly brackets)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.tax.domain.contribution_rules import DomesticInpsRates


def resolve_domestic_inps_rate(
    rates: DomesticInpsRates,
    hourly_rate: Decimal,
    weekly_hours: Decimal,
    *,
    is_fixed_term: bool,
) -> tuple[Decimal, Decimal]:
    """Return ``(employee_per_hour, employer_per_hour)`` for the scenario.

    Returns:
        A tuple of (employee contribution per hour, employer contribution
        per hour) based on weekly_hours and hourly_rate.

    Raises:
        AssertionError: Structurally unreachable; the ``DomesticInpsRates``
            invariant guarantees an open-ended last bracket.
    """
    if weekly_hours > rates.weekly_hours_threshold:
        b = rates.hours_bracket
        er = b.employer_per_hour_fixed_term if is_fixed_term else b.employer_per_hour
        return b.employee_per_hour, er
    for bracket in rates.wage_brackets:
        if (
            bracket.hourly_rate_up_to is None
            or hourly_rate <= bracket.hourly_rate_up_to
        ):
            er = (
                bracket.employer_per_hour_fixed_term
                if is_fixed_term
                else bracket.employer_per_hour
            )
            return bracket.employee_per_hour, er
    # Unreachable: DomesticInpsRates invariant guarantees an open-ended
    # last bracket (hourly_rate_up_to=None) that covers every hourly_rate.
    raise AssertionError  # pragma: no cover
