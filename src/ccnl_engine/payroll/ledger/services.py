"""Build base pay items and project base ledger entries for a period.

The base lines of a run (salary chain, INPS, TFR, IRPEF, credits, surtax and
PdR substitute tax) are collected as intents by
:mod:`~ccnl_engine.payroll.ledger.services_base_line`; pay items and
ledger entries are two projections of the same intents.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import (
    CompetencePeriod,
    FixedAllowanceEarning,
    PayItem,
)
from ccnl_engine.payroll.ledger.models import LedgerEntry
from ccnl_engine.payroll.ledger.services_base_line import _base_lines
from ccnl_engine.payroll.period.services_shared import (
    _make_entry,
    _require_resolution,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.amount.policies import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.amount.types import _PeriodAmounts
    from ccnl_engine.payroll.amount.types_chain import MonthlyPayChain
    from ccnl_engine.payroll.ledger.services_line import _BaseLine
    from ccnl_engine.payroll.period.models_payroll import PeriodId

#: Kinds resolved once per run, before any entry is posted; any other kind
#: is resolved only when a line of that kind is posted.
_EAGER_KINDS = (
    "base_salary_earning",
    "employee_withholding_item",
    "employer_contribution_item",
    "tfr_accrual_item",
)


def _run_tag(period_id: PeriodId, run_tag: str | None) -> str:
    return run_tag if run_tag is not None else f"{period_id.year}_{period_id.month:02d}"


def _pay_item(
    line: _BaseLine, tag: str, cp: CompetencePeriod, payment_date: date
) -> PayItem | None:
    """Return the pay item of ``line``, or ``None`` for a ledger-only line.

    Returns:
        The pay item, with the allowance code for a fixed allowance line.
    """
    item_id = f"{line.stem}_{tag}"
    amount = line.amount if line.item_amount is None else line.item_amount
    if line.allowance_code is not None:
        return FixedAllowanceEarning(
            item_id=item_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amount,
            allowance_code=line.allowance_code,
        )
    if line.item_type is None:
        return None
    return line.item_type(
        item_id=item_id,
        competence_period=cp,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=amount,
    )


def _build_pay_items(
    amounts: _PeriodAmounts,
    chain: MonthlyPayChain,
    period_id: PeriodId,
    payment_date: date,
    run_tag: str | None = None,
) -> tuple[PayItem, ...]:
    """Build the base pay-item tuple from resolved period amounts and chain.

    Returns:
        Tuple of :class:`~ccnl_engine.payroll.amount.facade.PayItem`
        instances for this period.
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = _run_tag(period_id, run_tag)
    items = (
        _pay_item(line, tag, cp, payment_date) for line in _base_lines(amounts, chain)
    )
    return tuple(item for item in items if item is not None)


def _project_ledger(
    amounts: _PeriodAmounts,
    chain: MonthlyPayChain,
    period_id: PeriodId,
    payment_date: date,
    resolver: PolicyResolver,
    context: PolicyContext,
    run_tag: str | None = None,
) -> tuple[LedgerEntry, ...]:
    """Project base pay items to ledger entries.

    Returns:
        Tuple of :class:`~ccnl_engine.payroll.ledger.models.LedgerEntry`
        instances.
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = _run_tag(period_id, run_tag)
    eager = {
        kind: _require_resolution(resolver, kind, context).policy_id
        for kind in _EAGER_KINDS
    }
    entries: list[LedgerEntry] = []
    for line in _base_lines(amounts, chain):
        policy_id = eager.get(line.kind)
        if policy_id is None:
            policy_id = _require_resolution(resolver, line.kind, context).policy_id
        entry_stem = line.entry_stem if line.entry_stem is not None else line.stem
        entries.append(
            _make_entry(
                f"{entry_stem}_{tag}",
                f"{line.stem}_{tag}",
                line.kind,
                cp,
                payment_date,
                line.account,
                line.amount,
                policy_id=policy_id,
                remittance_code=line.remittance_code,
            )
        )
    return tuple(entries)
