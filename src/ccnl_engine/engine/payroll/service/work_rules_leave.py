"""Leave handler: accrual and balance computation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.payroll.service.leave import compute_leave

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario

_ZERO = Decimal(0)


@dataclass(frozen=True)
class _LeaveResult:
    accrued: Decimal
    taken: Decimal
    balance: Decimal
    present: bool


def _run_wr_leave(
    scenario: PayrollScenario,
    ccnl: CCNL,
) -> _LeaveResult:
    """Run the work-rules leave-accrual block.

    Returns:
        :class:`_LeaveResult` with zero day counters when no leave input is
        supplied.

    Raises:
        OutOfScopeError: If leave_input is supplied but the CCNL has no
            leave_rules schema.
        RuntimeError: If ``work_rules`` or ``leave_rules`` is ``None``
            despite ``present=True`` (indicates a data bug).
    """
    leave_input = scenario.leave_input
    present = ccnl.work_rules is not None and ccnl.work_rules.leave_rules is not None
    if leave_input is None:
        return _LeaveResult(accrued=_ZERO, taken=_ZERO, balance=_ZERO, present=present)
    if present:
        work_rules_lv = ccnl.work_rules
        if (  # pragma: no cover
            work_rules_lv is None or work_rules_lv.leave_rules is None
        ):
            msg = "leave_rules is None despite present=True"
            raise RuntimeError(msg)
        service_months = scenario.employee.seniority_months_as_of(
            scenario.employment.as_of
        )
        accrued, taken, balance = compute_leave(
            leave_input=leave_input,
            leave_rules=work_rules_lv.leave_rules,
            service_months=service_months,
        )
        return _LeaveResult(accrued=accrued, taken=taken, balance=balance, present=True)
    msg = "leave_input requested but not modelled for this CCNL"
    raise OutOfScopeError(msg, feature="leave", reason="no_schema")
