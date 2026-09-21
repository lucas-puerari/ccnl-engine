"""Build typed PayItem objects with PolicyDecision from payroll computation results.

Each non-zero computation output is wrapped as a typed PayItem carrying the
standard Italian payroll treatment (tax, contribution, TFR, cost axes).  The
resulting tuple can be stored on Calculation.pay_items and used to project raw
totals without re-running the computation.

Sub-modules
-----------
- :mod:`item_producer_policy` — treatment policies and POLICY_REGISTRY.
- :mod:`item_producer_gross` — gross, work-rules, and extra-month builders.
- :mod:`item_producer_fiscal` — fiscal, contribution, and tax-credit builders.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.item_producer_fiscal import _build_fiscal_items
from ccnl_engine.engine.payroll.domain.item_producer_gross import (
    _build_extra_month_items,
    _build_gross_items,
    _build_work_items,
    _last_day,
    _period,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.engine.payroll.service.fiscal_result import FiscalPay
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay


def build_pay_items(
    gross: GrossPay,
    work: WorkRulesPay,
    fiscal: FiscalPay,
    as_of: date,
    extra_monthly_payments: int = 0,
) -> tuple[PayItem, ...]:
    """Produce typed PayItem objects from a completed payroll computation.

    One item is produced per non-zero computation output.  Each item carries a
    :class:`~ccnl_engine.engine.payroll.domain.pay_items.PolicyDecision` that
    encodes the Italian payroll treatment on the four axes (tax, contribution,
    TFR, cost).  Amounts mirror those recorded by the ledger builder so that
    totals are derivable by summing items grouped by account.

    Args:
        gross: Resolved contractual pay components.
        work: Work-rules pay components (supplements, absence, variable pay).
        fiscal: Annual contributions, taxes and net pay.
        as_of: Competence date (first day of the payroll month).
        extra_monthly_payments: Number of extra monthly payments (0, 1, or 2).

    Returns:
        Tuple of typed PayItem objects, one per non-zero component.
    """
    period = _period(as_of)
    payment = _last_day(as_of)
    yymm = f"{period.year}_{period.month:02d}"
    items: list[PayItem] = []
    items.extend(_build_gross_items(gross, period, payment, yymm, as_of))
    items.extend(
        _build_extra_month_items(
            gross, extra_monthly_payments, period, payment, yymm, as_of
        )
    )
    items.extend(_build_work_items(work, period, payment, yymm, as_of))
    items.extend(_build_fiscal_items(fiscal, period, payment, yymm, as_of))
    return tuple(items)
