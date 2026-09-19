"""Absence handler: unpaid-day deduction computation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.payroll.service.absence import compute_absence_deduction
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario

_ZERO = Decimal(0)


@dataclass(frozen=True)
class _AbsenceResult:
    deduction: Decimal
    effective_gross: Decimal
    present: bool


def _run_wr_absence(
    scenario: PayrollScenario,
    ccnl: CCNL,
    gross_monthly: Decimal,
    hourly_rate: Decimal,
    wr_warnings: list[str],
) -> _AbsenceResult:
    """Run the work-rules absence-deduction block.

    Returns:
        :class:`_AbsenceResult` with zero deduction and
        ``effective_gross == gross_monthly`` when no absence is supplied or
        the CCNL has no absence rules.

    Raises:
        OutOfScopeError: If unpaid_days > 0 but the CCNL has no absence schema.
        RuntimeError: If ``work_rules`` or ``absence_rules`` is ``None``
            despite ``present=True`` (indicates a data bug).
    """
    absence_input = scenario.absence_days
    present = ccnl.work_rules is not None and ccnl.work_rules.absence_rules is not None
    deduction = _ZERO
    if absence_input is not None and absence_input.unpaid_days != _ZERO:
        if present:
            work_rules_ab = ccnl.work_rules
            if (  # pragma: no cover
                work_rules_ab is None or work_rules_ab.absence_rules is None
            ):
                msg = "absence_rules is None despite present=True"
                raise RuntimeError(msg)
            deduction = compute_absence_deduction(
                absence_input=absence_input,
                absence_rules=work_rules_ab.absence_rules,
                gross_monthly=gross_monthly,
                hourly_rate=hourly_rate,
            )
            if deduction > gross_monthly:
                wr_warnings.append(
                    "absence_deduction exceeds gross_monthly: capped to gross_monthly"
                )
                deduction = gross_monthly
        else:
            msg = "absence_days requested but not modelled for this CCNL"
            raise OutOfScopeError(msg, feature="absence", reason="no_schema")
    return _AbsenceResult(
        deduction=deduction,
        effective_gross=money(gross_monthly - deduction),
        present=present,
    )
