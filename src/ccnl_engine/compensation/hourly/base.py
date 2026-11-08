"""Hourly percentage bases assembled from the paid monthly chain."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.hourly.models import HourlyPercentage


def percentage_base(chain: MonthlyPayChain, percentage: HourlyPercentage) -> Decimal:
    """Return contractual base salary and the eligible paid elements.

    The named contractual allowances and, when the clause requests them,
    individual elements enter the percentage base. An ordinary-remuneration
    floor integration is not automatically a named contractual allowance.

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
        ),
        Decimal(0),
    )
