"""Fiscal-chain trace builder for payroll computations.

Produces the ordered :class:`~ccnl_engine.engine.payroll.domain.calculation\
.TraceStep` list that records the annual derivation from gross to net.

The fiscal chain is a *derivation* — each step shows what is deducted from or
added to the running total — not a sum like the gross chain.  All amounts are
annual.  Steps with zero amounts are emitted unconditionally so the skeleton
stays stable across runs and diffs cleanly.

The only fork is the ``employer_withholds_irpef`` flag: when ``False`` the
IRPEF steps are labelled as informational (not actually withheld).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep

if TYPE_CHECKING:
    from decimal import Decimal

_ANNUAL = "annual"


def _step(
    category: TraceCategory,
    label: str,
    amount: Decimal,
    detail: str | None = None,
) -> TraceStep:
    """Return an annual :class:`TraceStep`.

    Returns:
        A :class:`TraceStep` with ``period="annual"``.
    """
    return TraceStep(
        category=category,
        label=label,
        amount=amount,
        detail=detail,
        period=_ANNUAL,
    )


def build_fiscal_trace(
    *,
    gross_annual: Decimal,
    inps_employee_annual: Decimal,
    inps_employer_annual: Decimal,
    employer_funds_annual: Decimal,
    tfr_annual: Decimal,
    taxable_income: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    family_deduction_annual: Decimal,
    art15_deduction_annual: Decimal,
    irpef_net: Decimal,
    addizionale_regionale_annual: Decimal,
    addizionale_comunale_annual: Decimal,
    trattamento_integrativo: Decimal,
    net_annual: Decimal,
    employer_withholds_irpef: bool,
) -> tuple[TraceStep, ...]:
    """Build the ordered fiscal-chain trace from pre-computed annual amounts.

    All step amounts are annual figures.  Steps are emitted unconditionally
    — including zeros — so the skeleton is stable across scenarios and diffs
    cleanly between engine versions.

    The only structural fork is ``employer_withholds_irpef``: when ``False``,
    the IRPEF and deduction steps are labelled as informational (the employer
    does not act as *sostituto d'imposta*).

    Args:
        gross_annual: Annual gross pay (starting point of the fiscal chain).
        inps_employee_annual: Employee INPS contribution (deducted).
        inps_employer_annual: Employer INPS contribution (informational).
        employer_funds_annual: Employer contractual-fund contribution
            (informational).
        tfr_annual: TFR accrual (informational).
        taxable_income: IRPEF taxable base (gross minus inps_employee).
        irpef_gross: IRPEF before work-income deduction (Art. 11 TUIR).
        work_income_deduction: Art. 13 work-income deduction.
        family_deduction_annual: Art. 12 family deductions (zero when absent).
        art15_deduction_annual: Art. 15 oneri detraibili (zero when absent).
        irpef_net: IRPEF actually withheld (after all deductions).
        addizionale_regionale_annual: Addizionale regionale (zero when
            no jurisdiction was supplied).
        addizionale_comunale_annual: Addizionale comunale (zero when
            no jurisdiction was supplied).
        trattamento_integrativo: Trattamento integrativo bonus (positive;
            zero when not applicable).
        net_annual: Annual net pay (the final result).
        employer_withholds_irpef: When ``False``, IRPEF steps are labelled
            as informational — the employer does not withhold tax.

    Returns:
        Ordered tuple of :class:`TraceStep` objects covering the full
        gross-to-net derivation.
    """
    irpef_suffix = "" if employer_withholds_irpef else " (informativo)"

    steps: list[TraceStep] = [
        # Gross summary (mirrors the last step of the gross chain, now annual)
        _step(
            TraceCategory.GROSS,
            "Lordo annuale",
            gross_annual,
        ),
        # Employee INPS contribution
        _step(
            TraceCategory.INPS_EMPLOYEE,
            "Contributi INPS dipendente",
            inps_employee_annual,
        ),
        # Taxable income (derivation)
        _step(
            TraceCategory.TAXABLE_INCOME,
            "Imponibile IRPEF",
            taxable_income,
            detail="gross_annual - inps_employee_annual",
        ),
        # IRPEF gross (Art. 11 TUIR)
        _step(
            TraceCategory.IRPEF_GROSS,
            f"IRPEF lorda (Art. 11 TUIR){irpef_suffix}",
            irpef_gross,
        ),
        # Work-income deduction (Art. 13 TUIR)
        _step(
            TraceCategory.WORK_DEDUCTION,
            f"Detrazione lavoro dipendente (Art. 13 TUIR){irpef_suffix}",
            work_income_deduction,
        ),
        # Family deductions (Art. 12 TUIR) — always emitted, zero when absent
        _step(
            TraceCategory.FAMILY_DEDUCTION,
            f"Detrazioni carichi familiari (Art. 12 TUIR){irpef_suffix}",
            family_deduction_annual,
        ),
        # Art. 15 deductions — always emitted, zero when absent
        _step(
            TraceCategory.ART15_DEDUCTION,
            f"Detrazioni Art. 15 TUIR{irpef_suffix}",
            art15_deduction_annual,
        ),
        # IRPEF net (deducted from gross)
        _step(
            TraceCategory.IRPEF_NET,
            "IRPEF netta",
            irpef_net,
        ),
        # Addizionale regionale — always emitted, zero when no jurisdiction
        _step(
            TraceCategory.ADDIZIONALE_REGIONALE,
            "Addizionale regionale IRPEF",
            addizionale_regionale_annual,
        ),
        # Addizionale comunale — always emitted, zero when no jurisdiction
        _step(
            TraceCategory.ADDIZIONALE_COMUNALE,
            "Addizionale comunale IRPEF",
            addizionale_comunale_annual,
        ),
        # Trattamento integrativo (positive; zero when not applicable)
        _step(
            TraceCategory.TRATTAMENTO_INTEGRATIVO,
            "Trattamento integrativo (Art. 1 D.L. 3/2020)",
            trattamento_integrativo,
        ),
        # Net annual (final result)
        _step(
            TraceCategory.NET,
            "Netto annuale",
            net_annual,
            detail=(
                "gross_annual - inps_employee_annual - irpef_net"
                " - addizionale_regionale_annual"
                " - addizionale_comunale_annual"
                " + trattamento_integrativo"
            ),
        ),
        # --- Employer side (informational only; not part of net derivation) ---
        _step(
            TraceCategory.INPS_EMPLOYER,
            "Contributi INPS datore (informativo)",
            inps_employer_annual,
        ),
        _step(
            TraceCategory.EMPLOYER_FUNDS,
            "Fondi contrattuali datore (informativo)",
            employer_funds_annual,
        ),
        _step(
            TraceCategory.TFR,
            "Accantonamento TFR (informativo)",
            tfr_annual,
        ),
    ]

    return tuple(steps)
