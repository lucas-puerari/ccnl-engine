"""Resolve a full-year IRPEF computation with per-component audit trace.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.taxation.results import TaxComputation
from ccnl_engine.payroll.taxation.results_irpef_trace import (
    annual_items,
    somma_esente_items,
)
from ccnl_engine.payroll.taxation.rules_foreign_tax_credit import foreign_tax_credit
from ccnl_engine.payroll.taxation.rules_irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.taxation.rules_irpef_minimum import minimum_decision
from ccnl_engine.payroll.taxation.rules_irpef_net import net_irpef
from ccnl_engine.payroll.taxation.rules_trattamento_credit import resolve_trattamento
from ccnl_engine.payroll.taxation.rules_ulteriore_recovery import (
    withhold_with_ulteriore,
)
from ccnl_engine.payroll.withholding.models_recovery_plan import InstallmentRun
from ccnl_engine.payroll.withholding.rules_period import NO_PAY, period_tax

if TYPE_CHECKING:
    from ccnl_engine.payroll.assurance.models_decision import CalculationDecision
    from ccnl_engine.payroll.state.models_credit_account import CreditAccount
    from ccnl_engine.payroll.taxation.inputs_foreign_tax import ForeignTaxPaid
    from ccnl_engine.payroll.taxation.results import TaxLineItem
    from ccnl_engine.payroll.taxation.rules_irpef_net import NetIrpef
    from ccnl_engine.payroll.taxation.rules_ulteriore_settlement import (
        UlterioreSettlement,
    )
    from ccnl_engine.payroll.withholding.models_recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.withholding.rules_period import PayPeriod
    from ccnl_engine.tax.annual.models import YearRules

_ZERO = Decimal(0)
#: A run that is neither the last of the employment nor an adjustment.
_ORDINARY_RUN = InstallmentRun()


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
            zero, less the foreign tax credit of the conguaglio.  The surtax
            is due only when it is positive.
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
    remaining_slots: int,
    family_deductions: Decimal = _ZERO,
    recovery_plan: RecoveryPlan | None = None,
    eligible_work_days: int = DAYS_IN_YEAR,
    period: PayPeriod = NO_PAY,
    carried_shortfall: Decimal = _ZERO,
    ulteriore_account: CreditAccount | None = None,
    run: InstallmentRun = _ORDINARY_RUN,
    ulteriore_plan: RecoveryPlan | None = None,
    foreign_taxes: tuple[ForeignTaxPaid, ...] = (),
    fixed_term: bool = False,
    external_income: Decimal = _ZERO,
) -> TaxResolution:
    """Compute IRPEF with a per-rule breakdown and the 2026 bonus measures.

    Applies in order:

    1. ``irpef_gross``: Art. 11 TUIR marginal brackets.
    2. ``work_deduction``: Art. 13 co. 1 TUIR (work-income deduction).
    3. ``family_deductions``: Art. 12 TUIR (passed in; computed separately).
    4. ``ulteriore_detrazione``: Art. 1 c. 6 L. 207/2024 (if configured).
    5. ``foreign_tax_credit``: Art. 165 TUIR, from the imposta netta.
    6. ``trattamento_integrativo``: Art. 1 D.L. 3/2020 / L. 207/2024.
    7. ``somma_esente``: L. 207/2024 low-income bonus (if configured).

    The art. 16-ter c. 5-bis TUIR reduction is not among them: it lowers
    only deductions the payroll does not compute (see
    :mod:`~ccnl_engine.payroll.taxation.rules_irpef_net`).

    The period withholding (``ordinary_tax``) is
    :func:`~ccnl_engine.payroll.taxation.rules_irpef_net.run_withholding`: before
    the last slot the IRPEF of the pay period under art. 23 c. 2 DPR
    600/1973 (:func:`~ccnl_engine.payroll.withholding.rules_period\
.period_tax`), the deductions of the period taken from the annual ones on
    the projection; the last slot settles the full balance, which can be
    negative (a refund).

    Args:
        taxable: Annual IRPEF taxable base (gross - employee INPS).
        rules: Year-specific tax rules.
        opening_irpef_withheld: IRPEF already withheld this year (YTD).
        opening_tratt_ytd: Trattamento integrativo already given this year
            (YTD).  Used for the conguaglio so over-payments are recovered
            and the annual entitlement is never exceeded.
        remaining_slots: Withholding slots of the tax year not yet paid,
            the current one included; ``1`` on the conguaglio.  Never
            derived from the equivalent months of pay.
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
        period: Pay of the run as art. 23 c. 2 DPR 600/1973 withholds it
            before the last slot; :data:`NO_PAY` withholds nothing then.
        carried_shortfall: IRPEF of earlier runs of the tax year that their
            pay did not cover; withheld in full on this run.
        ulteriore_account: YTD account of the ulteriore detrazione, or
            ``None`` not to track it.  On the last slot an excess above 60
            EUR is deferred to ten installments (L. 207/2024 art. 1 c. 7).
        run: The run as a recovery sees it.  On the final run of the
            employment nothing is deferred and every running plan is
            settled; an adjustment run posts the next installment.
        ulteriore_plan: Ulteriore detrazione plan opened by a conguaglio of
            this tax year, whose next installment the run posts.
        foreign_taxes: Foreign taxes paid, credited on the annual IRPEF
            (:mod:`~ccnl_engine.payroll.taxation.rules_foreign_tax_credit`).  The
            caller passes them on the conguaglio only.
        fixed_term: Whether an employment of the year is fixed-term: the
            minimum of the art. 13 deduction is then 1,380 EUR instead of
            690 (c. 1 lett. a) TUIR), proportioned to the days on the
            projection and on the conguaglio alike.
        external_income: Reddito complessivo of the tax year beyond this
            employment, for the somma esente and the ulteriore detrazione
            (L. 207/2024 art. 1 c. 4, 6 and 9); zero when none is known.

    Returns:
        The IRPEF computation with all components, the updated recovery plan
        to carry into the next period's opening state, and one decision per
        credit in force: the ulteriore detrazione and the trattamento
        integrativo, each with its annual amount and the reason it is due
        or not (e.g. ``income_above_upper_threshold``).
    """
    days = min(eligible_work_days, DAYS_IN_YEAR)
    annual, components, decisions = _annual(
        taxable,
        rules,
        family_deductions,
        days,
        foreign_taxes,
        fixed_term=fixed_term,
        other_income=external_income,
    )
    remaining = remaining_slots
    ordinary_tax, ulteriore = withhold_with_ulteriore(
        annual,
        remaining,
        period_tax(period, annual, rules),
        opening_irpef_withheld=opening_irpef_withheld,
        carried_shortfall=carried_shortfall,
        ulteriore_account=ulteriore_account,
        run=run,
        running_plan=ulteriore_plan,
    )
    if ulteriore is not None:
        decisions.extend(ulteriore.decisions(rules))

    period_tratt, next_recovery_plan, tratt_items, tratt_decisions = _trattamento(
        taxable, annual, rules, opening_tratt_ytd, remaining, recovery_plan, days, run
    )
    components.extend(tratt_items)
    decisions.extend(tratt_decisions)
    components.extend(somma_esente_items(taxable, rules, days, external_income, period))

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


def _annual(
    taxable: Decimal,
    rules: YearRules,
    family_deductions: Decimal,
    days: int,
    foreign_taxes: tuple[ForeignTaxPaid, ...],
    *,
    fixed_term: bool,
    other_income: Decimal,
) -> tuple[NetIrpef, list[TaxLineItem], list[CalculationDecision]]:
    """Return the net annual IRPEF after the foreign tax credit, with its trace.

    Returns:
        The net IRPEF, its components and the decisions of the ulteriore
        detrazione, of the art. 13 minimum left to the tax return and of
        the foreign tax credit, each when it applies.
    """
    annual = net_irpef(
        taxable,
        rules,
        family_deductions=family_deductions,
        eligible_work_days=days,
        fixed_term=fixed_term,
        other_income=other_income,
    )
    credit = foreign_tax_credit(foreign_taxes, taxable, annual, rules)
    if credit is not None:
        annual = replace(annual, foreign_credit=credit.amount)
    components, decisions = annual_items(
        annual, rules, taxable, family_deductions, days
    )
    minimum = minimum_decision(rules, taxable, days, fixed_term=fixed_term)
    if minimum is not None:
        decisions.append(minimum)
    if credit is not None:
        decisions.append(credit.decision)
    return annual, components, decisions


def _trattamento(
    taxable: Decimal,
    annual: NetIrpef,
    rules: YearRules,
    opening_tratt_ytd: Decimal,
    remaining: int,
    recovery_plan: RecoveryPlan | None,
    eligible_work_days: int,
    run: InstallmentRun,
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
    period_tratt, component, next_plan, decisions = resolve_trattamento(
        taxable,
        annual,
        rules,
        opening_tratt_ytd,
        remaining,
        recovery_plan,
        eligible_work_days,
        run=run,
    )
    return (
        period_tratt,
        next_plan,
        () if component is None else (component,),
        decisions,
    )
