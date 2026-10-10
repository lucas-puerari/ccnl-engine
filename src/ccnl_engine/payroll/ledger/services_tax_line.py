"""Tax and credit base lines of a run: IRPEF, credits, surtax and PdR tax.

Every line posts a non-negative amount; the account gives its direction
and :mod:`~ccnl_engine.payroll.ledger.models_remittance` its codice tributo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import (
    EmployeeWithholdingItem,
    TaxCreditItem,
    TaxRefundItem,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.ledger.models_remittance import (
    IRPEF_WITHHOLDING,
    PDR_SUBSTITUTE_TAX,
    TRATTAMENTO_CREDIT,
)
from ccnl_engine.payroll.ledger.services_line import WITHHOLDING, _BaseLine
from ccnl_engine.payroll.period.services_shared import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.amount.types import _PeriodAmounts

__all__ = ["tax_lines"]


def _trattamento_line(tratt: Decimal) -> _BaseLine:
    """Return the trattamento integrativo paid or recovered on the run.

    Returns:
        A ``CREDITS`` line coded 1701 when paid; a ``CREDIT_RECOVERIES``
        line when recovered, whose pay item keeps the negative amount.
    """
    if tratt > _ZERO:
        return _BaseLine(
            "tratt_integ",
            "tax_credit_item",
            AccountKind.CREDITS,
            tratt,
            TaxCreditItem,
            remittance_code=TRATTAMENTO_CREDIT,
        )
    return _BaseLine(
        "tratt_integ",
        "tax_credit_item",
        AccountKind.CREDIT_RECOVERIES,
        -tratt,
        TaxCreditItem,
        entry_stem="tratt_integ_recovery",
        item_amount=tratt,
    )


def _irpef_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the IRPEF withheld or refunded and the trattamento integrativo.

    Returns:
        Each line only when its amount is non-zero.
    """
    lines: list[_BaseLine] = []
    irpef = amounts.period_irpef
    if irpef > _ZERO:
        lines.append(
            _BaseLine(
                "irpef",
                WITHHOLDING,
                AccountKind.ORDINARY_TAX,
                irpef,
                EmployeeWithholdingItem,
                remittance_code=IRPEF_WITHHOLDING,
            )
        )
    elif irpef < _ZERO:
        lines.append(
            _BaseLine(
                "irpef_refund",
                "tax_refund_item",
                AccountKind.TAX_REFUNDS,
                -irpef,
                TaxRefundItem,
            )
        )
    if amounts.period_tratt != _ZERO:
        lines.append(_trattamento_line(amounts.period_tratt))
    return lines


def _surtax_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the surtax withheld and refunded on the run.

    The surtax withheld after the pay cap is split over what was due
    (:meth:`~ccnl_engine.payroll.taxation.rules_surtax.RunSurtax\
.allocate`): one line per component and reference year, coded 3802
    (regional), 3848 (municipal saldo) or 3847 (municipal acconto), and one
    uncoded ``surtax`` line for the surtax carried in for lack of pay.
    Surtax given back by the conguaglio (usually a municipal acconto above
    the surtax due) is a ``SURTAX_REFUNDS`` line.

    Returns:
        Each line only when its amount is positive.
    """
    surtax = amounts.surtax
    lines = [
        _BaseLine(
            "surtax" if part is None else part.stem,
            WITHHOLDING,
            AccountKind.SURTAX,
            amount,
            EmployeeWithholdingItem,
            remittance_code=None if part is None else part.remittance_code,
        )
        for part, amount in surtax.allocate(amounts.period_surtax)
        if amount > _ZERO
    ]
    if surtax.refund > _ZERO:
        lines.append(
            _BaseLine(
                "surtax_refund",
                "tax_refund_item",
                AccountKind.SURTAX_REFUNDS,
                surtax.refund,
                TaxRefundItem,
            )
        )
    return lines


def tax_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the tax and credit lines of a run, in payslip order.

    Returns:
        IRPEF and credits, surtax, then the PdR substitute tax, posted to
        the ledger without a pay item.
    """
    lines = [*_irpef_lines(amounts), *_surtax_lines(amounts)]
    if amounts.period_substitute_tax > _ZERO:
        lines.append(
            _BaseLine(
                "substitute_tax",
                "productivity_bonus_earning",
                AccountKind.SUBSTITUTE_TAX,
                amounts.period_substitute_tax,
                None,
                remittance_code=PDR_SUBSTITUTE_TAX,
            )
        )
    return lines
