"""Pure state-transition function for the period-first payroll engine.

:func:`close` advances a :class:`~ccnl_engine.payroll.domain.state.PayrollState`
by one closed period using a
:class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`.

The function reads amounts exclusively from the result's ``ledger_entries``
(keyed by :class:`~ccnl_engine.engine.payroll.domain.ledger.AccountKind`), so
it stays correct as new axes are added to the result in later PRs.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.state import (
    ContributiveState,
    FiscalState,
    PayrollState,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult

_ZERO = Decimal(0)


def _sum_account(result: PeriodCalculationResult, account: AccountKind) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total amount for ``account`` in ``result.ledger_entries``, or zero
        when no entries for that account are present.
    """
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )


def close(
    opening: PayrollState,
    result: PeriodCalculationResult,
) -> PayrollState:
    """Advance ``opening`` by accumulating one closed period into the state.

    Reads amounts exclusively from ``result.ledger_entries`` so that the
    function stays correct as more pay axes are added to the result.  Fields
    not yet produced by the vertical slice (e.g. INAIL, leave, addizionali)
    carry over from ``opening`` unchanged.

    Args:
        opening: YTD state entering the period.
        result: Completed calculation result for the period being closed.

    Returns:
        A new :class:`~ccnl_engine.payroll.domain.state.PayrollState` with
        ``periods_closed`` incremented by one and all present-axis accumulators
        updated from the result's ledger.
    """
    gross = _sum_account(result, AccountKind.CASH_EARNINGS)
    inps_employee = _sum_account(result, AccountKind.EMPLOYEE_CONTRIBUTIONS)
    inps_employer = _sum_account(result, AccountKind.EMPLOYER_CONTRIBUTIONS)
    tfr = _sum_account(result, AccountKind.TFR_ACCRUAL)
    irpef = _sum_account(result, AccountKind.ORDINARY_TAX)
    tax_credits = _sum_account(result, AccountKind.CREDITS)

    new_periods_closed = opening.periods_closed + 1
    new_fiscal = FiscalState(
        taxable_income_ytd=opening.fiscal.taxable_income_ytd,
        irpef_gross_ytd=opening.fiscal.irpef_gross_ytd,
        irpef_withheld_ytd=opening.fiscal.irpef_withheld_ytd + irpef,
        work_income_deduction_ytd=opening.fiscal.work_income_deduction_ytd,
        fam_deductions_ytd=opening.fiscal.fam_deductions_ytd,
        art15_deductions_ytd=opening.fiscal.art15_deductions_ytd,
        trattamento_integrativo_ytd=(
            opening.fiscal.trattamento_integrativo_ytd + tax_credits
        ),
        addizionale_regionale_ytd=opening.fiscal.addizionale_regionale_ytd,
        addizionale_comunale_ytd=opening.fiscal.addizionale_comunale_ytd,
    )
    new_contributive = ContributiveState(
        gross_ytd=opening.contributive.gross_ytd + gross,
        inps_employee_ytd=opening.contributive.inps_employee_ytd + inps_employee,
        inps_employer_ytd=opening.contributive.inps_employer_ytd + inps_employer,
        inail_employer_ytd=opening.contributive.inail_employer_ytd,
        tfr_ytd=opening.contributive.tfr_ytd + tfr,
    )
    return PayrollState(
        tax_year=opening.tax_year,
        periods_closed=new_periods_closed,
        revision_id=f"ytd-{opening.tax_year}-p{new_periods_closed:02d}",
        fiscal=new_fiscal,
        contributive=new_contributive,
        leave=opening.leave,
        source_period_ids=(*opening.source_period_ids, result.period_id),
    )
