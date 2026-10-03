"""Current-year income facts for tests that declare a family.

A run with a dependent who gives right to an art. 12 TUIR deduction needs
the reddito complessivo of the year: without it the result has a
``missing_fact`` blocker on ``current_year``.  Tests about another subject
state that the employment is the only income of the year.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine import CurrentYearTaxFacts

__all__ = ["employment_only"]


def employment_only(year: int = 2026) -> CurrentYearTaxFacts:
    """Return the facts of a worker with no income beyond this employment.

    Returns:
        Zero other income of ``year``, declared on 1 January.
    """
    return CurrentYearTaxFacts.employment_only(year, date(year, 1, 1))
