"""Base lines of a run: the posting intents of its salary, contributions and taxes.

Each :class:`_BaseLine` is projected both to a pay item and to a ledger
entry by :mod:`~ccnl_engine.payroll.application.post_ledger`; the tax and
credit lines come from
:mod:`~ccnl_engine.payroll.application.period._tax_lines`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.period._line import WITHHOLDING, _BaseLine
from ccnl_engine.payroll.application.period._tax_lines import tax_lines
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    SeniorityEarning,
    TfrAccrualItem,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.service.types import MonthlyPayChain

__all__ = ["_BaseLine", "_base_lines"]


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


def _pension_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the pension fund lines of a run whose worker is enrolled.

    The employee contribution is withheld from the pay, the employer
    contribution goes to the fund and its INPS solidarity contribution to
    the employer contributions.

    Returns:
        The three lines, none when the worker is not enrolled.
    """
    pension = amounts.pension
    if pension is None:
        return []
    return [
        _BaseLine(
            "pension_fund_employee",
            WITHHOLDING,
            AccountKind.PENSION_FUND_EMPLOYEE,
            pension.employee,
            EmployeeWithholdingItem,
        ),
        _BaseLine(
            "pension_fund_employer",
            "employer_contribution_item",
            AccountKind.PENSION_FUND_EMPLOYER,
            pension.employer,
            EmployerContributionItem,
        ),
        _BaseLine(
            "pension_solidarity",
            "employer_contribution_item",
            AccountKind.EMPLOYER_CONTRIBUTIONS,
            pension.solidarity,
            EmployerContributionItem,
        ),
    ]


def _contribution_lines(amounts: _PeriodAmounts) -> list[_BaseLine]:
    """Return the INPS employee, INPS employer and TFR lines of a run.

    Returns:
        The three lines, posted even when zero, then the pension fund lines.
    """
    return [
        _BaseLine(
            "inps_employee",
            WITHHOLDING,
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
            amounts.tfr.account,
            amounts.tfr.amount,
            TfrAccrualItem,
        ),
        *_pension_lines(amounts),
    ]


def _base_lines(amounts: _PeriodAmounts, chain: MonthlyPayChain) -> list[_BaseLine]:
    """Return every base line of a run, in payslip order.

    Returns:
        Earnings, contributions and TFR, IRPEF and credits, then other taxes.
    """
    return [
        *_earning_lines(chain),
        *_contribution_lines(amounts),
        *tax_lines(amounts),
    ]
