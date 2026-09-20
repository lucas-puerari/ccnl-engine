"""Post contractual pay components to the Ledger as LedgerEntry records."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.service.gross import GrossPay

_ZERO = Decimal(0)


def post_earnings(gross: GrossPay, as_of: date, ledger: Ledger) -> None:
    """Post base salary, seniority and fixed allowances as GROSS_EARNINGS entries.

    Entries with a zero amount are silently skipped.  All entries are posted to
    :attr:`~ccnl_engine.engine.payroll.domain.ledger.AccountKind.GROSS_EARNINGS`.

    Args:
        gross: The resolved gross-pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"

    if gross.chain.base != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"base_salary_{yymm}",
                competence_period=period,
                pay_item_id=f"base_salary_{yymm}",
                pay_item_kind="base_salary_earning",
                account=AccountKind.GROSS_EARNINGS,
                amount=gross.chain.base,
            )
        )

    if gross.chain.seniority != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"seniority_{yymm}",
                competence_period=period,
                pay_item_id=f"seniority_{yymm}",
                pay_item_kind="seniority_earning",
                account=AccountKind.GROSS_EARNINGS,
                amount=gross.chain.seniority,
                note=f"count={gross.count}",
            )
        )

    for allowance, amount in gross.chain.allowances:
        if amount == _ZERO:
            continue
        ledger.append(
            LedgerEntry(
                entry_id=f"allowance_{allowance.code}_{yymm}",
                competence_period=period,
                pay_item_id=f"allowance_{allowance.code}_{yymm}",
                pay_item_kind="fixed_allowance_earning",
                account=AccountKind.GROSS_EARNINGS,
                amount=amount,
                note=allowance.code,
            )
        )
