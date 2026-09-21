"""Period-first payroll calculation: single competence month.

The computation order is:
  1. Resolve gross from the CCNL salary table for the period date.
  2. Compute INPS contributions and TFR accrual on the period gross.
  3. Project annual taxable income and compute IRPEF via conguaglio YTD.
  4. Build pay items and ledger entries from the resolved amounts.
  5. Advance the YTD state.

This is a vertical slice: permanent employee, ordinary month, no overtime
or absences, no seniority increments beyond what _level_chain resolves.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    PayItem,
    TaxCreditItem,
    TfrAccrualItem,
)
from ccnl_engine.engine.payroll.service import irpef as irpef_svc
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.contributions import resolve_rates
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.engine.tax.domain.credit_rules import TrattamentoIntegrativoRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)
_PERMANENT = Permanent()


@dataclass(frozen=True)
class _PeriodAmounts:
    """All resolved monetary amounts for one pay period."""

    monthly_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: Decimal
    period_irpef: Decimal
    period_tratt: Decimal
    period_net: Decimal
    period_employer_cost: Decimal


def _as_of(period_id: PeriodId) -> date:
    """Return the first calendar day of the competence period.

    Returns:
        ``date(year, month, 1)`` for the given period.
    """
    return date(period_id.year, period_id.month, 1)


def _resolve_monthly_gross(ccnl: CCNL, level_code: str, as_of: date) -> Decimal:
    """Look up the full-time monthly gross from the CCNL salary table.

    Returns:
        Rounded monthly gross (base + seniority + allowances) in EUR.
    """
    level = ccnl.level_by_code(level_code)
    chain = _level_chain(ccnl, level, 0, frozenset(), as_of, is_apprentice=False)
    return money(chain.base + chain.seniority + chain.allowances_total)


def _trattamento_period(
    taxable: Decimal,
    irpef_gross: Decimal,
    work_ded: Decimal,
    ti_rules: TrattamentoIntegrativoRules | None,
    additional_months: int,
) -> Decimal:
    """Compute the period share of trattamento integrativo (Art. 1 D.L. 3/2020).

    Returns:
        Monthly trattamento amount, or zero if ``ti_rules`` is ``None``.
    """
    if ti_rules is None:
        return _ZERO
    annual = irpef_svc.trattamento_integrativo(
        taxable, irpef_gross, work_ded, work_ded, ti_rules
    )
    return money(annual / additional_months)


def _compute_amounts(
    monthly_gross: Decimal,
    opening: PeriodState,
    additional_months: int,
    rules: YearRules,
) -> _PeriodAmounts:
    """Resolve all monetary amounts for the period from gross and YTD state.

    Returns:
        A :class:`_PeriodAmounts` with all rounded monetary quantities.
    """
    rates = resolve_rates(rules, _PERMANENT, None)
    inps_employee = money(monthly_gross * rates.employee_rate)
    inps_employer = money(monthly_gross * rates.employer_rate)
    tfr = money(monthly_gross / rules.tfr.accrual_divisor)

    annual_gross = monthly_gross * additional_months
    taxable = annual_gross - money(annual_gross * rates.employee_rate)
    ig = irpef_svc.irpef_gross(taxable, rules)
    wd = irpef_svc.work_income_deduction(taxable, constants=rules.work_deduction)
    irpef_net_annual = ig - wd

    remaining = max(1, additional_months - opening.months_closed)
    period_irpef = money(
        max(_ZERO, (irpef_net_annual - opening.irpef_withheld_ytd) / remaining)
    )
    period_tratt = _trattamento_period(
        taxable, ig, wd, rules.trattamento_integrativo, additional_months
    )

    period_net = money(monthly_gross - inps_employee - period_irpef + period_tratt)
    period_employer_cost = money(monthly_gross + inps_employer + tfr)

    return _PeriodAmounts(
        monthly_gross=monthly_gross,
        inps_employee=inps_employee,
        inps_employer=inps_employer,
        tfr=tfr,
        period_irpef=period_irpef,
        period_tratt=period_tratt,
        period_net=period_net,
        period_employer_cost=period_employer_cost,
    )


def _make_entry(
    entry_id: str,
    pay_item_id: str,
    pay_item_kind: str,
    competence_period: CompetencePeriod,
    payment_date: date,
    account: AccountKind,
    amount: Decimal,
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=competence_period,
        payment_date=payment_date,
        pay_item_id=pay_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=amount,
        source_item_id=pay_item_id,
    )


def _build_pay_items(
    amounts: _PeriodAmounts,
    period_id: PeriodId,
    payment_date: date,
) -> tuple[PayItem, ...]:
    """Build the pay-item tuple from resolved period amounts.

    Returns:
        Tuple of :class:`~ccnl_engine.engine.payroll.domain.pay_items.PayItem`
        instances for this period (5 base items, plus TaxCreditItem when
        trattamento integrativo is positive).
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = f"{period_id.year}_{period_id.month:02d}"
    items: list[PayItem] = [
        BaseSalaryEarning(
            item_id=f"base_salary_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.monthly_gross,
        ),
        EmployeeWithholdingItem(
            item_id=f"inps_employee_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.inps_employee,
        ),
        EmployeeWithholdingItem(
            item_id=f"irpef_{tag}",
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=amounts.period_irpef,
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
    ]
    if amounts.period_tratt > _ZERO:
        items.append(
            TaxCreditItem(
                item_id=f"tratt_integ_{tag}",
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amounts.period_tratt,
            )
        )
    return tuple(items)


def _project_ledger(
    amounts: _PeriodAmounts,
    period_id: PeriodId,
    payment_date: date,
) -> tuple[LedgerEntry, ...]:
    """Project pay items to ledger entries.

    Returns:
        Tuple of :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`
        instances (5 base accounts, plus CREDITS when trattamento is positive).
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = f"{period_id.year}_{period_id.month:02d}"
    entries: list[LedgerEntry] = [
        _make_entry(
            f"cash_earnings_{tag}",
            f"base_salary_{tag}",
            "base_salary_earning",
            cp,
            payment_date,
            AccountKind.CASH_EARNINGS,
            amounts.monthly_gross,
        ),
        _make_entry(
            f"inps_employee_{tag}",
            f"inps_employee_{tag}",
            "employee_withholding_item",
            cp,
            payment_date,
            AccountKind.EMPLOYEE_CONTRIBUTIONS,
            amounts.inps_employee,
        ),
        _make_entry(
            f"irpef_{tag}",
            f"irpef_{tag}",
            "employee_withholding_item",
            cp,
            payment_date,
            AccountKind.ORDINARY_TAX,
            amounts.period_irpef,
        ),
        _make_entry(
            f"inps_employer_{tag}",
            f"inps_employer_{tag}",
            "employer_contribution_item",
            cp,
            payment_date,
            AccountKind.EMPLOYER_CONTRIBUTIONS,
            amounts.inps_employer,
        ),
        _make_entry(
            f"tfr_{tag}",
            f"tfr_{tag}",
            "tfr_accrual_item",
            cp,
            payment_date,
            AccountKind.TFR_ACCRUAL,
            amounts.tfr,
        ),
    ]
    if amounts.period_tratt > _ZERO:
        entries.append(
            _make_entry(
                f"tratt_integ_{tag}",
                f"tratt_integ_{tag}",
                "tax_credit_item",
                cp,
                payment_date,
                AccountKind.CREDITS,
                amounts.period_tratt,
            )
        )
    return tuple(entries)


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository | None = None,
) -> PeriodCalculationResult:
    """Compute payroll for one competence period using the period-first model.

    The period net is derived from pay items and a real IRPEF conguaglio:
    changing the YTD IRPEF withheld in ``opening_state`` changes the period
    net.  This is the key property that distinguishes this engine from the
    legacy annual-divide approach.

    Args:
        request: Period calculation input: CCNL, level, period, and YTD state.
        repo: Optional knowledge repository. Uses
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` when ``None``.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
        with gross, net, employer cost, closing YTD state, pay items and ledger.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    ccnl = effective_repo.load_ccnl(request.ccnl_slug)
    as_of = _as_of(request.period_id)
    year_rules = effective_repo.load_year_rules(
        request.period_id.year, ccnl.meta.tax_sector, request.num_employees
    )
    additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
    monthly_gross = _resolve_monthly_gross(ccnl, request.level_code, as_of)
    amounts = _compute_amounts(
        monthly_gross, request.opening_state, additional_months, year_rules
    )
    pay_items = _build_pay_items(amounts, request.period_id, request.payment_date)
    ledger_entries = _project_ledger(amounts, request.period_id, request.payment_date)
    closing = PeriodState(
        months_closed=request.opening_state.months_closed + 1,
        irpef_withheld_ytd=(
            request.opening_state.irpef_withheld_ytd + amounts.period_irpef
        ),
        inps_employee_ytd=(
            request.opening_state.inps_employee_ytd + amounts.inps_employee
        ),
        gross_ytd=request.opening_state.gross_ytd + monthly_gross,
    )
    return PeriodCalculationResult(
        period_id=request.period_id,
        payment_date=request.payment_date,
        period_gross=amounts.monthly_gross,
        period_net=amounts.period_net,
        period_employer_cost=amounts.period_employer_cost,
        closing_state=closing,
        pay_items=pay_items,
        ledger_entries=ledger_entries,
    )
