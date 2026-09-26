"""Close a tax year: open the next one with the obligations still running."""

from __future__ import annotations

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState

__all__ = ["close_tax_year"]


def close_tax_year(closing: PeriodState) -> PeriodState:
    """Return the opening state of tax year N+1 from the year-end state of N.

    The tax year state restarts: no run closed, every YTD account at zero,
    bound to N+1.  The obligations are carried unchanged: an installment
    recovery opened in N (D.L. 3/2020 art. 1 c. 3) keeps its origin year and
    its remaining installments are due from the first run of N+1, one per
    run, until the last one.  Those installments are deducted on the
    payslips of N+1 without entering the N+1 trattamento integrativo
    account.

    Year-end rule: ``closing`` must be bound to a tax year and every
    withholding slot of that year must be closed
    (:attr:`~ccnl_engine.payroll.domain.tax_year_state.TaxYearState.is_complete`),
    so that the conguaglio has run and any recovery it opened is recorded.
    A state computed only up to an earlier run, or built by hand without a
    run, is rejected.  For balances imported from another provider at the
    turn of the year, build the N+1 state with
    :class:`~ccnl_engine.payroll.application.opening_balances.OpeningBalances`.

    Args:
        closing: ``closing_state`` of the last run of tax year N.

    Returns:
        The state to pass as ``opening_state`` to the first run of N+1.

    Raises:
        InvalidInputError: When ``closing`` is not a year-end state.
    """
    ytd = closing.ytd
    if ytd.tax_year is None:
        msg = (
            "cannot close a tax year from a state bound to no tax year: pass "
            "the closing state of the last run of the year"
        )
        raise InvalidInputError(msg, feature="tax_year")
    if not ytd.is_complete:
        msg = (
            f"tax year {ytd.tax_year} is not complete: "
            f"{ytd.tax_withholding_periods_closed} of {ytd.withholding_slots} "
            "withholding slots closed; close the year after its last run"
        )
        raise InvalidInputError(msg, feature="tax_year")
    return PeriodState(
        ytd=TaxYearState(tax_year=ytd.tax_year + 1),
        obligations=closing.obligations,
    )
