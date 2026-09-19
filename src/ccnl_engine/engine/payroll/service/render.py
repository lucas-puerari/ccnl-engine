"""Payroll breakdown renderer.

Produces a structured, human-readable annual breakdown from a
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.AnnualEstimate`,
ordered in the conventional Italian payslip sequence (lordo → INPS →
imponibile → IRPEF → detrazioni → netto).

**Important**: all amounts in :class:`AnnualBreakdown` are *annual* totals.
Monthly figures (where shown) are simple ``annual / additional_months``
approximations; they do not model the actual monthly withholding calendar
(e.g. addizionali are withheld over 11 instalments in practice, and IRPEF
is subject to an end-of-year conguaglio).  Use the annual totals for
comparisons and rely on a dedicated payroll system for month-by-month payslips.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.payroll_result import AnnualEstimate


@dataclass(frozen=True)
class AnnualBreakdown:
    """Annual gross-to-net payroll breakdown in payslip order.

    All ``Decimal`` amounts are annual EUR totals.  Monthly approximations
    (where shown) are ``annual / additional_months`` and do not model the
    actual monthly withholding calendar.

    Attributes:
        gross_annual: Annual gross pay.
        inps_employee_annual: Employee INPS contribution.
        taxable_income: IRPEF taxable base (gross minus INPS employee).
        irpef_gross: IRPEF before work-income deduction.
        work_income_deduction: Art. 13 TUIR work-income deduction.
        ulteriore_detrazione_lavoro: Ulteriore detrazione lavoro
            (D.L. 3/2020, Art. 1, co. 1-bis); zero when not applicable.
        family_deduction_annual: Art. 12 TUIR family deductions.
        art15_deduction_annual: Art. 15 TUIR oneri detraibili (pre-clawback).
        sterilizzazione_clawback_annual: Sterilizzazione detrazioni clawback
            (Art. 1 c. 3-4 L. 199/2025): amount by which the Art. 15 credit
            was reduced for reddito complessivo above the threshold. Zero when
            the income is below the threshold or no Art. 15 deductions apply.
        irpef_net: IRPEF net (after all deductions; zero when employer
            does not act as sostituto d'imposta).
        addizionale_regionale_annual: Regional IRPEF surtax.
        addizionale_comunale_annual: Municipal IRPEF surtax.
        trattamento_integrativo: Trattamento integrativo bonus.
        somma_esente: Somma esente bonus (L. 207/2024); zero when not
            applicable.
        bilateral_employee_annual: Employee bilateral-fund contribution;
            zero when no bilateral funds were supplied.
        net_annual: Annual net pay.
        net_monthly_approx: Monthly net approximation
            (``net_annual / additional_months``).
        inps_employer_annual: Employer INPS contribution (informational).
        employer_funds_annual: Employer contractual-fund contribution
            (informational).
        tfr_annual: TFR accrual (informational).
        bilateral_employer_annual: Employer bilateral-fund contribution
            (informational); zero when no bilateral funds were supplied.
        employer_cost_annual: Total annual employer cost (informational).
        employer_withholds_irpef: Whether the employer withholds IRPEF.
    """

    gross_annual: Decimal
    inps_employee_annual: Decimal
    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    ulteriore_detrazione_lavoro: Decimal
    family_deduction_annual: Decimal
    art15_deduction_annual: Decimal
    sterilizzazione_clawback_annual: Decimal
    irpef_net: Decimal
    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal
    trattamento_integrativo: Decimal
    somma_esente: Decimal
    bilateral_employee_annual: Decimal
    net_annual: Decimal
    net_monthly_approx: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employer_annual: Decimal
    employer_cost_annual: Decimal
    employer_withholds_irpef: bool

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        All :class:`~decimal.Decimal` amounts are converted to ``str``.

        Returns:
            A dictionary with JSON-native types.
        """
        out: dict[str, object] = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            out[field.name] = str(value) if isinstance(value, Decimal) else value
        return out

    def to_json(self) -> str:
        """Serialise to a JSON string.

        Returns:
            A compact JSON string (see :meth:`to_dict` for encoding rules).
        """
        return json.dumps(self.to_dict())


def render_breakdown(result: AnnualEstimate) -> AnnualBreakdown:
    """Produce an :class:`AnnualBreakdown` from an :class:`AnnualEstimate`.

    Reads all relevant fields from *result* and returns them arranged in the
    conventional Italian payslip order.  The monthly approximation is taken
    directly from ``result.net_monthly`` (which is ``net_annual / additional_months``
    as computed by the orchestrator).

    Args:
        result: A computed :class:`AnnualEstimate`.

    Returns:
        An :class:`AnnualBreakdown` with all annual figures and a monthly
        approximation.
    """
    return AnnualBreakdown(
        net_monthly_approx=result.net_monthly,
        gross_annual=result.earnings.gross_annual,
        inps_employee_annual=result.contributions.inps_employee_annual,
        taxable_income=result.taxes.taxable_income,
        irpef_gross=result.taxes.irpef_gross,
        work_income_deduction=result.taxes.work_income_deduction,
        ulteriore_detrazione_lavoro=result.taxes.ulteriore_detrazione_lavoro,
        family_deduction_annual=result.taxes.family_deduction_annual,
        art15_deduction_annual=result.taxes.art15_deduction_annual,
        sterilizzazione_clawback_annual=result.taxes.sterilizzazione_clawback_annual,
        irpef_net=result.taxes.irpef_net,
        addizionale_regionale_annual=result.taxes.addizionale_regionale_annual,
        addizionale_comunale_annual=result.taxes.addizionale_comunale_annual,
        trattamento_integrativo=result.taxes.trattamento_integrativo,
        somma_esente=result.taxes.somma_esente,
        bilateral_employee_annual=result.contributions.bilateral_employee_annual,
        net_annual=result.net_annual,
        inps_employer_annual=result.contributions.inps_employer_annual,
        employer_funds_annual=result.contributions.employer_funds_annual,
        tfr_annual=result.contributions.tfr_annual,
        bilateral_employer_annual=result.contributions.bilateral_employer_annual,
        employer_cost_annual=result.employer_cost.employer_cost_annual,
        employer_withholds_irpef=result.taxes.employer_withholds_irpef,
    )
