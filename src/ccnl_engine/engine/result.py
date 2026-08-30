"""ComputationResult dataclass — the output record of compute().

This is a frozen dataclass (not a Pydantic model) because it is an output
record, not validated input. All monetary fields are pre-rounded
:class:`~decimal.Decimal` values produced by
:func:`~ccnl_engine.engine.rounding.money`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal


@dataclass(frozen=True)
class ComputationResult:
    """Full gross-to-net and employer-cost breakdown for one payroll computation.

    All ``*_annual`` fields are annual totals; all ``*_monthly`` fields are
    the per-month equivalents (divided by ``additional_months``). Monetary
    values are rounded to the nearest cent.

    Attributes:
        ccnl_id: Stable identifier of the source CCNL (e.g.
            ``"commercio-confcommercio"``).
        level_code: Classification level code (e.g. ``"4"``).
        employment_type: ``"permanent"``, ``"fixed_term"``, or
            ``"apprentice"``.
        part_time_pct: Part-time fraction in ``(0, 1]``; ``1`` for full-time.
        as_of: Reference date used to look up salary and parameter values.
        year: Fiscal year (from ``as_of``).
        base_monthly: Monthly base salary (*paga base*) at full-time.
        seniority_monthly: Monthly seniority increments for the given count.
        allowances_monthly: Sum of all fixed monthly allowances.
        gross_monthly: Monthly gross pay after part-time adjustment.
        gross_annual: Annual gross pay (RAL), possibly overridden by a
            negotiated value.
        apprenticeship_pct: Percentage applied to destination-level salary for
            apprentices (``None`` for non-apprentice contracts).
        apprenticeship_under_level_code: Pay level code used in under-
            classification apprenticeships (``None`` otherwise).
        inps_employee_annual: Annual employee INPS contribution.
        inps_employer_annual: Annual employer INPS contribution (including
            NASpI addizionale for fixed-term).
        tfr_annual: Annual TFR accrual.
        taxable_income: IRPEF taxable income (``gross_annual -
            inps_employee_annual``).
        irpef_gross: Gross IRPEF before deductions.
        work_income_deduction: Art. 13 TUIR deduction.
        irpef_net: IRPEF due after deduction (floored at zero).
        net_annual: Annual take-home pay.
        net_monthly: Monthly take-home pay (``net_annual / additional_months``).
        employer_cost_annual: Total annual cost to the employer.
    """

    # --- echoed inputs ---
    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: date
    year: int

    # --- salary chain ---
    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal

    # --- apprenticeship intermediates ---
    apprenticeship_pct: Decimal | None
    apprenticeship_under_level_code: str | None

    # --- contributions ---
    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    tfr_annual: Decimal

    # --- IRPEF ---
    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal

    # --- net ---
    net_annual: Decimal
    net_monthly: Decimal

    # --- employer ---
    employer_cost_annual: Decimal
