"""Post earnings (base salary, seniority, allowances) to the ledger."""

from __future__ import annotations

import calendar
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.service.gross import GrossPay

_ZERO = Decimal(0)


def _last_day(as_of: date) -> date:
    """Return the last calendar day of the month containing *as_of*.

    Returns:
        A :class:`~datetime.date` for the final day of that month.
    """
    import datetime  # noqa: PLC0415

    last = calendar.monthrange(as_of.year, as_of.month)[1]
    return datetime.date(as_of.year, as_of.month, last)


def post_earnings(gross: GrossPay, as_of: date, ledger: Ledger) -> None:
    """Post base salary, seniority and fixed allowances as CASH_EARNINGS entries.

    Entries with a zero amount are silently skipped.  All entries are posted to
    :attr:`~ccnl_engine.engine.payroll.domain.ledger.AccountKind.CASH_EARNINGS`.

    Args:
        gross: The resolved gross-pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    if gross.chain.base != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"base_salary_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"base_salary_{yymm}",
                pay_item_kind="base_salary_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=gross.chain.base,
                source_item_id=f"base_salary_{yymm}",
                policy_decision_id="it/earning/ordinary",
            )
        )

    if gross.chain.seniority != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"seniority_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"seniority_{yymm}",
                pay_item_kind="seniority_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=gross.chain.seniority,
                source_item_id=f"seniority_{yymm}",
                policy_decision_id="it/earning/ordinary",
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
                payment_date=payment,
                pay_item_id=f"allowance_{allowance.code}_{yymm}",
                pay_item_kind="fixed_allowance_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=amount,
                source_item_id=f"allowance_{allowance.code}_{yymm}",
                policy_decision_id="it/earning/ordinary",
                note=allowance.code,
            )
        )
