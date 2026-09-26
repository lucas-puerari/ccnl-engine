"""Resolve a full-year IRPEF computation with per-component audit trace.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.obligations import (
    RECOVERY_RULES,
    TRATTAMENTO_RECOVERY,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.service import irpef as irpef_svc
from ccnl_engine.payroll.service import irpef_credits
from ccnl_engine.payroll.service.credit_decisions import credit_decision
from ccnl_engine.payroll.service.irpef_net import net_irpef, run_withholding
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule

_ZERO = Decimal(0)
# D.L. 3/2020 art. 1 co. 3: recovery exceeding 60 EUR uses 8 equal installments.
_RECOVERY_INSTALLMENT_THRESHOLD = Decimal(60)
_RECOVERY_INSTALLMENTS = RECOVERY_RULES[TRATTAMENTO_RECOVERY].installments
_TRATTAMENTO_RULE = "dl3-2020-art1"
_ULTERIORE_RULE = "l207-2024-art1-c6"


@dataclass(frozen=True, slots=True)
class TaxResolution:
    """IRPEF computation of a period with the decisions taken on its credits.

    Attributes:
        computation: The per-component IRPEF computation.
        recovery_plan: Recovery plan to carry into the next period, or
            ``None`` when no recovery is in progress.
        decisions: One decision per credit whose rules are in force for the
            year: ``ulteriore_detrazione_lavoro`` then
            ``trattamento_integrativo``.
        irpef_net: Net annual IRPEF: gross less the deductions, at least
            zero.  The surtax is due only when it is positive.
    """

    computation: TaxComputation
    recovery_plan: RecoveryPlan | None
    decisions: tuple[CalculationDecision, ...] = ()
    irpef_net: Decimal = _ZERO


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
    plan = RecoveryPlan.create(TRATTAMENTO_RECOVERY, recovery, _RECOVERY_INSTALLMENTS)
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
) -> tuple[
    Decimal, TaxLineItem | None, RecoveryPlan | None, CalculationDecision | None
]:
    """Compute the per-period trattamento integrativo via conguaglio.

    When the worker owes back a credit (tratt_due < 0) the recovery is split
    into eight equal installments if the amount exceeds 60 EUR, or taken in
    one period otherwise (D.L. 3/2020 art. 1 co. 3).  Once a
    :class:`~ccnl_engine.payroll.domain.recovery_plan.RecoveryPlan` is in
    force (``existing_plan`` is not ``None``) the installment amount is frozen
    for all remaining periods and the last installment absorbs the rounding
    residual.

    Returns:
        ``(period_tratt, component, next_plan, decision)`` where:
        - ``period_tratt`` is the signed per-period amount (negative = recovery);
        - ``component`` is a :class:`TaxLineItem` for the audit trace when the
          annual entitlement is positive, or ``None`` otherwise;
        - ``next_plan`` is the updated :class:`RecoveryPlan` to carry into the
          next period's opening state, or ``None`` when no plan is active;
        - ``decision`` records the annual entitlement, why it is due or not,
          and the signed ``period_amount``; ``None`` when the credit is not
          in force for the year.
    """
    if rules.trattamento_integrativo is None:
        return _ZERO, None, None, None
    outcome = irpef_credits.trattamento_integrativo_outcome(
        taxable,
        irpef_gross,
        work_deduction,
        work_deduction,
        rules.trattamento_integrativo,
        eligible_work_days=eligible_work_days,
    )
    annual_tratt = outcome.amount
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
            rule_id=_TRATTAMENTO_RULE,
            fonte="Art. 1 D.L. 3/2020 (L. 207/2024)",
        )
        if annual_tratt > _ZERO
        else None
    )
    decision = credit_decision(
        "trattamento_integrativo",
        _TRATTAMENTO_RULE,
        rules,
        outcome,
        {
            "taxable_income": taxable,
            "irpef_gross": irpef_gross,
            "work_deduction": work_deduction,
            "eligible_work_days": str(eligible_work_days),
            "recovery_in_progress": str(existing_plan is not None).lower(),
            "period_amount": period_tratt,
        },
    )
    return period_tratt, component, next_plan, decision


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
    """Compute IRPEF as :func:`compute_tax`, without the credit decisions.

    Returns:
        ``(TaxComputation, RecoveryPlan | None)`` of :func:`compute_tax`.
    """
    resolution = compute_tax(
        taxable,
        rules,
        opening_irpef_withheld=opening_irpef_withheld,
        opening_tratt_ytd=opening_tratt_ytd,
        withholding_schedule=withholding_schedule,
        slots_closed=slots_closed,
        family_deductions=family_deductions,
        recovery_plan=recovery_plan,
        eligible_work_days=eligible_work_days,
    )
    return resolution.computation, resolution.recovery_plan


def compute_tax(
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
    net_without_one_off: Decimal | None = None,
) -> TaxResolution:
    """Compute IRPEF with a per-rule breakdown and the 2026 bonus measures.

    Applies in order:

    1. ``irpef_gross`` — Art. 11 TUIR marginal brackets.
    2. ``work_deduction`` — Art. 13 co. 1 TUIR (work-income deduction).
    3. ``family_deductions`` — Art. 12 TUIR (passed in; computed separately).
    4. ``ulteriore_detrazione`` — Art. 1 c. 6 L. 207/2024 (if configured).
    5. ``sterilizzazione`` — Art. 1 c. 3-4 L. 199/2025 (if configured).
    6. ``trattamento_integrativo`` — Art. 1 D.L. 3/2020 / L. 207/2024.
    7. ``somma_esente`` — L. 207/2024 low-income bonus (if configured).

    The period withholding (``ordinary_tax``) is
    :func:`~ccnl_engine.payroll.service.irpef_net.run_withholding`: the tax
    the one-off income of the run adds, plus the share
    ``max(0, (irpef_net_annual - one_off_tax - ytd_withheld) /
    remaining_slots)``, where ``remaining_slots`` counts the slots of
    ``withholding_schedule`` not yet closed, the current one included.  The
    last slot settles the full balance, which can be negative (a refund).

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
        net_without_one_off: Net annual IRPEF on the projection without the
            one-off income the run pays, or ``None`` when it pays none.  The
            difference from the full net is withheld on the run.

    Returns:
        The IRPEF computation with all components, the updated recovery plan
        to carry into the next period's opening state, and one decision per
        credit in force: the ulteriore detrazione and the trattamento
        integrativo, each with its annual amount and the reason it is due
        or not (e.g. ``income_above_upper_threshold``).
    """
    components: list[TaxLineItem] = []
    decisions: list[CalculationDecision] = []
    eligible_work_days = min(eligible_work_days, irpef_svc.DAYS_IN_YEAR)

    annual = net_irpef(
        taxable,
        rules,
        family_deductions=family_deductions,
        eligible_work_days=eligible_work_days,
    )
    ig, wd = annual.gross, annual.work_deduction
    components.extend((
        TaxLineItem(
            name="irpef_gross", amount=ig, rule_id="art11-tuir", fonte="Art. 11 TUIR"
        ),
        TaxLineItem(
            name="work_deduction",
            amount=wd,
            rule_id="art13-tuir",
            fonte="Art. 13 co. 1 TUIR",
        ),
    ))
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
    if annual.ulteriore is not None:
        decisions.append(
            credit_decision(
                "ulteriore_detrazione_lavoro",
                _ULTERIORE_RULE,
                rules,
                annual.ulteriore,
                {
                    "taxable_income": taxable,
                    "eligible_work_days": str(eligible_work_days),
                },
            )
        )
        if annual.ulteriore.amount > _ZERO:
            components.append(
                TaxLineItem(
                    name="ulteriore_detrazione",
                    amount=annual.ulteriore.amount,
                    rule_id=_ULTERIORE_RULE,
                    fonte="Art. 1 c. 6 L. 207/2024",
                )
            )

    # Sterilizzazione: Art. 1 c. 3-4 L. 199/2025 (high earners, > EUR 200k)
    if annual.effective_deductions < annual.total_deductions:
        components.append(
            TaxLineItem(
                name="sterilizzazione_detrazioni",
                amount=annual.effective_deductions - annual.total_deductions,
                rule_id="l199-2025-art1-c3-c4",
                fonte="Art. 1 c. 3-4 L. 199/2025",
            )
        )

    # withholding_due: positive = still owed; negative = refund due to worker.
    withholding_due = annual.net - opening_irpef_withheld
    remaining = withholding_schedule.remaining(slots_closed)
    ordinary_tax = run_withholding(
        annual.net, net_without_one_off, opening_irpef_withheld, remaining
    )

    period_tratt, tratt_component, next_recovery_plan, tratt = _resolve_trattamento(
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
    if tratt is not None:
        decisions.append(tratt)

    # Somma esente: L. 207/2024 low-income bonus
    if rules.somma_esente is not None:
        se = irpef_svc.somma_esente(taxable, rules.somma_esente, eligible_work_days)
        if se > _ZERO:
            components.append(
                TaxLineItem(
                    name="somma_esente",
                    amount=se,
                    rule_id="l207-2024-somma-esente",
                    fonte="Art. 1 c. 4-5 L. 207/2024",
                )
            )

    computation = TaxComputation(
        ordinary_tax=ordinary_tax,
        trattamento_integrativo=period_tratt,
        withholding_due=withholding_due,
        components=tuple(components),
    )
    return TaxResolution(
        computation, next_recovery_plan, tuple(decisions), irpef_net=annual.net
    )
