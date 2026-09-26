"""Audit trace of the annual IRPEF of a run: one line item per rule.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.tax import TaxLineItem
from ccnl_engine.payroll.service.irpef_credits import somma_esente
from ccnl_engine.payroll.service.ulteriore_recovery import ulteriore_items

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.service.irpef_net import NetIrpef
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["annual_items", "somma_esente_items"]

_ZERO = Decimal(0)


def annual_items(
    annual: NetIrpef,
    rules: YearRules,
    taxable: Decimal,
    family_deductions: Decimal,
    eligible_work_days: int,
) -> tuple[list[TaxLineItem], list[CalculationDecision]]:
    """Return the trace of the annual net IRPEF and the ulteriore decision.

    Returns:
        The components gross IRPEF, work deduction, family deductions,
        ulteriore detrazione and sterilizzazione, each only when it applies,
        and the decision on the ulteriore detrazione when it is in force.
    """
    components = [
        TaxLineItem(
            name="irpef_gross",
            amount=annual.gross,
            rule_id="art11-tuir",
            fonte="Art. 11 TUIR",
        ),
        TaxLineItem(
            name="work_deduction",
            amount=annual.work_deduction,
            rule_id="art13-tuir",
            fonte="Art. 13 co. 1 TUIR",
        ),
    ]
    if family_deductions > _ZERO:
        components.append(
            TaxLineItem(
                name="family_deductions",
                amount=family_deductions,
                rule_id="art12-tuir",
                fonte="Art. 12 TUIR",
            )
        )
    decisions: list[CalculationDecision] = []
    # Ulteriore detrazione (2026): Art. 1 c. 6 L. 207/2024
    if annual.ulteriore is not None:
        decision, component = ulteriore_items(
            annual.ulteriore, rules, taxable, eligible_work_days
        )
        decisions.append(decision)
        components.extend(component)
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
    return components, decisions


def somma_esente_items(
    taxable: Decimal, rules: YearRules, eligible_work_days: int
) -> tuple[TaxLineItem, ...]:
    """Return the trace of the somma esente of L. 207/2024, when it is due.

    Returns:
        One component when the rules are in force and the amount is
        positive, otherwise none.
    """
    if rules.somma_esente is None:
        return ()
    amount = somma_esente(taxable, rules.somma_esente, eligible_work_days)
    if amount <= _ZERO:
        return ()
    return (
        TaxLineItem(
            name="somma_esente",
            amount=amount,
            rule_id="l207-2024-somma-esente",
            fonte="Art. 1 c. 4-5 L. 207/2024",
        ),
    )
