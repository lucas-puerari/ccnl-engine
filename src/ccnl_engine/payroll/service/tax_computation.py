"""Resolve a full-year IRPEF computation with per-component audit trace.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.service import irpef as irpef_svc
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule

_ZERO = Decimal(0)
# D.L. 3/2020 art. 1 co. 3: recovery exceeding 60 EUR uses 8 equal installments.
_RECOVERY_INSTALLMENT_THRESHOLD = Decimal(60)
_RECOVERY_INSTALLMENTS = 8


def _advance_plan(plan: RecoveryPlan) -> RecoveryPlan | None:
    """Return the plan advanced by one installment, or None when fully recovered.

    Returns:
        The advanced plan, or ``None`` if this was the last installment.
    """
    is_last = plan.installments_posted == plan.installments_total - 1
    return None if is_last else plan.advance()


def _new_recovery(recovery: Decimal) -> tuple[Decimal, RecoveryPlan | None]:
    """Open a fresh recovery: return (installment_amount, next_plan).

    Amounts <= 60 EUR are taken in full immediately (single period).
    Larger amounts are split into eight equal installments per
    D.L. 3/2020 art. 1 co. 3.

    Returns:
        ``(installment, next_plan)`` where ``next_plan`` is ``None`` when
        the recovery is settled in a single period.
    """
    if recovery <= _RECOVERY_INSTALLMENT_THRESHOLD:
        return money(recovery), None
    plan = RecoveryPlan.create(
        "trattamento_integrativo", recovery, _RECOVERY_INSTALLMENTS
    )
    return plan.next_installment, _advance_plan(plan)


def _resolve_trattamento(
    taxable: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    rules: YearRules,
    opening_tratt_ytd: Decimal,
    remaining: int,
    existing_plan: RecoveryPlan | None = None,
    eligible_work_days: int = irpef_svc.DAYS_IN_YEAR,
) -> tuple[Decimal, TaxLineItem | None, RecoveryPlan | None]:
    """Compute the per-period trattamento integrativo via conguaglio.

    When the worker owes back a credit (tratt_due < 0) the recovery is split
    into eight equal installments if the amount exceeds 60 EUR, or taken in
    one period otherwise (D.L. 3/2020 art. 1 co. 3).  Once a
    :class:`~ccnl_engine.payroll.domain.recovery_plan.RecoveryPlan` is in
    force (``existing_plan`` is not ``None``) the installment amount is frozen
    for all remaining periods and the last installment absorbs the rounding
    residual.

    Returns:
        ``(period_tratt, component, next_plan)`` where:
        - ``period_tratt`` is the signed per-period amount (negative = recovery);
        - ``component`` is a :class:`TaxLineItem` for the audit trace when the
          annual entitlement is positive, or ``None`` otherwise;
        - ``next_plan`` is the updated :class:`RecoveryPlan` to carry into the
          next period's opening state, or ``None`` when no plan is active.
    """
    if rules.trattamento_integrativo is None:
        return _ZERO, None, None
    tratt_rules = rules.trattamento_integrativo
    annual_tratt = irpef_svc.trattamento_integrativo(
        taxable,
        irpef_gross,
        work_deduction,
        work_deduction,
        tratt_rules,
        eligible_work_days=eligible_work_days,
    )
    if existing_plan is not None:
        period_tratt = -existing_plan.next_installment
        next_plan: RecoveryPlan | None = _advance_plan(existing_plan)
    else:
        tratt_due = annual_tratt - opening_tratt_ytd
        if tratt_due >= _ZERO:
            period_tratt = (
                money(tratt_due) if remaining == 1 else money(tratt_due / remaining)
            )
            next_plan = None
        else:
            installment, next_plan = _new_recovery(-tratt_due)
            period_tratt = -installment
    component = (
        TaxLineItem(
            name="trattamento_integrativo",
            amount=annual_tratt,
            rule_id="dl3-2020-art1",
            fonte="Art. 1 D.L. 3/2020 (L. 207/2024)",
        )
        if annual_tratt > _ZERO
        else None
    )
    return period_tratt, component, next_plan


def resolve_tax_computation(
    taxable: Decimal,
    rules: YearRules,
    *,
    opening_irpef_withheld: Decimal = _ZERO,
    opening_tratt_ytd: Decimal = _ZERO,
    withholding_schedule: WithholdingSchedule,
    slots_closed: int = 0,
    family_deductions: Decimal = _ZERO,
    recovery_plan: RecoveryPlan | None = None,
    eligible_work_days: int = irpef_svc.DAYS_IN_YEAR,
) -> tuple[TaxComputation, RecoveryPlan | None]:
    """Compute IRPEF with a per-rule breakdown and the 2026 bonus measures.

    Applies in order:

    1. ``irpef_gross`` — Art. 11 TUIR marginal brackets.
    2. ``work_deduction`` — Art. 13 co. 1 TUIR (work-income deduction).
    3. ``family_deductions`` — Art. 12 TUIR (passed in; computed separately).
    4. ``ulteriore_detrazione`` — Art. 1 c. 6 L. 207/2024 (if configured).
    5. ``sterilizzazione`` — Art. 1 c. 3-4 L. 199/2025 (if configured).
    6. ``trattamento_integrativo`` — Art. 1 D.L. 3/2020 / L. 207/2024.
    7. ``somma_esente`` — L. 207/2024 low-income bonus (if configured).

    The period withholding (``ordinary_tax``) is the conguaglio share:
    ``max(0, (irpef_net_annual - ytd_withheld) / remaining_slots)``, where
    ``remaining_slots`` counts the slots of ``withholding_schedule`` not yet
    closed, the current one included.  The last slot settles the full
    balance, which can be negative (a refund).

    Args:
        taxable: Annual IRPEF taxable base (gross - employee INPS).
        rules: Year-specific tax rules.
        opening_irpef_withheld: IRPEF already withheld this year (YTD).
        opening_tratt_ytd: Trattamento integrativo already given this year
            (YTD).  Used for the conguaglio so over-payments are recovered
            and the annual entitlement is never exceeded.
        withholding_schedule: Withholding slots of the year, one per
            payslip.  Never derived from the equivalent months of pay.
        slots_closed: Withholding slots already closed this year.
        family_deductions: Annual Art. 12 family deductions (computed
            separately by :func:`~...compute_family_deductions`).
        recovery_plan: Active installment recovery plan from the previous
            period's closing state, or ``None`` when no recovery is in
            progress.  When present, the installment amount is taken from
            the plan rather than recomputed.
        eligible_work_days: Days of employment in the tax year, capped at
            365.  The work deduction, the ulteriore detrazione and the
            trattamento integrativo are proportioned to them ("rapportata
            al periodo di lavoro nell'anno": art. 13 c. 1 TUIR, L. 207/2024
            art. 1 c. 6, D.L. 3/2020 art. 1).

    Returns:
        ``(TaxComputation, RecoveryPlan | None)`` — the IRPEF computation
        with all components and the updated recovery plan to carry into the
        next period's opening state.
    """
    components: list[TaxLineItem] = []
    eligible_work_days = min(eligible_work_days, irpef_svc.DAYS_IN_YEAR)

    ig = irpef_svc.irpef_gross(taxable, rules)
    components.append(
        TaxLineItem(
            name="irpef_gross",
            amount=ig,
            rule_id="art11-tuir",
            fonte="Art. 11 TUIR",
        )
    )

    wd = irpef_svc.work_income_deduction(
        taxable, eligible_work_days, constants=rules.work_deduction
    )
    components.append(
        TaxLineItem(
            name="work_deduction",
            amount=wd,
            rule_id="art13-tuir",
            fonte="Art. 13 co. 1 TUIR",
        )
    )

    if family_deductions > _ZERO:
        components.append(
            TaxLineItem(
                name="family_deductions",
                amount=family_deductions,
                rule_id="art12-tuir",
                fonte="Art. 12 TUIR",
            )
        )

    # Ulteriore detrazione (2026): Art. 1 c. 6 L. 207/2024
    ud = _ZERO
    if rules.ulteriore_detrazione is not None:
        ud = irpef_svc.ulteriore_detrazione_lavoro(
            taxable, rules.ulteriore_detrazione, eligible_work_days
        )
        if ud > _ZERO:
            components.append(
                TaxLineItem(
                    name="ulteriore_detrazione",
                    amount=ud,
                    rule_id="l207-2024-art1-c6",
                    fonte="Art. 1 c. 6 L. 207/2024",
                )
            )

    total_deductions = wd + family_deductions + ud
    # Sterilizzazione: Art. 1 c. 3-4 L. 199/2025 (high earners, > EUR 200k)
    effective_deductions = irpef_svc.apply_sterilizzazione_detrazioni(
        total_deductions, taxable, rules.sterilizzazione_detrazioni
    )
    if effective_deductions < total_deductions:
        reduction = total_deductions - effective_deductions
        components.append(
            TaxLineItem(
                name="sterilizzazione_detrazioni",
                amount=-reduction,
                rule_id="l199-2025-art1-c3-c4",
                fonte="Art. 1 c. 3-4 L. 199/2025",
            )
        )

    irpef_net_annual = max(_ZERO, ig - effective_deductions)

    # withholding_due: positive = still owed; negative = refund due to worker.
    # The last period settles the full balance; earlier periods clamp at zero to
    # avoid spreading a mid-year refund across months.
    withholding_due = irpef_net_annual - opening_irpef_withheld
    remaining = withholding_schedule.remaining(slots_closed)
    if remaining == 1:
        # Final period: settle the full balance (can be negative = refund).
        ordinary_tax = money(withholding_due)
    else:
        ordinary_tax = money(max(_ZERO, withholding_due / remaining))

    period_tratt, tratt_component, next_recovery_plan = _resolve_trattamento(
        taxable,
        ig,
        wd,
        rules,
        opening_tratt_ytd,
        remaining,
        recovery_plan,
        eligible_work_days,
    )
    if tratt_component is not None:
        components.append(tratt_component)

    # Somma esente: L. 207/2024 low-income bonus
    if rules.somma_esente is not None:
        se = irpef_svc.somma_esente(taxable, rules.somma_esente)
        if se > _ZERO:
            components.append(
                TaxLineItem(
                    name="somma_esente",
                    amount=se,
                    rule_id="l207-2024-somma-esente",
                    fonte="L. 207/2024 (somma esente)",
                )
            )

    return TaxComputation(
        ordinary_tax=ordinary_tax,
        trattamento_integrativo=period_tratt,
        withholding_due=withholding_due,
        components=tuple(components),
    ), next_recovery_plan
