"""Resolve a full-year IRPEF computation with per-component audit trace.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.tax import TaxComputation
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.irpef_net import net_irpef
from ccnl_engine.payroll.service.irpef_trace import annual_items, somma_esente_items
from ccnl_engine.payroll.service.trattamento_credit import resolve_trattamento
from ccnl_engine.payroll.service.ulteriore_recovery import (
    UlterioreSettlement,
    withhold_with_ulteriore,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.credit_accounts import CreditAccount
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax import TaxLineItem
    from ccnl_engine.payroll.service.irpef_net import NetIrpef
    from ccnl_engine.tax.domain.ruleset import YearRules

_ZERO = Decimal(0)


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
        ulteriore: What the run recognized or recovered of the ulteriore
            detrazione, ``None`` when it is not tracked.
    """

    computation: TaxComputation
    recovery_plan: RecoveryPlan | None
    decisions: tuple[CalculationDecision, ...] = ()
    irpef_net: Decimal = _ZERO
    ulteriore: UlterioreSettlement | None = None


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
    eligible_work_days: int = DAYS_IN_YEAR,
    net_without_one_off: Decimal | None = None,
    carried_shortfall: Decimal = _ZERO,
    ulteriore_account: CreditAccount | None = None,
    ulteriore_without_one_off: Decimal = _ZERO,
    later_payslips: bool = True,
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
        carried_shortfall: IRPEF of earlier runs of the tax year that their
            pay did not cover; withheld in full on this run.
        ulteriore_account: YTD account of the ulteriore detrazione, or
            ``None`` not to track it.  On the last slot an excess above 60
            EUR is deferred to ten installments (L. 207/2024 art. 1 c. 7).
        ulteriore_without_one_off: IRPEF the ulteriore detrazione removes
            on the projection without the one-off income of the run.
        later_payslips: Whether payslips follow the last slot; false when
            the employment ends in the tax year, so nothing is deferred.

    Returns:
        The IRPEF computation with all components, the updated recovery plan
        to carry into the next period's opening state, and one decision per
        credit in force: the ulteriore detrazione and the trattamento
        integrativo, each with its annual amount and the reason it is due
        or not (e.g. ``income_above_upper_threshold``).
    """
    days = min(eligible_work_days, DAYS_IN_YEAR)
    annual = net_irpef(
        taxable, rules, family_deductions=family_deductions, eligible_work_days=days
    )
    components, decisions = annual_items(
        annual, rules, taxable, family_deductions, days
    )
    remaining = withholding_schedule.remaining(slots_closed)
    ordinary_tax, ulteriore = withhold_with_ulteriore(
        annual,
        remaining,
        opening_irpef_withheld=opening_irpef_withheld,
        net_without_one_off=net_without_one_off,
        carried_shortfall=carried_shortfall,
        ulteriore_account=ulteriore_account,
        ulteriore_without_one_off=ulteriore_without_one_off,
        later_payslips=later_payslips,
    )
    if ulteriore is not None:
        decisions.extend(ulteriore.decisions(rules))

    period_tratt, next_recovery_plan, tratt_items, tratt_decisions = _trattamento(
        taxable, annual, rules, opening_tratt_ytd, remaining, recovery_plan, days
    )
    components.extend(tratt_items)
    decisions.extend(tratt_decisions)
    components.extend(somma_esente_items(taxable, rules, days))

    return TaxResolution(
        TaxComputation(
            ordinary_tax=ordinary_tax,
            trattamento_integrativo=period_tratt,
            # Positive = still owed; negative = refund due to the worker.
            withholding_due=annual.net - opening_irpef_withheld,
            components=tuple(components),
        ),
        next_recovery_plan,
        tuple(decisions),
        irpef_net=annual.net,
        ulteriore=ulteriore,
    )


def _trattamento(
    taxable: Decimal,
    annual: NetIrpef,
    rules: YearRules,
    opening_tratt_ytd: Decimal,
    remaining: int,
    recovery_plan: RecoveryPlan | None,
    eligible_work_days: int,
) -> tuple[
    Decimal,
    RecoveryPlan | None,
    tuple[TaxLineItem, ...],
    tuple[CalculationDecision, ...],
]:
    """Return the trattamento integrativo of the run with its trace.

    Returns:
        ``(period_tratt, next_plan, components, decisions)``: the signed
        amount of the run, the recovery plan to carry forward, and the line
        item and decision of the credit, each only when there is one.
    """
    period_tratt, component, next_plan, decision = resolve_trattamento(
        taxable,
        annual.gross,
        annual.work_deduction,
        rules,
        opening_tratt_ytd,
        remaining,
        recovery_plan,
        eligible_work_days,
    )
    return (
        period_tratt,
        next_plan,
        () if component is None else (component,),
        () if decision is None else (decision,),
    )
