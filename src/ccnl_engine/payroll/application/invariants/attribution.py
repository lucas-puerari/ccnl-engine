"""Attribution invariant: every posted amount rests on a decision.

Implemented invariant:
    amount_has_decision: each non-zero ledger entry maps to the catalog
        capabilities that can post it, and the run took a decision of at
        least one of them.  An earnings, benefit or deduction entry maps by
        its pay-item kind (an overtime earning to ``overtime``); any other
        entry maps by its account (``ORDINARY_TAX`` to ``irpef``, the
        withholding shortfall and its deferral).  An entry whose kind or
        account has no mapping is a violation too: a new posting must name
        the capability that decides it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.invariants._types import (
    InvariantCode,
    ReconciliationViolation,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__ = [
    "ACCOUNT_CAPABILITIES",
    "KIND_ACCOUNTS",
    "KIND_CAPABILITIES",
    "check_amount_has_decision",
    "entry_capabilities",
]

_ZERO = Decimal(0)
_CREDITS = frozenset({"trattamento_integrativo", "somma_esente"})
#: The surtax of the run, or the surtax an earlier run carried for lack of
#: pay, which the withholding cap decides.
_SURTAX = frozenset({
    "addizionale_regionale",
    "addizionale_comunale",
    "withholding_shortfall",
})
_WORK_TIME = frozenset({"night_work", "holiday_work", "shift_work"})

#: Accounts whose entries map by pay-item kind.
KIND_ACCOUNTS = frozenset({
    AccountKind.CASH_EARNINGS,
    AccountKind.NON_CASH_BENEFITS,
    AccountKind.EMPLOYEE_DEDUCTIONS,
})

#: Capabilities that post an earnings, benefit or deduction pay-item kind.
KIND_CAPABILITIES: dict[str, frozenset[str]] = {
    "base_salary_earning": frozenset({"base_salary"}),
    "fixed_allowance_earning": frozenset({"base_salary"}),
    "extra_month_earning": frozenset({"base_salary"}),
    "seniority_earning": frozenset({"seniority"}),
    "overtime_earning": frozenset({"overtime"}),
    "night_holiday_shift_earning": _WORK_TIME,
    "bonus_earning": frozenset({"bonus"}),
    "productivity_bonus_earning": frozenset({"bonus"}),
    "contract_renewal_earning": frozenset({"bonus"}),
    "contract_renewal_arrears": frozenset({"contract_renewal_arrears"}),
    "sickness_item": frozenset({"sickness"}),
    "sickness_inps_item": frozenset({"sickness"}),
    "absence_deduction": frozenset({"absence", "sickness"}),
    "fringe_benefit_item": frozenset({"fringe_benefit"}),
    "welfare_item": frozenset({"welfare"}),
}

#: Capabilities that post to every other account.
ACCOUNT_CAPABILITIES: dict[AccountKind, frozenset[str]] = {
    AccountKind.EMPLOYEE_CONTRIBUTIONS: frozenset({"inps_employee"}),
    AccountKind.EMPLOYER_CONTRIBUTIONS: frozenset({
        "inps_employer",
        "pension_fund_contribution",
    }),
    AccountKind.BILATERAL_FUND_EMPLOYEE: frozenset({"bilateral_funds"}),
    AccountKind.BILATERAL_FUND_EMPLOYER: frozenset({"bilateral_funds"}),
    AccountKind.ORDINARY_TAX: frozenset({
        "irpef",
        "withholding_shortfall",
        "shortfall_deferral",
    }),
    AccountKind.TAX_REFUNDS: frozenset({"irpef"}),
    AccountKind.SUBSTITUTE_TAX: frozenset({
        "bonus_pdr",
        "rinnovo_substitute_tax",
        "notte_festivi_turni_substitute_tax",
    }),
    AccountKind.SEPARATE_TAX: frozenset({
        "contract_renewal_arrears",
        "termination_tfr",
    }),
    AccountKind.SURTAX: _SURTAX,
    AccountKind.SURTAX_REFUNDS: _SURTAX,
    AccountKind.CREDITS: _CREDITS,
    AccountKind.CREDIT_RECOVERIES: _CREDITS | {"ulteriore_detrazione_lavoro"},
    AccountKind.CREDIT_RECOVERY_SHORTFALL: _CREDITS
    | {"ulteriore_detrazione_lavoro", "withholding_shortfall"},
    AccountKind.TFR_ACCRUAL: frozenset({"tfr"}),
    AccountKind.PENSION_FUND_TFR: frozenset({"tfr"}),
    AccountKind.TFR_TREASURY_FUND: frozenset({"tfr"}),
    AccountKind.TFR_SETTLEMENT: frozenset({"termination_tfr"}),
    AccountKind.PENSION_FUND_EMPLOYEE: frozenset({"pension_fund_contribution"}),
    AccountKind.PENSION_FUND_EMPLOYER: frozenset({"pension_fund_contribution"}),
}


def entry_capabilities(entry: LedgerEntry) -> frozenset[str]:
    """Return the capabilities that can post ``entry``.

    Returns:
        The capabilities of its pay-item kind on an earnings, benefit or
        deduction account, of its account otherwise; empty when unmapped.
    """
    if entry.account in KIND_ACCOUNTS:
        return KIND_CAPABILITIES.get(entry.pay_item_kind, frozenset())
    return ACCOUNT_CAPABILITIES.get(entry.account, frozenset())


def check_amount_has_decision(result: PeriodResult) -> list[ReconciliationViolation]:
    """Check that every non-zero entry is attributable to a decision.

    Returns:
        One violation per non-zero entry whose capabilities took no
        decision in the run, or that maps to no capability.
    """
    decided = {d.capability for d in result.decisions}
    violations: list[ReconciliationViolation] = []
    for entry in result.ledger_entries:
        if entry.amount == _ZERO:
            continue
        capabilities = entry_capabilities(entry)
        if capabilities & decided:
            continue
        expected = ", ".join(sorted(capabilities)) or "no mapped capability"
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.AMOUNT_HAS_DECISION,
                message=(
                    f"entry {entry.entry_id} ({entry.account.value}, "
                    f"{entry.pay_item_kind}) has no decision of {expected}"
                ),
                actual=entry.amount,
            )
        )
    return violations
