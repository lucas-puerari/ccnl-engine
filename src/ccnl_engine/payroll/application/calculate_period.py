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
from typing import TYPE_CHECKING, assert_never

from ccnl_engine.engine.capability_catalog import CapabilityReport
from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ContractRenewalArrears,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FixedAllowanceEarning,
    FringeBenefitItem,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    SeniorityEarning,
    SicknessItem,
    TaxCreditItem,
    TfrAccrualItem,
    TfrSettlementItem,
    WelfareItem,
)
from ccnl_engine.engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.contributions import (
    resolve_contributions,
    resolve_rates,
)
from ccnl_engine.engine.payroll.service.family_deductions import (
    compute_family_deductions,
)
from ccnl_engine.engine.payroll.service.fiscal_surtax import _compute_addizionali
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.tax_computation import resolve_tax_computation
from ccnl_engine.engine.payroll.service.types import MonthlyPayChain  # noqa: TC001
from ccnl_engine.engine.tax.service.loaders import load_family_deduction_rules
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,  # noqa: TC001
)
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
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
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.tax import TaxComputation  # noqa: TC001
from ccnl_engine.payroll.domain.treatment import EventTreatment

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.contract.domain.compensation import Level
    from ccnl_engine.engine.contract.domain.seniority import LevelCategory
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)

# Treatment policy: maps each standard event type to the axes its gross contributes to.
# Fringe, Arrears, BilateralFund and TerminationTFR are not listed here because their
# axis amounts are computed differently from the event gross (threshold logic, separate-
# tax entries, or non-cash side-effects). Those are handled in their own branches.
_STANDARD_TREATMENTS: dict[type, EventTreatment] = {
    OvertimeEvent: EventTreatment(inps=True, tfr=False, irpef=True),
    NightShiftEvent: EventTreatment(inps=True, tfr=False, irpef=True),
    HolidayWorkEvent: EventTreatment(inps=True, tfr=False, irpef=True),
    AbsenceEvent: EventTreatment(inps=True, tfr=True, irpef=True),
    SickLeaveEvent: EventTreatment(inps=True, tfr=False, irpef=True),
    BonusEvent: EventTreatment(inps=True, tfr=False, irpef=True),
    WelfareEvent: EventTreatment(inps=False, tfr=False, irpef=False),
}

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
    """Aggregated INPS/TFR/IRPEF bases from variable work events.

    Only the three axes that feed into rate computations are tracked here.
    All other axis-level amounts (gross, net, separate-tax, settlements) are
    read directly from the ledger after the event entries are posted.
    """

    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal


@dataclass(frozen=True)
class _PeriodAmounts:
    """Computed monetary amounts passed to pay-item and ledger builders.

    Does not include period_gross, period_net or period_employer_cost — those
    are derived from the ledger after all entries are posted.
    """

    monthly_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: Decimal
    period_irpef: Decimal
    period_tratt: Decimal
    period_surtax: Decimal
    period_taxable: Decimal


def _as_of(period_id: PeriodId) -> date:
    """Return the first calendar day of the competence period.

    Returns:
        ``date(year, month, 1)`` for the given period.
    """
    return date(period_id.year, period_id.month, 1)


def _resolve_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
) -> MonthlyPayChain:
    """Resolve the elementary pay chain for the period.

    For apprentices, scales by the applicable percentage or maps to the
    underclass.  For standard and fixed-term contracts the level chain is
    used unchanged.

    Returns:
        :class:`~ccnl_engine.engine.payroll.service.types.MonthlyPayChain`
        with each component rounded and ready for pay-item emission.
    """
    if isinstance(contract_type, Apprentice):
        chain, pct, _ = _apprentice_chain(
            ccnl, level, contract_type, 0, frozenset(), as_of
        )
        return chain.scaled(pct) if pct is not None else chain
    return _level_chain(ccnl, level, 0, frozenset(), as_of, is_apprentice=False)


def _compute_amounts(
    monthly_gross: Decimal,
    event_totals: _EventTotals,
    opening: PeriodState,
    additional_months: int,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: LevelCategory | None,
    surtax_rules: SurtaxRules | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    family_deduction_rules: FamilyDeductionRules | None = None,
) -> tuple[_PeriodAmounts, ContributionBreakdown, TaxComputation]:
    """Resolve all monetary amounts for the period from gross, events and YTD state.

    Returns:
        ``(_PeriodAmounts, ContributionBreakdown, TaxComputation)`` with all
        rounded monetary quantities, the per-component INPS breakdown, and the
        per-rule IRPEF computation.
    """
    # INPS: base salary + event INPS-liable amounts, with IVS ceiling enforcement
    period_inps_base = monthly_gross + event_totals.inps_base
    breakdown = resolve_contributions(
        period_inps_base,
        rules,
        contract_type,
        category,
        ytd_inps_base=opening.inps_base_ytd,
    )
    inps_employee = breakdown.employee
    inps_employer = breakdown.employer

    # For IRPEF projection we still need the raw employee rate (no ceiling split needed
    # here: the annual projection uses the nominal rate on the recurring base).
    rates = resolve_rates(rules, contract_type, category)

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

    # Family deductions reduce annual IRPEF
    if family_composition is not None and family_deduction_rules is not None:
        _, _, _, fam_ded = compute_family_deductions(
            family_composition, taxable, family_deduction_rules
        )
    else:
        fam_ded = _ZERO

    tax_comp = resolve_tax_computation(
        taxable,
        rules,
        opening_irpef_withheld=opening.irpef_withheld_ytd,
        months_closed=opening.months_closed,
        additional_months=additional_months,
        family_deductions=fam_ded,
    )
    period_irpef = tax_comp.ordinary_tax
    period_tratt = tax_comp.trattamento_integrativo

    # Addizionali regionale e comunale (SURTAX account, not ORDINARY_TAX)
    ig = next((c.amount for c in tax_comp.components if c.name == "irpef_gross"), _ZERO)
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

    period_taxable = money(taxable / additional_months)
    return (
        _PeriodAmounts(
            monthly_gross=monthly_gross,
            inps_employee=inps_employee,
            inps_employer=inps_employer,
            tfr=tfr,
            period_irpef=period_irpef,
            period_tratt=period_tratt,
            period_surtax=period_surtax,
            period_taxable=period_taxable,
        ),
        breakdown,
        tax_comp,
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


def _sum_ledger(entries: tuple[LedgerEntry, ...], account: AccountKind) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total for ``account`` in ``entries``, or zero when no entry is present.
    """
    return sum((e.amount for e in entries if e.account == account), _ZERO)


def _check_event_date(
    event: WorkEvent, date_ctx: EffectiveDateContext, idx: int
) -> None:
    """Raise InvalidInputError if event falls outside the competence period.

    ArrearsEvent is exempt: back-paid contract renewals legitimately reference
    past periods.

    Raises:
        InvalidInputError: When event_date is outside [period_start, period_end].
    """
    if isinstance(event, ArrearsEvent):
        return
    if not date_ctx.contains(event.event_date):
        msg = (
            f"event {idx} ({type(event).__name__}) event_date {event.event_date} "
            f"is outside period [{date_ctx.period_start}, {date_ctx.period_end}]"
        )
        raise InvalidInputError(msg)


def _standard_event_gross(event: WorkEvent) -> Decimal:
    """Compute the gross (payslip) amount for a standard work event.

    Returns:
        Rounded gross amount in EUR (negative for absence deductions).
    """
    if isinstance(event, OvertimeEvent):
        return money(event.hours * event.hourly_rate * event.multiplier)
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent)):
        return event.supplement_amount
    if isinstance(event, AbsenceEvent):
        return -money(event.hours * event.hourly_rate)
    if isinstance(event, SickLeaveEvent):
        return event.amount
    if isinstance(event, BonusEvent):
        return event.amount
    return event.amount  # type: ignore[union-attr]  # WelfareEvent


def _standard_event_item(
    event: WorkEvent,
    gross: Decimal,
    evt_id: str,
    cp: CompetencePeriod,
    payment_date: date,
) -> tuple[PayItem, str]:
    """Create the pay item and kind string for a standard work event.

    Returns:
        ``(item, pay_item_kind)`` where *pay_item_kind* is the string used in
        the corresponding
        :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`.
    """
    if isinstance(event, OvertimeEvent):
        return (
            OvertimeEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
            ),
            "overtime_earning",
        )
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent)):
        return (
            NightHolidayShiftEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            ),
            "night_holiday_shift_earning",
        )
    if isinstance(event, AbsenceEvent):
        return (
            AbsenceDeduction(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=event.hours,
                amount=gross,
                absence_days=event.hours / Decimal(8),
            ),
            "absence_deduction",
        )
    if isinstance(event, SickLeaveEvent):
        return (
            SicknessItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
                sick_days=Decimal(1),
            ),
            "sickness_item",
        )
    if isinstance(event, BonusEvent):
        return (
            BonusEarning(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            ),
            "bonus_earning",
        )
    return (
        WelfareItem(
            item_id=evt_id,
            competence_period=cp,
            payment_date=payment_date,
            quantity=Decimal(1),
            amount=gross,
        ),
        "welfare_item",
    )


def _treatment_deltas(
    treatment: EventTreatment, gross: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_delta, tfr_delta, irpef_delta) for a standard event.

    Returns:
        A triple of gross or zero for each axis per the treatment policy.
    """
    return (
        gross if treatment.inps else _ZERO,
        gross if treatment.tfr else _ZERO,
        gross if treatment.irpef else _ZERO,
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
    date_ctx: EffectiveDateContext,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    Most events produce one pay item and one CASH_EARNINGS entry.
    BilateralFundEvent produces two items (employee + employer) and two entries.
    ArrearsEvent and TerminationTFREvent each produce an additional SEPARATE_TAX entry.

    ArrearsEvent is exempt from the period-coherence check because it legitimately
    references past periods (back-paid contract renewals); see ``_check_event_date``.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    total_inps = _ZERO
    total_tfr = _ZERO
    total_irpef = _ZERO
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []

    for i, event in enumerate(events):
        evt_id = f"{tag}_evt{i}"
        _check_event_date(event, date_ctx, i)

        if isinstance(
            event,
            (
                OvertimeEvent,
                NightShiftEvent,
                HolidayWorkEvent,
                AbsenceEvent,
                SickLeaveEvent,
                BonusEvent,
                WelfareEvent,
            ),
        ):
            treatment = _STANDARD_TREATMENTS[type(event)]
            gross = _standard_event_gross(event)
            item, kind = _standard_event_item(event, gross, evt_id, cp, payment_date)
            di, dt, dirpef = _treatment_deltas(treatment, gross)
            total_inps += di
            total_tfr += dt
            total_irpef += dirpef
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
        elif isinstance(event, TerminationTFREvent):
            gross = event.amount
            sep_tax = money(gross * event.separate_tax_rate)
            item = TfrSettlementItem(
                item_id=evt_id,
                competence_period=cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=gross,
            )
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
        else:
            assert_never(event)

    return (
        _EventTotals(
            inps_base=total_inps,
            tfr_base=total_tfr,
            irpef_base=total_irpef,
        ),
        tuple(items),
        tuple(entries),
    )


def _build_pay_items(
    amounts: _PeriodAmounts,
    chain: MonthlyPayChain,
    period_id: PeriodId,
    payment_date: date,
) -> tuple[PayItem, ...]:
    """Build the base pay-item tuple from resolved period amounts and chain.

    The salary chain is emitted as elementary items (base, seniority, each
    allowance) rather than a single aggregated gross, making each component
    individually visible in the period result.

    Returns:
        Tuple of :class:`~ccnl_engine.engine.payroll.domain.pay_items.PayItem`
        instances for this period.
    """
    cp = CompetencePeriod(year=period_id.year, month=period_id.month)
    tag = f"{period_id.year}_{period_id.month:02d}"
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
    ])
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
    chain: MonthlyPayChain,
    period_id: PeriodId,
    payment_date: date,
) -> tuple[LedgerEntry, ...]:
    """Project base pay items to ledger entries.

    Salary chain components (base, seniority, each allowance) post as
    separate CASH_EARNINGS entries to mirror the elementary pay items.

    Returns:
        Tuple of :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`
        instances.
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
            chain.base,
        ),
    ]
    if chain.seniority > _ZERO:
        entries.append(
            _make_entry(
                f"seniority_{tag}",
                f"seniority_{tag}",
                "seniority_earning",
                cp,
                payment_date,
                AccountKind.CASH_EARNINGS,
                chain.seniority,
            )
        )
    for allowance, amount in chain.allowances:
        if amount > _ZERO:
            entries.append(
                _make_entry(
                    f"allowance_{allowance.code}_{tag}",
                    f"allowance_{allowance.code}_{tag}",
                    "fixed_allowance_earning",
                    cp,
                    payment_date,
                    AccountKind.CASH_EARNINGS,
                    amount,
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
    ])
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
    level = ccnl.level_by_code(request.level_code)
    date_ctx = EffectiveDateContext.from_period(
        request.period_id.year, request.period_id.month, request.payment_date
    )
    period_year = request.period_id.year
    year_rules = effective_repo.load_year_rules(
        period_year, ccnl.meta.tax_sector, request.num_employees
    )
    catalog = effective_repo.load_capability_catalog(period_year)
    capability_gaps = catalog.gaps(_OBSERVED, detect_absent=True, year=period_year)
    capability_report = CapabilityReport(catalog_year=period_year, gaps=capability_gaps)
    additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
    chain = _resolve_chain(ccnl, level, request.contract_type, as_of)
    monthly_gross = money(chain.base + chain.seniority + chain.allowances_total)

    cp = CompetencePeriod(year=request.period_id.year, month=request.period_id.month)
    tag = f"{period_year}_{request.period_id.month:02d}"
    event_totals, event_items, event_entries = _process_events(
        request.events, cp, request.payment_date, tag, date_ctx
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
    amounts, contribution_breakdown, tax_computation = _compute_amounts(
        monthly_gross,
        event_totals,
        request.opening_state,
        additional_months,
        year_rules,
        request.contract_type,
        level.category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=fam_ded_rules,
    )
    pay_items = _build_pay_items(
        amounts, chain, request.period_id, request.payment_date
    )
    ledger_entries = _project_ledger(
        amounts, chain, request.period_id, request.payment_date
    )
    all_entries = ledger_entries + event_entries

    period_gross = _sum_ledger(all_entries, AccountKind.CASH_EARNINGS)
    period_net = (
        period_gross
        + _sum_ledger(all_entries, AccountKind.TFR_SETTLEMENT)
        + _sum_ledger(all_entries, AccountKind.CREDITS)
        - _sum_ledger(all_entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        - _sum_ledger(all_entries, AccountKind.ORDINARY_TAX)
        - _sum_ledger(all_entries, AccountKind.SURTAX)
        - _sum_ledger(all_entries, AccountKind.SEPARATE_TAX)
    )
    period_employer_cost = (
        period_gross
        + _sum_ledger(all_entries, AccountKind.EMPLOYER_CONTRIBUTIONS)
        + _sum_ledger(all_entries, AccountKind.TFR_ACCRUAL)
    )

    period_inps_base = monthly_gross + event_totals.inps_base
    closing = PeriodState(
        months_closed=request.opening_state.months_closed + 1,
        irpef_withheld_ytd=(
            request.opening_state.irpef_withheld_ytd + amounts.period_irpef
        ),
        inps_employee_ytd=(
            request.opening_state.inps_employee_ytd
            + _sum_ledger(all_entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        ),
        gross_ytd=request.opening_state.gross_ytd + period_gross,
        inps_base_ytd=request.opening_state.inps_base_ytd + period_inps_base,
        taxable_ytd=request.opening_state.taxable_ytd + amounts.period_taxable,
    )
    return PeriodCalculationResult(
        period_id=request.period_id,
        payment_date=request.payment_date,
        period_gross=period_gross,
        period_net=period_net,
        period_employer_cost=period_employer_cost,
        closing_state=closing,
        pay_items=pay_items + event_items,
        ledger_entries=all_entries,
        capability_report=capability_report,
        contribution_breakdown=contribution_breakdown,
        tax_computation=tax_computation,
    )
