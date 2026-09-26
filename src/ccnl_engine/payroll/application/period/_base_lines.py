"""Base lines of a run: the posting intents of its salary, contributions and taxes.

Each :class:`_BaseLine` is projected both to a pay item and to a ledger
entry by :mod:`~ccnl_engine.payroll.application.post_ledger`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    SeniorityEarning,
    TaxCreditItem,
    TaxRefundItem,
    TfrAccrualItem,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.service.types import MonthlyPayChain

_ItemType = (
    type[BaseSalaryEarning]
    | type[SeniorityEarning]
    | type[EmployeeWithholdingItem]
    | type[EmployerContributionItem]
    | type[TfrAccrualItem]
    | type[TaxRefundItem]
    | type[TaxCreditItem]
)

_WITHHOLDING = "employee_withholding_item"


@dataclass(frozen=True)
class _BaseLine:
    """Posting intent of one base line: its pay item and its ledger entry.

    Attributes:
        stem: Id of the pay item and of the entry, before the run tag.
        kind: Pay-item kind of the entry and of its policy resolution.
        account: Ledger account the entry is posted to.
        amount: Amount of the item and of the entry.
        item_type: Pay-item class, or ``None`` for a line posted to the
            ledger only (the PdR substitute tax).
        entry_stem: Entry id stem when it differs from ``stem``.
        allowance_code: Code of a fixed allowance line.
    """

    stem: str
    kind: str
    account: AccountKind
    amount: Decimal
    item_type: _ItemType | None
    entry_stem: str | None = None
    allowance_code: str | None = None


def _earning_lines(chain: MonthlyPayChain) -> list[_BaseLine]:
    """Return the base salary, seniority and allowance lines of ``chain``.

    Returns:
        The base salary line, then seniority and each allowance when positive.
    """
    cash = AccountKind.CASH_EARNINGS
    lines = [
        _BaseLine(
            "base_salary",
            "base_salary_earning",
            cash,
            chain.base,
            BaseSalaryEarning,
            entry_stem="cash_earnings",
        )
    ]
    if chain.seniority > _ZERO:
        lines.append(
            _BaseLine(
                "seniority",
                "seniority_earning",
                cash,
                chain.seniority,
                SeniorityEarning,
            )
        )
    lines.extend(
        _BaseLine(
            f"allowance_{allowance.code}",
            "fixed_allowance_earning",
            cash,
            amount,
            None,
            allowance_code=allowance.code,
        )
        for allowance, amount in chain.allowances
        if amount > _ZERO
    )
    return lines


def _contribution_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the INPS employee, INPS employer and TFR lines of a run.

    Returns:
        The three lines, posted even when zero.
    """
    return [
        _BaseLine(
            "inps_employee",
            _WITHHOLDING,
            AccountKind.EMPLOYEE_CONTRIBUTIONS,
            amounts.inps_employee,
            EmployeeWithholdingItem,
        ),
        _BaseLine(
            "inps_employer",
            "employer_contribution_item",
            AccountKind.EMPLOYER_CONTRIBUTIONS,
            amounts.inps_employer,
            EmployerContributionItem,
        ),
        _BaseLine(
            "tfr",
            "tfr_accrual_item",
            AccountKind.TFR_ACCRUAL,
            amounts.tfr,
            TfrAccrualItem,
        ),
    ]


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
                _WITHHOLDING,
                AccountKind.ORDINARY_TAX,
                irpef,
                EmployeeWithholdingItem,
            )
        )
    elif irpef < _ZERO:
        lines.append(
            _BaseLine(
                "irpef_refund",
                "tax_refund_item",
                AccountKind.CREDITS,
                -irpef,
                TaxRefundItem,
            )
        )
    if amounts.period_tratt != _ZERO:
        lines.append(
            _BaseLine(
                "tratt_integ",
                "tax_credit_item",
                AccountKind.CREDITS,
                amounts.period_tratt,
                TaxCreditItem,
            )
        )
    return lines


def _other_tax_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the surtax and the PdR substitute tax lines of a run.

    Returns:
        Each line only when its amount is positive; the substitute tax is
        posted to the ledger without a pay item.
    """
    lines: list[_BaseLine] = []
    if amounts.period_surtax > _ZERO:
        lines.append(
            _BaseLine(
                "surtax",
                _WITHHOLDING,
                AccountKind.SURTAX,
                amounts.period_surtax,
                EmployeeWithholdingItem,
            )
        )
    if amounts.period_substitute_tax > _ZERO:
        lines.append(
            _BaseLine(
                "substitute_tax",
                "productivity_bonus_earning",
                AccountKind.SUBSTITUTE_TAX,
                amounts.period_substitute_tax,
                None,
            )
        )
    return lines


def _base_lines(amounts: _PeriodAmounts, chain: MonthlyPayChain) -> list[_BaseLine]:
    """Return every base line of a run, in payslip order.

    Returns:
        Earnings, contributions and TFR, IRPEF and credits, then other taxes.
    """
    return [
        *_earning_lines(chain),
        *_contribution_lines(amounts),
        *_irpef_lines(amounts),
        *_other_tax_lines(amounts),
    ]
