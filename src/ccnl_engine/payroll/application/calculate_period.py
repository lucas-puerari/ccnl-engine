"""Period-first payroll calculation: single competence month.

The computation order is:
  1. Process variable work events into aggregated totals.
  2. Resolve gross from the CCNL salary table for the period date.
  3. Compute INPS contributions and TFR accrual on the augmented bases.
  4. Project annual taxable income and compute IRPEF via conguaglio YTD.
  5. Build pay items and ledger entries from the resolved amounts.
  6. Advance the YTD state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.capability_catalog import CapabilityReport
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ContractRenewalArrears,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FringeBenefitItem,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    SicknessItem,
    TaxCreditItem,
    TfrAccrualItem,
    TfrSettlementItem,
    WelfareItem,
)
from ccnl_engine.engine.payroll.service import irpef as irpef_svc
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.contributions import resolve_rates
from ccnl_engine.engine.payroll.service.family_deductions import (
    compute_family_deductions,
)
from ccnl_engine.engine.payroll.service.fiscal_surtax import _compute_addizionali
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.tax.service.loaders import load_family_deduction_rules
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.credit_rules import TrattamentoIntegrativoRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)
_PERMANENT = Permanent()

_OBSERVED: dict[str, str] = {
    "base_salary": "computed",
    "seniority": "computed",
    "inps_employee": "computed",
    "inps_employer": "computed",
    "tfr": "computed",
    "irpef": "computed",
    "trattamento_integrativo": "computed",
    "ulteriore_detrazione_lavoro": "computed",
    "addizionale_regionale": "computed",
    "addizionale_comunale": "computed",
    "family_deductions": "computed",
    "overtime": "computed",
    "night_work": "computed",
    "holiday_work": "computed",
    "absence": "computed",
    "leave": "computed",
    "sickness": "computed",
    "fringe_benefit": "computed",
    "welfare": "computed",
    "bonus_pdr": "computed",
    "contract_renewal_arrears": "computed",
    "bilateral_funds": "computed",
    "termination_tfr": "computed",
}


@dataclass(frozen=True)
class _EventTotals:
    """Aggregated event amounts for the period."""

    gross: Decimal
    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal
    separate_tax: Decimal
    employee_deductions: Decimal
    employer_additional: Decimal
    tfr_settlement: Decimal

    @classmethod
    def zero(cls) -> _EventTotals:
        """Return a zero-valued totals object.

        Returns:
            An :class:`_EventTotals` with all fields at zero.
        """
        return cls(
            gross=_ZERO,
            inps_base=_ZERO,
            tfr_base=_ZERO,
            irpef_base=_ZERO,
            separate_tax=_ZERO,
            employee_deductions=_ZERO,
            employer_additional=_ZERO,
            tfr_settlement=_ZERO,
        )


@dataclass(frozen=True)
class _PeriodAmounts:
    """All resolved monetary amounts for one pay period."""

    monthly_gross: Decimal
    period_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: Decimal
    period_irpef: Decimal
    period_tratt: Decimal
    period_surtax: Decimal
    period_separate_tax: Decimal
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
    event_totals: _EventTotals,
    opening: PeriodState,
    additional_months: int,
    rules: YearRules,
    surtax_rules: SurtaxRules | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    family_deduction_rules: FamilyDeductionRules | None = None,
) -> _PeriodAmounts:
    """Resolve all monetary amounts for the period from gross, events and YTD state.

    Returns:
        A :class:`_PeriodAmounts` with all rounded monetary quantities.
    """
    rates = resolve_rates(rules, _PERMANENT, None)

    # INPS: base salary + event INPS-liable amounts
    period_inps_base = monthly_gross + event_totals.inps_base
    inps_employee = money(period_inps_base * rates.employee_rate)
    inps_employer = money(period_inps_base * rates.employer_rate)

    # TFR: base salary + event TFR-liable amounts
    period_tfr_base = monthly_gross + event_totals.tfr_base
    tfr = money(period_tfr_base / rules.tfr.accrual_divisor)

    # IRPEF: recurring base projected annually + event IRPEF-liable amounts (one-off)
    recurring_annual = monthly_gross * additional_months
    recurring_inps_annual = money(recurring_annual * rates.employee_rate)
    recurring_taxable = recurring_annual - recurring_inps_annual
    event_inps_on_irpef = money(event_totals.inps_base * rates.employee_rate)
    event_taxable = event_totals.irpef_base - event_inps_on_irpef
    taxable = recurring_taxable + event_taxable

    ig = irpef_svc.irpef_gross(taxable, rules)
    wd = irpef_svc.work_income_deduction(taxable, constants=rules.work_deduction)

    # Family deductions reduce annual IRPEF
    if family_composition is not None and family_deduction_rules is not None:
        _, _, _, fam_ded = compute_family_deductions(
            family_composition, taxable, family_deduction_rules
        )
    else:
        fam_ded = _ZERO
    irpef_net_annual = max(_ZERO, ig - wd - fam_ded)

    remaining = max(1, additional_months - opening.months_closed)
    period_irpef = money(
        max(_ZERO, (irpef_net_annual - opening.irpef_withheld_ytd) / remaining)
    )
    period_tratt = _trattamento_period(
        taxable, ig, wd, rules.trattamento_integrativo, additional_months
    )

    # Addizionali regionale e comunale (SURTAX account, not ORDINARY_TAX)
    surtax_reg, surtax_com, _, _, _ = _compute_addizionali(
        taxable,
        surtax_rules,
        frozenset(),
        regione=regione,
        comune_belfiore=comune_belfiore,
        irpef_due=ig,
    )
    period_surtax_annual = surtax_reg + surtax_com
    period_surtax = money(period_surtax_annual / additional_months)

    period_gross = monthly_gross + event_totals.gross
    period_separate_tax = event_totals.separate_tax
    period_net = money(
        period_gross
        + event_totals.tfr_settlement
        - inps_employee
        - event_totals.employee_deductions
        - period_irpef
        + period_tratt
        - period_surtax
        - period_separate_tax
    )
    period_employer_cost = money(
        period_gross + inps_employer + event_totals.employer_additional + tfr
    )

    return _PeriodAmounts(
        monthly_gross=monthly_gross,
        period_gross=period_gross,
        inps_employee=inps_employee,
        inps_employer=inps_employer,
        tfr=tfr,
        period_irpef=period_irpef,
        period_tratt=period_tratt,
        period_surtax=period_surtax,
        period_separate_tax=period_separate_tax,
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


def _fringe_bases(event: FringeEvent) -> tuple[Decimal, Decimal]:
    """Return (inps_base, irpef_base) for a fringe benefit event.

    Returns:
        ``(gross, gross)`` when ``amount`` exceeds the exempt threshold;
        ``(_ZERO, _ZERO)`` otherwise.
    """
    gross = event.amount
    if gross <= event.exempt_threshold:
        return _ZERO, _ZERO
    return gross, gross


def _process_events(
    events: tuple[WorkEvent, ...],
    cp: CompetencePeriod,
    payment_date: date,
    tag: str,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    Most events produce one pay item and one CASH_EARNINGS entry.
    BilateralFundEvent produces two items (employee + employer) and two entries.
    ArrearsEvent and TerminationTFREvent each produce an additional SEPARATE_TAX entry.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    total_gross = _ZERO
    total_inps = _ZERO
    total_tfr = _ZERO
    total_irpef = _ZERO
    total_separate_tax = _ZERO
    total_employee_ded = _ZERO
    total_employer_add = _ZERO
    total_tfr_settlement = _ZERO
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []

    for i, event in enumerate(events):
        evt_id = f"{tag}_evt{i}"

        if isinstance(event, OvertimeEvent):
            gross = money(event.hours * event.hourly_rate * event.multiplier)
            item: PayItem = OvertimeEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
            )
            total_gross += gross
            total_inps += gross
            total_tfr += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "overtime_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, NightShiftEvent):
            gross = event.supplement_amount
            item = NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            total_inps += gross
            total_tfr += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "night_holiday_shift_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, HolidayWorkEvent):
            gross = event.supplement_amount
            item = NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            total_inps += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "night_holiday_shift_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, AbsenceEvent):
            gross = -money(event.hours * event.hourly_rate)
            item = AbsenceDeduction(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
                absence_days=event.hours / Decimal(8),
            )
            total_gross += gross
            total_inps += gross
            total_tfr += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "absence_deduction",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, SickLeaveEvent):
            gross = event.amount
            item = SicknessItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
                sick_days=Decimal(1),
            )
            total_gross += gross
            total_inps += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "sickness_item",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, BonusEvent):
            gross = event.amount
            item = BonusEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            total_inps += gross
            total_tfr += gross
            total_irpef += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "bonus_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, FringeEvent):
            gross = event.amount
            fringe_inps, fringe_irpef = _fringe_bases(event)
            item = FringeBenefitItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            total_inps += fringe_inps
            total_irpef += fringe_irpef
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "fringe_benefit_item",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, WelfareEvent):
            gross = event.amount
            item = WelfareItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            items.append(item)
            entries.append(
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "welfare_item",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                )
            )
        elif isinstance(event, ArrearsEvent):
            gross = event.amount
            sep_tax = money(gross * event.separate_tax_rate)
            item = ContractRenewalArrears(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_gross += gross
            total_separate_tax += sep_tax
            items.append(item)
            entries.extend([
                _make_entry(
                    f"cash_{evt_id}",
                    evt_id,
                    "contract_renewal_arrears",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    gross,
                ),
                _make_entry(
                    f"sep_tax_{evt_id}",
                    evt_id,
                    "contract_renewal_arrears",
                    cp,
                    payment_date,
                    AccountKind.SEPARATE_TAX,
                    sep_tax,
                ),
            ])
        elif isinstance(event, BilateralFundEvent):
            emp_id = f"{evt_id}_emp"
            er_id = f"{evt_id}_er"
            emp_item = EmployeeWithholdingItem(
                item_id=emp_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=event.employee_amount,
            )
            er_item = EmployerContributionItem(
                item_id=er_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=event.employer_amount,
            )
            total_employee_ded += event.employee_amount
            total_employer_add += event.employer_amount
            items.extend((emp_item, er_item))
            entries.extend([
                _make_entry(
                    f"bilat_emp_{evt_id}",
                    emp_id,
                    "employee_withholding_item",
                    cp,
                    payment_date,
                    AccountKind.EMPLOYEE_CONTRIBUTIONS,
                    event.employee_amount,
                ),
                _make_entry(
                    f"bilat_er_{evt_id}",
                    er_id,
                    "employer_contribution_item",
                    cp,
                    payment_date,
                    AccountKind.EMPLOYER_CONTRIBUTIONS,
                    event.employer_amount,
                ),
            ])
        else:
            gross = event.amount  # TerminationTFREvent
            sep_tax = money(gross * event.separate_tax_rate)
            item = TfrSettlementItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            total_tfr_settlement += gross
            total_separate_tax += sep_tax
            items.append(item)
            entries.extend([
                _make_entry(
                    f"tfr_settle_{evt_id}",
                    evt_id,
                    "tfr_settlement_item",
                    cp,
                    payment_date,
                    AccountKind.TFR_SETTLEMENT,
                    gross,
                ),
                _make_entry(
                    f"sep_tax_{evt_id}",
                    evt_id,
                    "tfr_settlement_item",
                    cp,
                    payment_date,
                    AccountKind.SEPARATE_TAX,
                    sep_tax,
                ),
            ])

    return (
        _EventTotals(
            gross=total_gross,
            inps_base=total_inps,
            tfr_base=total_tfr,
            irpef_base=total_irpef,
            separate_tax=total_separate_tax,
            employee_deductions=total_employee_ded,
            employer_additional=total_employer_add,
            tfr_settlement=total_tfr_settlement,
        ),
        tuple(items),
        tuple(entries),
    )


def _build_pay_items(
    amounts: _PeriodAmounts,
    period_id: PeriodId,
    payment_date: date,
) -> tuple[PayItem, ...]:
    """Build the base pay-item tuple from resolved period amounts.

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
    period_id: PeriodId,
    payment_date: date,
) -> tuple[LedgerEntry, ...]:
    """Project base pay items to ledger entries.

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
            )
        )
    return tuple(entries)


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository | None = None,
) -> PeriodCalculationResult:
    """Compute payroll for one competence period using the period-first model.

    Variable work events (overtime, absences, bonuses, etc.) supplied on the
    request are processed first: their gross, INPS, TFR and IRPEF bases are
    aggregated and feed into the full period computation.  Each event produces
    its own pay item and CASH_EARNINGS ledger entry.

    Args:
        request: Period calculation input: CCNL, level, period, YTD state and
            optional variable events.
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
    period_year = request.period_id.year
    year_rules = effective_repo.load_year_rules(
        period_year, ccnl.meta.tax_sector, request.num_employees
    )
    catalog = effective_repo.load_capability_catalog(period_year)
    capability_gaps = catalog.gaps(_OBSERVED, detect_absent=True, year=period_year)
    capability_report = CapabilityReport(catalog_year=period_year, gaps=capability_gaps)
    additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
    monthly_gross = _resolve_monthly_gross(ccnl, request.level_code, as_of)

    cp = CompetencePeriod(year=request.period_id.year, month=request.period_id.month)
    tag = f"{period_year}_{request.period_id.month:02d}"
    event_totals, event_items, event_entries = _process_events(
        request.events, cp, request.payment_date, tag
    )

    needs_surtax = request.regione is not None or request.comune_belfiore is not None
    surtax_rules = (
        effective_repo.load_surtax_rules(period_year) if needs_surtax else None
    )
    fam_ded_rules = (
        load_family_deduction_rules(period_year)
        if request.family_composition is not None
        else None
    )
    amounts = _compute_amounts(
        monthly_gross,
        event_totals,
        request.opening_state,
        additional_months,
        year_rules,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=fam_ded_rules,
    )
    pay_items = _build_pay_items(amounts, request.period_id, request.payment_date)
    ledger_entries = _project_ledger(amounts, request.period_id, request.payment_date)
    closing = PeriodState(
        months_closed=request.opening_state.months_closed + 1,
        irpef_withheld_ytd=(
            request.opening_state.irpef_withheld_ytd + amounts.period_irpef
        ),
        inps_employee_ytd=(
            request.opening_state.inps_employee_ytd
            + amounts.inps_employee
            + event_totals.employee_deductions
        ),
        gross_ytd=request.opening_state.gross_ytd + amounts.period_gross,
    )
    return PeriodCalculationResult(
        period_id=request.period_id,
        payment_date=request.payment_date,
        period_gross=amounts.period_gross,
        period_net=amounts.period_net,
        period_employer_cost=amounts.period_employer_cost,
        closing_state=closing,
        pay_items=pay_items + event_items,
        ledger_entries=ledger_entries + event_entries,
        capability_report=capability_report,
    )
