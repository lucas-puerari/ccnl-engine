"""Tax and credit base lines of a run: IRPEF, credits, surtax and PdR tax.

Every line posts a non-negative amount; the account gives its direction
and :mod:`~ccnl_engine.payroll.domain.remittance` its codice tributo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.period._line import WITHHOLDING, _BaseLine
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    EmployeeWithholdingItem,
    TaxCreditItem,
    TaxRefundItem,
)
from ccnl_engine.payroll.domain.remittance import (
    IRPEF_WITHHOLDING,
    PDR_SUBSTITUTE_TAX,
    REGIONAL_SURTAX,
    TRATTAMENTO_CREDIT,
)
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome

__all__ = ["surtax_split", "tax_lines"]


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


def surtax_split(withheld: Decimal, surtax: SurtaxOutcome) -> tuple[Decimal, Decimal]:
    """Split the surtax withheld on a run between region and municipality.

    The run withholds one amount: its share of the annual surtax plus any
    surtax carried in, capped at the pay available.  It is split in the
    ratio of the annual regional and municipal amounts; the municipal part
    takes the rounding residual, so the two add up to ``withheld``.

    Returns:
        ``(regional, municipal)``; ``(0, 0)`` when no annual surtax is
        known to split on.
    """
    total = surtax.total
    if total == _ZERO:
        return _ZERO, _ZERO
    regional = money(withheld * surtax.regional / total)
    return regional, withheld - regional


def _surtax_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the regional and municipal surtax withheld on the run.

    The regional line is coded 3802; the municipal line is uncoded.  A
    surtax carried in with no annual surtax to split on is posted on one
    uncoded ``surtax`` line.

    Returns:
        Each line only when its amount is positive.
    """
    withheld = amounts.period_surtax
    if withheld <= _ZERO:
        return []
    regional, municipal = surtax_split(withheld, amounts.surtax)
    if regional == municipal == _ZERO:
        parts: tuple[tuple[str, Decimal, str | None], ...] = (
            ("surtax", withheld, None),
        )
    else:
        parts = (
            ("surtax_regional", regional, REGIONAL_SURTAX),
            ("surtax_municipal", municipal, None),
        )
    return [
        _BaseLine(
            stem,
            WITHHOLDING,
            AccountKind.SURTAX,
            amount,
            EmployeeWithholdingItem,
            remittance_code=code,
        )
        for stem, amount, code in parts
        if amount > _ZERO
    ]


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
