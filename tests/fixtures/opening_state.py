"""Opening state of a tax year whose earlier history is stated as empty.

A run opens with the history of the employment before it, or it has a
``missing_fact opening_state`` blocker: a zero state is the fact only for
the first run of an employment whose start is stated.  Tests of another
subject that run a year of an employment begun earlier open it here: the
balances imported for the tax year state that nothing is carried from the
year before (no surtax, no recovery, no deferral) and that the worker had
no other employment in the year.  A scenario computed by hand on zero
totals in a later month states the regular months before it as paid with
no amount.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import PayrollEngine
from ccnl_engine.inputs import (
    InpsBaseYtd,
    OpeningBalances,
    PaymentId,
    PayrollRunId,
    PeriodState,
)

__all__ = ["fresh_tax_year", "unpaid_months_before"]


def fresh_tax_year(year: int = 2026) -> PeriodState:
    """Return the state that opens ``year`` with nothing carried into it.

    Returns:
        The imported state of ``year``: no payment, no obligation, and an
        INPS base of ``year`` with no other employment.
    """
    return PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=year,
            inps_bases=(InpsBaseYtd(year, Decimal(0), Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )


def unpaid_months_before(month: int, year: int = 2026, *, day: int = 27) -> PeriodState:
    """Return the state of ``year`` whose regular runs before ``month`` paid nothing.

    The worker was employed from 1 January, as
    :func:`~tests.fixtures.seniority.new_hire` states, and the earlier
    months of the year carried no pay (an unpaid leave), so the run of
    ``month`` opens with zero totals and with its history.  January opens
    with :func:`fresh_tax_year`.

    Returns:
        The imported state with the regular payments of the months before
        ``month``, each paid on ``day``, and every total at zero.
    """
    if month == 1:
        return fresh_tax_year(year)
    return PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=year,
            payments=tuple(
                PaymentId(
                    PayrollRunId.parse(f"{year}-{m:02d}-regular"), date(year, m, day)
                )
                for m in range(1, month)
            ),
            inps_bases=(InpsBaseYtd(year, Decimal(0), Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
