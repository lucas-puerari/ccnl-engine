"""The payslip of a run as lines, from its ledger.

Each ledger entry of an account the net pay reads
(:func:`~ccnl_engine.withholding.cap.services.run_net`) is one line: an
earning account fills the competenze column, a deduction account the
trattenute one, so the competenze less the trattenute are the net of the
run with no arithmetic of the caller.  A line of a pay item carries its
quantity, unit and rate; a statutory line (INPS, IRPEF, surtax) has none
and its voce is the account it posts to.
The employer accounts (contributions, TFR accrued) are not lines.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.payslip.line.models import PayslipLine, Progressives

if TYPE_CHECKING:
    from ccnl_engine.balance.models import PeriodState
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.models import PayItem
    from ccnl_engine.period.results import PeriodResult

__all__ = ["DEDUCTION_ACCOUNTS", "EARNING_ACCOUNTS", "payslip_lines", "progressives"]

#: Accounts the net adds: the competenze column.
EARNING_ACCOUNTS = frozenset({
    AccountKind.CASH_EARNINGS,
    AccountKind.TFR_SETTLEMENT,
    AccountKind.CREDITS,
    AccountKind.TAX_REFUNDS,
    AccountKind.SURTAX_REFUNDS,
    AccountKind.CREDIT_RECOVERY_SHORTFALL,
})
#: Accounts the net subtracts: the trattenute column.
DEDUCTION_ACCOUNTS = frozenset({
    AccountKind.CREDIT_RECOVERIES,
    AccountKind.EMPLOYEE_CONTRIBUTIONS,
    AccountKind.BILATERAL_FUND_EMPLOYEE,
    AccountKind.PENSION_FUND_EMPLOYEE,
    AccountKind.EMPLOYEE_DEDUCTIONS,
    AccountKind.SUBSTITUTE_TAX,
    AccountKind.ORDINARY_TAX,
    AccountKind.SURTAX,
    AccountKind.SEPARATE_TAX,
})
_ZERO = Decimal(0)
#: Kind of the statutory withholdings (INPS, IRPEF, surtax): their voce is
#: the account they post to.
_WITHHOLDING = "employee_withholding_item"


def payslip_lines(
    result: PeriodResult, voci: Mapping[str, str] | None = None
) -> tuple[PayslipLine, ...]:
    """Return the lines of the payslip of ``result``.

    Args:
        result: The run.
        voci: The provider's voce code by engine code; an engine code it
            does not name keeps itself.

    Returns:
        One line per ledger entry of an earning or a deduction account, in
        ledger order.
    """
    items = {item.item_id: item for item in result.pay_items}
    mapping = voci or {}
    return tuple(
        _line(entry, items.get(entry.pay_item_id), mapping)
        for entry in result.ledger_entries
        if entry.account in EARNING_ACCOUNTS | DEDUCTION_ACCOUNTS
    )


def _line(
    entry: LedgerEntry, item: PayItem | None, voci: Mapping[str, str]
) -> PayslipLine:
    earning = entry.account in EARNING_ACCOUNTS
    amounts = {
        "earning": entry.amount if earning else _ZERO,
        "deduction": _ZERO if earning else entry.amount,
    }
    if item is None or item.kind == _WITHHOLDING:
        code = entry.account.value
        return PayslipLine(
            voce=voci.get(code, code),
            engine_code=code,
            description=entry.note or code,
            quantity=None,
            unit=None,
            rate=None,
            **amounts,
        )
    code = item.voce_code
    return PayslipLine(
        voce=voci.get(code, code),
        engine_code=code,
        description=item.source or entry.note or code,
        quantity=item.voce_quantity,
        unit=item.unit,
        rate=item.rate,
        **amounts,
    )


def progressives(state: PeriodState, competence_year: int) -> Progressives:
    """Return the progressivi of the state a run closes with.

    Returns:
        The cash amounts of the tax year of ``state`` and the INPS base of
        this employment in ``competence_year``.
    """
    cash = state.cash
    base = next(
        (b.own for b in state.accrual.inps_bases if b.year == competence_year), _ZERO
    )
    return Progressives(
        tax_year=cash.tax_year,
        gross=cash.earnings.gross,
        taxable=cash.earnings.taxable,
        inps_employee=cash.earnings.inps_employee,
        irpef=cash.tax.irpef,
        surtax=cash.tax.surtax,
        inps_base=base,
    )
