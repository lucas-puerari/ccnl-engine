"""ComputationResult — the output record of compute()."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal


@dataclass(frozen=True)
class ComputationResult:
    """Full gross-to-net and employer-cost breakdown for one payroll computation.

    Monthly components (``base_monthly``, ``seniority_monthly``,
    ``allowances_monthly``, ``ad_personam_monthly``) are already scaled by
    ``part_time_pct`` and sum to ``gross_monthly``.
    """

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: date
    year: int

    seniority_count: int
    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    ad_personam_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    hourly_rate: Decimal

    apprenticeship_pct: Decimal | None
    apprenticeship_under_level_code: str | None

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal

    net_annual: Decimal
    net_monthly: Decimal

    employer_cost_annual: Decimal
