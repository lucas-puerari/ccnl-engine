"""Build base pay items and project base ledger entries for a period."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FixedAllowanceEarning,
    PayItem,
    SeniorityEarning,
    TaxCreditItem,
    TaxRefundItem,
    TfrAccrualItem,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.service.types import MonthlyPayChain


def _build_pay_items(
    amounts: _PeriodAmounts,
    chain: MonthlyPayChain,
    period_id: PeriodId,
    payment_date: date,
    run_tag: str | None = None,
) -> tuple[PayItem, ...]:
    """Build the base pay-item tuple from resolved period amounts and chain.

    Returns:
        Tuple of :class:`~ccnl_engine.payroll.domain.pay_items.PayItem`
        instances for this period.
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = run_tag if run_tag is not None else f"{period_id.year}_{period_id.month:02d}"
    items: list[PayItem] = [
        BaseSalaryEarning(
            item_id=f"base_salary_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=chain.base,
        ),
    ]
    if chain.seniority > _ZERO:
        items.append(
            SeniorityEarning(
                item_id=f"seniority_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=chain.seniority,
            )
        )
    for allowance, amount in chain.allowances:
        if amount > _ZERO:
            items.append(
                FixedAllowanceEarning(
                    item_id=f"allowance_{allowance.code}_{tag}",
                    competence_period=cp,
                    payment_date=payment_date,
                    quantity=Decimal(1),
                    amount=amount,
                    allowance_code=allowance.code,
                )
            )
    items.extend([
        EmployeeWithholdingItem(
            item_id=f"inps_employee_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.inps_employee,
        ),
        EmployerContributionItem(
            item_id=f"inps_employer_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.inps_employer,
        ),
        TfrAccrualItem(
            item_id=f"tfr_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.tfr,
        ),
    ])
    if amounts.period_irpef > _ZERO:
        items.append(
            EmployeeWithholdingItem(
                item_id=f"irpef_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amounts.period_irpef,
            )
        )
    elif amounts.period_irpef < _ZERO:
        items.append(
            TaxRefundItem(
                item_id=f"irpef_refund_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=-amounts.period_irpef,
            )
        )
    if amounts.period_tratt != _ZERO:
        items.append(
            TaxCreditItem(
                item_id=f"tratt_integ_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amounts.period_tratt,
            )
        )
    if amounts.period_surtax > _ZERO:
        items.append(
            EmployeeWithholdingItem(
                item_id=f"surtax_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amounts.period_surtax,
            )
        )
    return tuple(items)


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
        Tuple of :class:`~ccnl_engine.payroll.domain.ledger.LedgerEntry`
        instances.
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = run_tag if run_tag is not None else f"{period_id.year}_{period_id.month:02d}"
    ordinary_pid = _require_resolution(
        resolver, "base_salary_earning", context
    ).policy_id
    emp_pid = _require_resolution(
        resolver, "employee_withholding_item", context
    ).policy_id
    er_pid = _require_resolution(
        resolver, "employer_contribution_item", context
    ).policy_id
    tfr_pid = _require_resolution(resolver, "tfr_accrual_item", context).policy_id
    entries: list[LedgerEntry] = [
        _make_entry(
            f"cash_earnings_{tag}",
            f"base_salary_{tag}",
            "base_salary_earning",
            cp,
            payment_date,
            AccountKind.CASH_EARNINGS,
            chain.base,
            policy_id=ordinary_pid,
        ),
    ]
    if chain.seniority > _ZERO:
        seniority_pid = _require_resolution(
            resolver, "seniority_earning", context
        ).policy_id
        entries.append(
            _make_entry(
                f"seniority_{tag}",
                f"seniority_{tag}",
                "seniority_earning",
                cp,
                payment_date,
                AccountKind.CASH_EARNINGS,
                chain.seniority,
                policy_id=seniority_pid,
            )
        )
    for allowance, amount in chain.allowances:
        if amount > _ZERO:
            allowance_pid = _require_resolution(
                resolver, "fixed_allowance_earning", context
            ).policy_id
            entries.append(
                _make_entry(
                    f"allowance_{allowance.code}_{tag}",
                    f"allowance_{allowance.code}_{tag}",
                    "fixed_allowance_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    amount,
                    policy_id=allowance_pid,
                )
            )
    entries.extend([
        _make_entry(
            f"inps_employee_{tag}",
            f"inps_employee_{tag}",
            "employee_withholding_item",
            cp,
            payment_date,
            AccountKind.EMPLOYEE_CONTRIBUTIONS,
            amounts.inps_employee,
            policy_id=emp_pid,
        ),
        _make_entry(
            f"inps_employer_{tag}",
            f"inps_employer_{tag}",
            "employer_contribution_item",
            cp,
            payment_date,
            AccountKind.EMPLOYER_CONTRIBUTIONS,
            amounts.inps_employer,
            policy_id=er_pid,
        ),
        _make_entry(
            f"tfr_{tag}",
            f"tfr_{tag}",
            "tfr_accrual_item",
            cp,
            payment_date,
            AccountKind.TFR_ACCRUAL,
            amounts.tfr,
            policy_id=tfr_pid,
        ),
    ])
    if amounts.period_irpef > _ZERO:
        entries.append(
            _make_entry(
                f"irpef_{tag}",
                f"irpef_{tag}",
                "employee_withholding_item",
                cp,
                payment_date,
                AccountKind.ORDINARY_TAX,
                amounts.period_irpef,
                policy_id=emp_pid,
            )
        )
    elif amounts.period_irpef < _ZERO:
        refund_pid = _require_resolution(resolver, "tax_refund_item", context).policy_id
        entries.append(
            _make_entry(
                f"irpef_refund_{tag}",
                f"irpef_refund_{tag}",
                "tax_refund_item",
                cp,
                payment_date,
                AccountKind.CREDITS,
                -amounts.period_irpef,
                policy_id=refund_pid,
            )
        )
    if amounts.period_tratt != _ZERO:
        credit_pid = _require_resolution(resolver, "tax_credit_item", context).policy_id
        entries.append(
            _make_entry(
                f"tratt_integ_{tag}",
                f"tratt_integ_{tag}",
                "tax_credit_item",
                cp,
                payment_date,
                AccountKind.CREDITS,
                amounts.period_tratt,
                policy_id=credit_pid,
            )
        )
    if amounts.period_surtax > _ZERO:
        entries.append(
            _make_entry(
                f"surtax_{tag}",
                f"surtax_{tag}",
                "employee_withholding_item",
                cp,
                payment_date,
                AccountKind.SURTAX,
                amounts.period_surtax,
                policy_id=emp_pid,
            )
        )
    if amounts.period_substitute_tax > _ZERO:
        prod_pid = _require_resolution(
            resolver, "productivity_bonus_earning", context
        ).policy_id
        entries.append(
            _make_entry(
                f"substitute_tax_{tag}",
                f"substitute_tax_{tag}",
                "productivity_bonus_earning",
                cp,
                payment_date,
                AccountKind.SUBSTITUTE_TAX,
                amounts.period_substitute_tax,
                policy_id=prod_pid,
            )
        )
    return tuple(entries)
