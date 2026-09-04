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

    All ``Decimal`` amounts are in EUR. Annual figures assume the contract-wide
    ``additional_months`` pay structure (typically 13 or 14 months).

    Attributes:
        ccnl_id: Identifier of the CCNL used (from ``CCNLMeta.id``).
        level_code: Classification level code used for the computation.
        employment_type: String tag of the employment type
            (``"permanent"``, ``"fixed_term"``, or ``"apprentice"``).
        part_time_pct: Part-time coefficient applied to gross and
            contribution bases. ``1`` for a full-time worker.
        as_of: Reference date used to resolve all time-series values.
        year: Calendar year derived from ``as_of``; used to select IRPEF
            brackets and contribution rules.

        seniority_count: Number of seniority increments (*scatti di
            anzianità*) applied. ``0`` when no seniority applies.
        base_monthly: Base monthly pay from the CCNL table, scaled by
            ``part_time_pct``.
        seniority_monthly: Monthly seniority increment amount, scaled by
            ``part_time_pct``.
        allowances_monthly: Sum of all applicable fixed monthly allowances,
            scaled by ``part_time_pct``.
        ad_personam_monthly: Individual frozen monthly element (e.g.
            pre-abolition seniority) added directly to gross, **not** scaled
            by ``part_time_pct``.
        gross_monthly: Total monthly gross pay (sum of the four monthly
            components above).
        gross_annual: Annual gross pay, accounting for additional months
            (``gross_monthly * additional_months``).
        hourly_rate: Hourly gross rate derived from the contractual weekly
            hours and the standard number of months per year.

        apprenticeship_pct: Percentage applied to destination-level pay for
            percentage-track apprentices (e.g. ``Decimal("0.80")``). ``None``
            for non-apprentice or under-classification contracts.
        apprenticeship_under_level_code: Destination level code for
            under-classification apprentices. ``None`` otherwise.

        inps_employee_annual: Employee INPS contribution for the year.
        inps_employer_annual: Employer INPS contribution for the year,
            including any NASpI addizionale for fixed-term contracts.
        employer_funds_annual: Employer contribution to contractual funds
            (e.g. Cassa Edile, Fondapi) for the year.
        tfr_annual: TFR (*Trattamento di Fine Rapporto*) accrual for the
            year (Art. 2120 c.c.).

        taxable_income: IRPEF taxable base (``gross_annual``
            minus ``inps_employee_annual``).
        irpef_gross: IRPEF before work-income deduction (Art. 11 TUIR).
        work_income_deduction: Work-income tax deduction (Art. 13 TUIR).
        irpef_net: IRPEF actually withheld (``irpef_gross``
            minus ``work_income_deduction``, floored at zero).
        employer_withholds_irpef: ``False`` when the employer is not a
            *sostituto d'imposta* (e.g. lavoro domestico); in that case
            ``irpef_gross`` and ``work_income_deduction`` are informational
            only and ``irpef_net`` is zero.

        net_annual: Annual net pay (``gross_annual`` minus
            ``inps_employee_annual`` minus ``irpef_net``).
        net_monthly: Monthly net pay (``net_annual / additional_months``).

        employer_cost_annual: Total annual employer cost
            (``gross_annual`` + ``inps_employer_annual``
            + ``employer_funds_annual`` + ``tfr_annual``).
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
    employer_withholds_irpef: bool

    net_annual: Decimal
    net_monthly: Decimal

    employer_cost_annual: Decimal
