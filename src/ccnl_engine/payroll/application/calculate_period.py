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
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FringeBenefitItem,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    SicknessItem,
    TaxCreditItem,
    TfrAccrualItem,
    WelfareItem,
)
from ccnl_engine.engine.payroll.service import irpef as irpef_svc
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.contributions import resolve_rates
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
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
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.engine.tax.domain.credit_rules import TrattamentoIntegrativoRules
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
}


@dataclass(frozen=True)
class _EventTotals:
    """Aggregated event amounts for the period."""

    gross: Decimal
    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal

    @classmethod
    def zero(cls) -> _EventTotals:
        """Return a zero-valued totals object.

        Returns:
            An :class:`_EventTotals` with all fields at zero.
        """
        return cls(gross=_ZERO, inps_base=_ZERO, tfr_base=_ZERO, irpef_base=_ZERO)


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
    irpef_net_annual = ig - wd

    remaining = max(1, additional_months - opening.months_closed)
    period_irpef = money(
        max(_ZERO, (irpef_net_annual - opening.irpef_withheld_ytd) / remaining)
    )
    period_tratt = _trattamento_period(
        taxable, ig, wd, rules.trattamento_integrativo, additional_months
    )

    period_gross = monthly_gross + event_totals.gross
    period_net = money(period_gross - inps_employee - period_irpef + period_tratt)
    period_employer_cost = money(period_gross + inps_employer + tfr)

    return _PeriodAmounts(
        monthly_gross=monthly_gross,
        period_gross=period_gross,
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


def _process_events(
    events: tuple[WorkEvent, ...],
    cp: CompetencePeriod,
    payment_date: date,
    tag: str,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    Each event produces exactly one pay item and one CASH_EARNINGS ledger entry.
    The returned :class:`_EventTotals` carries the aggregated gross, INPS base,
    TFR base and IRPEF base used by :func:`_compute_amounts`.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    total_gross = _ZERO
    total_inps = _ZERO
    total_tfr = _ZERO
    total_irpef = _ZERO
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []

    for i, event in enumerate(events):
        evt_id = f"{tag}_evt{i}"
        gross: Decimal
        inps: Decimal
        evt_tfr: Decimal
        irpef: Decimal
        item: PayItem
        kind: str

        if isinstance(event, OvertimeEvent):
            gross = money(event.hours * event.hourly_rate * event.multiplier)
            inps = gross
            evt_tfr = gross
            irpef = gross
            item = OvertimeEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
            )
            kind = "overtime_earning"
        elif isinstance(event, NightShiftEvent):
            gross = event.supplement_amount
            inps = gross
            evt_tfr = gross
            irpef = gross
            item = NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            kind = "night_holiday_shift_earning"
        elif isinstance(event, HolidayWorkEvent):
            gross = event.supplement_amount
            inps = gross
            evt_tfr = _ZERO
            irpef = gross
            item = NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            kind = "night_holiday_shift_earning"
        elif isinstance(event, AbsenceEvent):
            gross = -money(event.hours * event.hourly_rate)
            inps = gross
            evt_tfr = gross
            irpef = gross
            item = AbsenceDeduction(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
                absence_days=event.hours / Decimal(8),
            )
            kind = "absence_deduction"
        elif isinstance(event, SickLeaveEvent):
            gross = event.amount
            inps = gross
            evt_tfr = _ZERO
            irpef = gross
            item = SicknessItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
                sick_days=Decimal(1),
            )
            kind = "sickness_item"
        elif isinstance(event, BonusEvent):
            gross = event.amount
            inps = gross
            evt_tfr = gross
            irpef = gross
            item = BonusEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            kind = "bonus_earning"
        elif isinstance(event, FringeEvent):
            gross = event.amount
            if gross > event.exempt_threshold:
                inps = gross
                irpef = gross
            else:
                inps = _ZERO
                irpef = _ZERO
            evt_tfr = _ZERO
            item = FringeBenefitItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            kind = "fringe_benefit_item"
        else:
            gross = event.amount  # WelfareEvent
            inps = _ZERO
            evt_tfr = _ZERO
            irpef = _ZERO
            item = WelfareItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
            kind = "welfare_item"

        total_gross += gross
        total_inps += inps
        total_tfr += evt_tfr
        total_irpef += irpef
        items.append(item)
        entries.append(
            _make_entry(
                f"cash_{evt_id}",
                evt_id,
                kind,
                cp,
                payment_date,
                AccountKind.CASH_EARNINGS,
                gross,
            )
        )

    return (
        _EventTotals(
            gross=total_gross,
            inps_base=total_inps,
            tfr_base=total_tfr,
            irpef_base=total_irpef,
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

    amounts = _compute_amounts(
        monthly_gross,
        event_totals,
        request.opening_state,
        additional_months,
        year_rules,
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
