"""Shared types for reconciliation invariant sub-modules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__ = ["InvariantCode", "ReconciliationViolation", "RunFacts"]

_ZERO = Decimal(0)


class InvariantCode(StrEnum):
    """Stable identifier of each reconciliation invariant.

    The value appears in :attr:`ReconciliationViolation.invariant_id` and in
    the message of the ``DataIntegrityError`` raised when a run breaks it.
    """

    PAY_ITEM_POSTED = "pay_item_posted"
    EARNING_CONTRIBUTION_EXCLUSIVE = "earning_contribution_exclusive"
    NET_IDENTITY = "net_identity"
    EMPLOYER_COST_IDENTITY = "employer_cost_identity"
    GROSS_IDENTITY = "gross_identity"
    LEDGER_ENTRY_UNIQUE = "ledger_entry_unique"
    GROSS_NON_NEGATIVE = "gross_non_negative"
    EMPLOYEE_DEDUCTION_NON_NEGATIVE = "employee_deduction_non_negative"
    SUBSTITUTE_TAX_NON_NEGATIVE = "substitute_tax_non_negative"
    ORDINARY_TAX_NON_NEGATIVE = "ordinary_tax_non_negative"
    EMPLOYEE_CONTRIBUTION_NON_NEGATIVE = "employee_contribution_non_negative"
    EMPLOYER_CONTRIBUTION_NON_NEGATIVE = "employer_contribution_non_negative"
    NET_PAY_NON_NEGATIVE = "net_pay_non_negative"
    RUN_COUNTERS_ADVANCE = "run_counters_advance"
    YTD_CONTINUITY = "ytd_continuity"
    IRPEF_WITHHELD_CONTINUITY = "irpef_withheld_continuity"
    CREDIT_RECOVERY_BOUNDS = "credit_recovery_bounds"
    CARRIED_RECOVERY_ADVANCE = "carried_recovery_advance"
    SUBSTITUTE_TAX_PLAFOND = "substitute_tax_plafond"
    SUBSTITUTE_TAX_ELIGIBILITY = "substitute_tax_eligibility"
    DECISION_PROVENANCE = "decision_provenance"
    RUN_WITHIN_EMPLOYMENT = "run_within_employment"
    EXTRA_MONTH_ACCRUAL_LIMIT = "extra_month_accrual_limit"
    CONTRIBUTION_CEILING = "contribution_ceiling"
    IRPEF_ANNUAL_RECONCILIATION = "irpef_annual_reconciliation"


@dataclass(frozen=True)
class ReconciliationViolation:
    """One failed invariant check.

    Attributes:
        invariant_id: Code of the invariant that failed, one of
            :class:`InvariantCode` (e.g. ``"net_identity"``).
        message: Human-readable description of the failure.
        expected: The value the invariant expected, when applicable.
        actual: The value that was observed, when applicable.
    """

    invariant_id: str
    message: str
    expected: Decimal | None = None
    actual: Decimal | None = None


@dataclass(frozen=True)
class RunFacts:
    """Facts of the run that the result does not carry.

    The invariants that need them are skipped when a fact is not given,
    so :func:`~ccnl_engine.payroll.application.reconcile.reconcile` can
    check a result on its own.

    Attributes:
        employment_period: Employment of the worker, ``None`` when not
            tracked.
        ivs_ceiling: IVS massimale of the tax year when the ceiling applies
            to the worker, otherwise ``None``.
        pdr_cap: Annual limit of the PdR substitute tax, ``None`` when not
            known.
        accruals: Extra-month ratei paid on the run: the rateo of an
            extra-month run and the ratei settled at termination.
        projected_taxable: Annual taxable income the IRPEF of the run was
            computed on, ``None`` when not known.
    """

    employment_period: EmploymentPeriod | None = None
    ivs_ceiling: Decimal | None = None
    pdr_cap: Decimal | None = None
    accruals: tuple[ExtraMonthAccrual, ...] = ()
    projected_taxable: Decimal | None = None


def _sum_account(
    result: PeriodResult,
    account: AccountKind,
) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total amount for ``account`` in ``result.ledger_entries``, or zero
        when no entries for that account are present.
    """
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )
