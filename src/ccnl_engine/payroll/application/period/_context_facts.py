"""Derived facts of a run: finality, conguaglio and gross of a pay chain.

Pure functions of the values a :class:`RunContext` holds, so the context
stays a plain immutable record.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.withholding._cap import ends_in_year
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.service.types import MonthlyPayChain

__all__ = ["chain_gross", "installment_run", "settles_tax_year"]


def installment_run(
    kind: RunKind,
    employment_period: EmploymentPeriod | None,
    fiscal_year: int,
    *,
    takes_last_slot: bool,
) -> InstallmentRun:
    """Return the run as the credit recoveries see it.

    The run is final when it is a termination run, or when the employment
    ends in the tax year and the run takes its last withholding slot: no
    later payslip can carry an installment.

    Returns:
        Whether the run is final and whether it is an adjustment.
    """
    final = kind is RunKind.TERMINATION or (
        ends_in_year(employment_period, fiscal_year) and takes_last_slot
    )
    return InstallmentRun(final=final, adjustment=kind is RunKind.ADJUSTMENT)


def settles_tax_year(
    run: InstallmentRun, kind: RunKind, *, takes_last_slot: bool
) -> bool:
    """Return whether the run settles the tax year (the conguaglio).

    Returns:
        ``True`` when the run takes the last withholding slot of the year
        or is the last run of the employment.
    """
    return run.final or (kind.consumes_withholding_slot and takes_last_slot)


def chain_gross(chain: MonthlyPayChain) -> Decimal:
    """Return the gross of a pay chain: base, seniority and allowances.

    Returns:
        The rounded gross.
    """
    return money(chain.base + chain.seniority + chain.allowances_total)
