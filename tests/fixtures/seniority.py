"""Recognised seniority for tests whose subject is not seniority.

A run whose level pays seniority increments needs the recognised seniority:
without it the result has a ``missing_fact`` blocker.  Tests about another
capability state a seniority that matures no increment in the runs they
compute, so their amounts are those of a worker without increments.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine import SeniorityFact, SenioritySource

__all__ = ["new_hire"]


def new_hire(year: int = 2026) -> SeniorityFact:
    """Return a seniority recognised from 1 January of ``year``.

    The shortest first increment of the bundle matures after 24 months, so
    no run of ``year`` or of the year after pays an increment.

    Returns:
        Zero months as of 1 January of ``year``, from the employer records.
    """
    return SeniorityFact.since(date(year, 1, 1), SenioritySource.EMPLOYER_RECORDS)
