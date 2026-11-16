"""Hourly percentage bases assembled from the paid monthly chain."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import FixedTerm
from ccnl_engine.errors import MissingRequiredFactError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.hourly.models import HourlyPercentage


def percentage_base(chain: MonthlyPayChain, percentage: HourlyPercentage) -> Decimal:
    """Return contractual base salary and the eligible paid elements.

    The named contractual allowances and, when the clause requests them,
    individual and territorial elements enter the percentage base.  An
    ordinary-remuneration floor integration is not automatically a named
    contractual allowance.

    Returns:
        The base of ``percentage`` on the pay of ``chain``.
    """
    named = percentage.base_allowances
    return chain.base + sum(
        (
            value
            for allowance, value in chain.allowances
            if allowance.code in named
            or (percentage.include_individual and allowance.individual)
            or (percentage.include_territorial and allowance.territorial)
        ),
        Decimal(0),
    )


def percentage_due(
    percentage: HourlyPercentage, contract_type: object, day: date
) -> bool:
    """Return whether the run pays ``percentage`` on its hours.

    A percentage whose first period starts after ``day`` is not yet in
    force.  One gated by ``fixed_term_years`` is paid to a fixed-term
    worker with at least those consecutive qualifying years.

    Returns:
        ``True`` when the percentage is in force and its gate is met.

    Raises:
        MissingRequiredFactError: When a gated percentage is in force and
            the fixed-term worker states no ``qualifying_years``.
    """
    if percentage.rate.periods[0].valid_from > day:
        return False
    needed = percentage.fixed_term_years
    if needed is None:
        return True
    if not isinstance(contract_type, FixedTerm):
        return False
    years = contract_type.qualifying_years
    if years is None:
        msg = (
            f"{percentage.code} is paid from {needed} consecutive qualifying "
            "years with the employer: FixedTerm.qualifying_years is not stated"
        )
        raise MissingRequiredFactError(msg, feature="base_salary")
    return years >= needed
