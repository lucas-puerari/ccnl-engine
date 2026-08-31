"""ComputationResult — the output record of compute()."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal


@dataclass(frozen=True)
class ComputationResult:
    """Full gross-to-net and employer-cost breakdown for one payroll computation."""

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: date
    year: int

    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal

    apprenticeship_pct: Decimal | None
    apprenticeship_under_level_code: str | None

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    tfr_annual: Decimal

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal

    net_annual: Decimal
    net_monthly: Decimal

    employer_cost_annual: Decimal
