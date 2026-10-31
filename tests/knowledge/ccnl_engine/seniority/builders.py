"""Recognised seniority for tests whose subject is not seniority.

A run whose level pays seniority increments needs the recognised seniority:
without it the result has a ``missing_fact`` blocker.  Tests about another
capability state a seniority that matures no increment in the runs they
compute, so their amounts are those of a worker without increments.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import (
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.inputs import SeniorityFact, SenioritySource
from ccnl_engine.period.repositories import BundledKnowledgeRepository

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.inputs import WorkerCategory
    from ccnl_engine.seniority.models import SeniorityIncrements

__all__ = ["SeniorityGapRepository", "new_hire", "pricing_category"]

#: First day the seniority amounts of the gap repository are known.
GAP_ENDS_ON = date(2026, 7, 1)


class SeniorityGapRepository(BundledKnowledgeRepository):
    """The bundle with the seniority amounts of a CCNL declared missing.

    Every amount of a seniority increment of the CCNL is a ``missing`` gap
    before :data:`GAP_ENDS_ON`: a run that pays an increment on an earlier
    date reads a declared gap.
    """

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the bundled CCNL with its seniority amounts missing early.

        Returns:
            The CCNL, its seniority series opening with the gap.
        """
        ccnl = super().load_ccnl(ccnl_id)
        increments = ccnl.parameters.seniority_increments
        amounts = {
            level: _missing_until(series, GAP_ENDS_ON)
            for level, series in increments.amount_by_level.items()
        }
        increments = increments.model_copy(update={"amount_by_level": amounts})
        parameters = ccnl.parameters.model_copy(
            update={"seniority_increments": increments}
        )
        return ccnl.model_copy(update={"parameters": parameters})


def _missing_until(series: TimeSeries, day: date) -> TimeSeries:
    start = series.periods[0].valid_from
    kept = tuple(
        p.model_copy(update={"valid_from": max(p.valid_from, day)})
        for p in series.periods
        if p.valid_until is None or p.valid_until > day
    )
    gap = ValidityPeriod(
        valid_from=start, valid_until=day, gap_kind=SalaryGapKind.MISSING
    )
    return TimeSeries(periods=(gap, *kept))


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
