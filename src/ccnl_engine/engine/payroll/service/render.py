"""Payroll breakdown renderer.

Produces a structured, human-readable annual breakdown from a
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.PayrollResult`,
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
    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult


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
        family_deduction_annual: Art. 12 TUIR family deductions.
        art15_deduction_annual: Art. 15 TUIR oneri detraibili.
        irpef_net: IRPEF net (after all deductions; zero when employer
            does not act as sostituto d'imposta).
        addizionale_regionale_annual: Regional IRPEF surtax.
        addizionale_comunale_annual: Municipal IRPEF surtax.
        trattamento_integrativo: Trattamento integrativo bonus.
        net_annual: Annual net pay.
        net_monthly_approx: Monthly net approximation
            (``net_annual / additional_months``).
        inps_employer_annual: Employer INPS contribution (informational).
        employer_funds_annual: Employer contractual-fund contribution
            (informational).
        tfr_annual: TFR accrual (informational).
        employer_cost_annual: Total annual employer cost (informational).
        employer_withholds_irpef: Whether the employer withholds IRPEF.
    """

    gross_annual: Decimal
    inps_employee_annual: Decimal
    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    family_deduction_annual: Decimal
    art15_deduction_annual: Decimal
    irpef_net: Decimal
    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal
    trattamento_integrativo: Decimal
    net_annual: Decimal
    net_monthly_approx: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
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


def render_breakdown(result: PayrollResult) -> AnnualBreakdown:
    """Produce an :class:`AnnualBreakdown` from a :class:`PayrollResult`.

    Reads all relevant fields from *result* and returns them arranged in the
    conventional Italian payslip order.  The monthly approximation is taken
    directly from ``result.net_monthly`` (which is ``net_annual / additional_months``
    as computed by the orchestrator).

    Args:
        result: A computed :class:`PayrollResult`.

    Returns:
        An :class:`AnnualBreakdown` with all annual figures and a monthly
        approximation.
    """
    return AnnualBreakdown(
        net_monthly_approx=result.net_monthly,
        gross_annual=result.gross_annual,
        inps_employee_annual=result.inps_employee_annual,
        taxable_income=result.taxable_income,
        irpef_gross=result.irpef_gross,
        work_income_deduction=result.work_income_deduction,
        family_deduction_annual=result.family_deduction_annual,
        art15_deduction_annual=result.art15_deduction_annual,
        irpef_net=result.irpef_net,
        addizionale_regionale_annual=result.addizionale_regionale_annual,
        addizionale_comunale_annual=result.addizionale_comunale_annual,
        trattamento_integrativo=result.trattamento_integrativo,
        net_annual=result.net_annual,
        inps_employer_annual=result.inps_employer_annual,
        employer_funds_annual=result.employer_funds_annual,
        tfr_annual=result.tfr_annual,
        employer_cost_annual=result.employer_cost_annual,
        employer_withholds_irpef=result.employer_withholds_irpef,
    )
