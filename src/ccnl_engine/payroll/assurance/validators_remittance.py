"""Remittance invariant: every tax and credit entry has a consistent code.

Implemented invariant:
    remittance_code_consistent: an entry carries a codice tributo only when its
        account admits that code
        (:data:`~ccnl_engine.payroll.ledger.models_remittance.ACCOUNT_CODES`), and
        every entry of an account whose code is always known (IRPEF
        withheld, separate tax, credits paid) carries one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.types import (
    InvariantCode,
    ReconciliationViolation,
)
from ccnl_engine.payroll.ledger.models_remittance import ACCOUNT_CODES, CODED_ACCOUNTS

if TYPE_CHECKING:
    from ccnl_engine.payroll.ledger.models import LedgerEntry
    from ccnl_engine.payroll.period.results import PeriodResult

__all__: list[str] = []


def _code_problem(entry: LedgerEntry) -> str | None:
    """Return why the code of ``entry`` is wrong, ``None`` when it is not.

    Returns:
        A message for a missing code on a coded account or a code the
        account does not admit.
    """
    code = entry.remittance_code
    if code is None:
        if entry.account in CODED_ACCOUNTS:
            return f"on {entry.account} has no codice tributo"
        return None
    if code not in ACCOUNT_CODES.get(entry.account, frozenset()):
        return f"on {entry.account} carries codice tributo {code}"
    return None


def check_remittance_code_consistent(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check the codice tributo of every ledger entry of ``result``.

    Returns:
        One violation per entry with a missing or inconsistent code.
    """
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.REMITTANCE_CODE_CONSISTENT,
            message=f"LedgerEntry '{e.entry_id}' {problem}",
        )
        for e in result.ledger_entries
        if (problem := _code_problem(e)) is not None
    ]
