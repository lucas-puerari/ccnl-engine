"""Resolve a full-year IRPEF computation with per-component audit trace.

Each component is annotated with a ``rule_id`` (machine-readable) and
``fonte`` (human-readable legal reference) so callers can attribute every
euro of tax to its statutory basis.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service import irpef as irpef_svc
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)


def resolve_tax_computation(
    taxable: Decimal,
    rules: YearRules,
    *,
    opening_irpef_withheld: Decimal = _ZERO,
    months_closed: int = 0,
    additional_months: int = 12,
    family_deductions: Decimal = _ZERO,
) -> TaxComputation:
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
    ``max(0, (irpef_net_annual - ytd_withheld) / remaining_periods)``.

    Args:
        taxable: Annual IRPEF taxable base (gross - employee INPS).
        rules: Year-specific tax rules.
        opening_irpef_withheld: IRPEF already withheld this year (YTD).
        months_closed: Periods already closed this year (for conguaglio).
        additional_months: Total periods in the year (usually 12).
        family_deductions: Annual Art. 12 family deductions (computed
            separately by :func:`~...compute_family_deductions`).

    Returns:
        :class:`~ccnl_engine.payroll.domain.tax.TaxComputation` with
        all components and the period withholding.
    """
    components: list[TaxLineItem] = []

    ig = irpef_svc.irpef_gross(taxable, rules)
    components.append(
        TaxLineItem(
            name="irpef_gross",
            amount=ig,
            rule_id="art11-tuir",
            fonte="Art. 11 TUIR",
        )
    )

    wd = irpef_svc.work_income_deduction(taxable, constants=rules.work_deduction)
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
        ud = irpef_svc.ulteriore_detrazione_lavoro(taxable, rules.ulteriore_detrazione)
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
    remaining = max(1, additional_months - months_closed)
    if remaining == 1:
        # Final period: settle the full balance (can be negative = refund).
        ordinary_tax = money(withholding_due)
    else:
        ordinary_tax = money(max(_ZERO, withholding_due / remaining))

    # Trattamento integrativo: Art. 1 D.L. 3/2020 as updated by L. 207/2024
    period_tratt = _ZERO
    if rules.trattamento_integrativo is not None:
        annual_tratt = irpef_svc.trattamento_integrativo(
            taxable, ig, wd, wd, rules.trattamento_integrativo
        )
        period_tratt = money(annual_tratt / additional_months)
        if annual_tratt > _ZERO:
            components.append(
                TaxLineItem(
                    name="trattamento_integrativo",
                    amount=annual_tratt,
                    rule_id="dl3-2020-art1",
                    fonte="Art. 1 D.L. 3/2020 (L. 207/2024)",
                )
            )

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
    )
