"""Invariant of a run whose employer is not a withholding agent.

Implemented invariant:
    non_agent_untaxed: when the employer is not a withholding agent (see
        :mod:`~ccnl_engine.payroll.service.withholding_agent`), the run posts
        nothing to the tax and credit accounts, so by ``net_identity`` its
        net is the gross less the employee contributions and the other
        non-tax deductions; and the net never exceeds the gross plus the
        TFR settled on the run, which is paid outside the gross.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.invariants._types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.invariants._types import RunFacts
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__: list[str] = []

_ZERO = Decimal(0)
#: Accounts only a withholding agent posts to.
_TAX_ACCOUNTS = (
    AccountKind.ORDINARY_TAX,
    AccountKind.SUBSTITUTE_TAX,
    AccountKind.SEPARATE_TAX,
    AccountKind.SURTAX,
    AccountKind.CREDITS,
    AccountKind.CREDIT_RECOVERIES,
    AccountKind.CREDIT_RECOVERY_SHORTFALL,
    AccountKind.TAX_REFUNDS,
    AccountKind.SURTAX_REFUNDS,
)


def check_non_agent_untaxed(
    result: PeriodResult, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that a non-withholding employer posts no tax and no credit.

    Returns:
        One violation per tax or credit account with an entry, and one when
        the net exceeds the gross plus the TFR settled; nothing for a
        withholding agent.
    """
    if facts.withholding_agent:
        return []
    violations = [
        ReconciliationViolation(
            invariant_id=InvariantCode.NON_AGENT_UNTAXED,
            message=f"employer is not a withholding agent but posts {account}",
            expected=_ZERO,
            actual=_sum_account(result, account),
        )
        for account in _TAX_ACCOUNTS
        if any(e.amount for e in result.ledger_entries if e.account == account)
    ]
    ceiling = result.period_gross + _sum_account(result, AccountKind.TFR_SETTLEMENT)
    if result.period_net > ceiling:
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.NON_AGENT_UNTAXED,
                message="net above the gross of an employer that withholds no tax",
                expected=ceiling,
                actual=result.period_net,
            )
        )
    return violations
