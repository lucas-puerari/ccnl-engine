"""Audit trace of the annual IRPEF of a run: one line item per rule.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.tax import TaxLineItem
from ccnl_engine.payroll.service.foreign_tax_credit import foreign_credit_rule
from ccnl_engine.payroll.service.irpef_credits import somma_esente
from ccnl_engine.payroll.service.period_withholding import NO_PAY, PayPeriod
from ccnl_engine.payroll.service.ulteriore_recovery import ulteriore_items
from ccnl_engine.payroll.service.withholding_law import (
    WithholdingTopic,
    withholding_rule,
)

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
        ulteriore detrazione, sterilizzazione and foreign tax credit, each
        only when it applies,
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
    if annual.foreign_credit > _ZERO:
        law = withholding_rule(WithholdingTopic.CONGUAGLIO, rules.year)
        rule_id, citation = foreign_credit_rule(rules.year)
        components.append(
            TaxLineItem(
                name="foreign_tax_credit",
                amount=annual.foreign_credit,
                rule_id=rule_id,
                fonte=f"{citation}; {law.citation}",
            )
        )
    return components, decisions


def somma_esente_items(
    taxable: Decimal,
    rules: YearRules,
    eligible_work_days: int,
    external_income: Decimal = _ZERO,
    period: PayPeriod = NO_PAY,
) -> tuple[TaxLineItem, ...]:
    """Return the trace of the somma esente of L. 207/2024, when it is due.

    ``external_income`` is the reddito complessivo beyond this employment
    (art. 1 c. 4 and 9).  ``period`` holds the employment income the run
    pays: the withholding agent applies the percentage of the projected
    annual income "al reddito effettivamente corrisposto mensilmente" (AdE
    circ. 4/E/2025 par. 1.2), the ``somma_esente_period`` component.

    Returns:
        The annual ``somma_esente`` and the ``somma_esente_period`` of the
        run when the rules are in force and the amount is positive,
        otherwise none.
    """
    if rules.somma_esente is None:
        return ()
    amount = somma_esente(
        taxable, rules.somma_esente, eligible_work_days, external_income
    )
    if amount <= _ZERO:
        return ()
    return (
        TaxLineItem(
            name="somma_esente",
            amount=amount,
            rule_id="l207-2024-somma-esente",
            fonte="Art. 1 c. 4-5 L. 207/2024",
        ),
        TaxLineItem(
            name="somma_esente_period",
            amount=money(amount * period.taxable / taxable),
            rule_id="l207-2024-somma-esente",
            fonte="Art. 1 c. 7 L. 207/2024; AdE circ. 4/E/2025 par. 1.2",
        ),
    )
