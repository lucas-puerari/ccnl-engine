"""Recognised seniority for tests whose subject is not seniority.

A run whose level pays seniority increments needs the recognised seniority:
without it the result has a ``missing_fact`` blocker.  Tests about another
capability state a seniority that matures no increment in the runs they
compute, so their amounts are those of a worker without increments.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.inputs import SeniorityFact, SenioritySource

if TYPE_CHECKING:
    from ccnl_engine.contract.seniority.models import SeniorityIncrements
    from ccnl_engine.inputs import WorkerCategory

__all__ = ["new_hire", "pricing_category"]


def new_hire(year: int = 2026) -> SeniorityFact:
    """Return a seniority recognised from 1 January of ``year``.

    The shortest first increment of the bundle matures after 24 months, so
    no run of ``year`` or of the year after pays an increment.

    Returns:
        Zero months as of 1 January of ``year``, from the employer records.
    """
    return SeniorityFact.since(date(year, 1, 1), SenioritySource.EMPLOYER_RECORDS)


def pricing_category(
    increments: SeniorityIncrements, level_code: str
) -> WorkerCategory | None:
    """Return a category that prices the increments of a level, if needed.

    Returns:
        The first category with an amount for the level when the level has
        no category-independent amount, otherwise ``None``.
    """
    if not increments.requires_category(level_code):
        return None
    return next(
        category
        for category, amounts in increments.amount_by_level_by_category.items()
        if level_code in amounts
    )
